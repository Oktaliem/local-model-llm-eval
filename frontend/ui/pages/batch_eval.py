"""Batch Evaluation UI page"""
import streamlit as st
import json
import threading
import time
import uuid
import io
from datetime import datetime
from queue import Queue
import pandas as pd
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_batch_eval_page(evaluation_service: EvaluationService):
    """Render the Batch Evaluation page"""
    # Import helper functions from backend services
    from backend.services.data_service import (
        save_evaluation_run,
        update_evaluation_run,
        get_evaluation_run
    )
    # TODO: process_batch_evaluation is complex and still uses app.py functions
    # Will be refactored to use EvaluationService in a later phase
    from backend.services.evaluation_functions import process_batch_evaluation  # type: ignore
    
    # Get available models from session state or sidebar
    available_models = st.session_state.get('available_models', ['llama3', 'mistral', 'gpt-oss-safeguard:20b'])
    model = st.selectbox("Judge Model", available_models, index=0 if available_models else None, key="batch_judge_model")
    
    st.header("📦 Batch Evaluation")
    st.markdown("Upload a dataset (JSON/CSV) and evaluate multiple test cases at once.")
    
    st.info("💡 **Supported formats:**\n- JSON: Array of objects with 'question' and optionally 'response' and 'reference' fields\n- CSV: Columns: question, response, reference")
    
    # Initialize session state for batch evaluation
    if 'batch_df' not in st.session_state:
        st.session_state.batch_df = None
    if 'batch_running' not in st.session_state:
        st.session_state.batch_running = False
    if 'batch_result' not in st.session_state:
        st.session_state.batch_result = None
    if 'batch_run_id' not in st.session_state:
        st.session_state.batch_run_id = None
    if 'batch_queue' not in st.session_state:
        st.session_state.batch_queue = Queue()
    
    uploaded_file = st.file_uploader(
        "Upload Dataset",
        type=['json', 'csv'],
        help="Upload a JSON or CSV file with test cases",
        key="batch_upload"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.json'):
                data = json.load(uploaded_file)
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    st.error("JSON file must contain an array of objects")
                    st.stop()
            else:  # CSV
                df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_cols = ['question', 'response']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                st.stop()
            
            st.session_state.batch_df = df
            st.success(f"✅ Loaded {len(df)} test cases")
            
            # Show preview
            with st.expander("📋 Preview Dataset", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
                st.caption(f"Total rows: {len(df)}")
            
            # Configuration
            st.markdown("### ⚙️ Evaluation Configuration")
            col_eval, col_task, col_save = st.columns(3)
            
            with col_eval:
                eval_type = st.selectbox(
                    "Evaluation Type",
                    ["comprehensive", "single"],
                    help="Choose comprehensive (5 metrics) or single (basic grading)",
                    key="batch_eval_type"
                )
            
            with col_task:
                task_type = st.selectbox(
                    "Task Type",
                    ["general", "qa", "summarization", "code", "translation", "creative"],
                    help="Select task type for context-aware evaluation",
                    key="batch_task_type",
                    disabled=(eval_type != "comprehensive")
                )
            
            with col_save:
                save_batch_enabled = st.checkbox("💾 Save to DB", value=True, key="save_batch")
            
            # Run name
            run_name = st.text_input(
                "Run Name (optional):",
                value=f"Batch Run {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                key="batch_run_name"
            )
            
            col_start, col_stop = st.columns([3, 1])
            
            with col_start:
                start_batch_btn = st.button("🚀 Start Batch Evaluation", type="primary", use_container_width=True, disabled=st.session_state.batch_running)
            
            with col_stop:
                if st.session_state.batch_running:
                    if st.button("⏹️ Stop", type="secondary", use_container_width=True, key="stop_batch"):
                        st.session_state.batch_running = False
                        st.rerun()
            
            if start_batch_btn and not st.session_state.batch_running:
                if st.session_state.batch_df is None or len(st.session_state.batch_df) == 0:
                    st.warning("Please upload a dataset first.")
                else:
                    st.session_state.batch_running = True
                    st.session_state.batch_result = None
                    st.session_state.batch_run_id = str(uuid.uuid4())
                    
                    # Convert dataframe to list of dicts
                    test_cases = st.session_state.batch_df.to_dict('records')
                    
                    # Save run to database
                    save_evaluation_run(
                        run_id=st.session_state.batch_run_id,
                        run_name=run_name,
                        dataset_name=uploaded_file.name,
                        total_cases=len(test_cases),
                        status="running"
                    )
                    
                    # Capture values before thread starts (thread-safe)
                    run_id_val = st.session_state.batch_run_id
                    result_queue = st.session_state.batch_queue
                    
                    def run_batch_eval():
                        import sys
                        import traceback
                        try:
                            print(f"[DEBUG] Batch eval thread started: run_id={run_id_val}, cases={len(test_cases)}", flush=True)
                            sys.stdout.flush()
                            
                            result = process_batch_evaluation(
                                test_cases=test_cases,
                                evaluation_type=eval_type,
                                judge_model=model,
                                task_type=task_type if eval_type == "comprehensive" else "general",
                                save_to_db=save_batch_enabled,
                                run_id=run_id_val
                            )
                            
                            print(f"[DEBUG] Batch eval process completed: status={result.get('status')}, completed={result.get('completed')}", flush=True)
                            sys.stdout.flush()
                            
                            # Update run status (redundant but ensures it's updated)
                            try:
                                update_evaluation_run(
                                    run_id=run_id_val,
                                    completed_cases=result["completed"],
                                    status=result["status"],
                                    results_json=json.dumps(result)
                                )
                                print(f"[DEBUG] Database updated with final status", flush=True)
                                sys.stdout.flush()
                            except Exception as db_e:
                                print(f"[DEBUG] Error updating database: {str(db_e)}", flush=True)
                                sys.stdout.flush()
                            
                            # Put result in queue (thread-safe)
                            result_queue.put(result)
                            print(f"[DEBUG] Batch eval result put in queue successfully", flush=True)
                            sys.stdout.flush()
                        except Exception as e:
                            error_trace = traceback.format_exc()
                            print(f"[DEBUG] Exception in batch eval thread: {str(e)}", flush=True)
                            print(f"[DEBUG] Traceback: {error_trace}", flush=True)
                            sys.stdout.flush()
                            # Put error result in queue (thread-safe)
                            error_result = {
                                "success": False,
                                "error": str(e),
                                "run_id": run_id_val
                            }
                            result_queue.put(error_result)
                            try:
                                update_evaluation_run(
                                    run_id=run_id_val,
                                    completed_cases=0,
                                    status="failed",
                                    results_json=json.dumps({"error": str(e), "traceback": error_trace})
                                )
                            except:
                                pass
                    
                    thread = threading.Thread(target=run_batch_eval, daemon=True)
                    thread.start()
                    st.rerun()
            
            # Check for results from background thread (thread-safe queue)
            try:
                while not st.session_state.batch_queue.empty():
                    result = st.session_state.batch_queue.get_nowait()
                    st.session_state.batch_result = result
                    st.session_state.batch_running = False
                    print(f"[DEBUG] Main thread: Received batch result from queue", flush=True)
            except Exception as e:
                pass
            
            # Show progress if running
            if st.session_state.batch_running:
                st.markdown("### 📊 Batch Evaluation Progress")
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                # Try to get current progress from database
                if st.session_state.batch_run_id:
                    run_info = get_evaluation_run(st.session_state.batch_run_id)
                    if run_info:
                        completed = run_info.get("completed_cases", 0)
                        total = run_info.get("total_cases", len(st.session_state.batch_df) if st.session_state.batch_df is not None else 0)
                        progress = completed / total if total > 0 else 0
                        
                        progress_placeholder.progress(progress)
                        status_placeholder.info(f"⏳ Processing... {completed}/{total} cases completed ({progress*100:.1f}%)")
                        
                        if completed < total:
                            time.sleep(2)
                            st.rerun()
                    else:
                        status_placeholder.info("⏳ Starting batch evaluation...")
                        time.sleep(2)
                        st.rerun()
                else:
                    status_placeholder.info("⏳ Initializing batch evaluation...")
                    time.sleep(1)
                    st.rerun()
            
            # Show results when complete
            elif st.session_state.batch_result is not None:
                result = st.session_state.batch_result
                
                if result.get("error"):
                    st.error(f"❌ Batch Evaluation Failed: {result['error']}")
                else:
                    st.success(f"✅ Batch Evaluation Complete!")
                    
                    # Summary metrics
                    st.markdown("### 📊 Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Cases", result.get("total_cases", 0))
                    with col2:
                        st.metric("Successful", result.get("successful", 0), delta=f"{result.get('successful', 0) - result.get('failed', 0)}")
                    with col3:
                        st.metric("Failed", result.get("failed", 0), delta=f"-{result.get('failed', 0)}", delta_color="inverse")
                    with col4:
                        success_rate = (result.get("successful", 0) / result.get("total_cases", 1)) * 100
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    
                    # Aggregate metrics for comprehensive evaluation
                    if eval_type == "comprehensive" and result.get("aggregate_metrics"):
                        st.markdown("### 📈 Aggregate Metrics")
                        agg = result["aggregate_metrics"]
                        
                        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                        
                        with col_m1:
                            st.metric("Avg Overall", f"{agg.get('avg_overall_score', 0):.2f}/10")
                        with col_m2:
                            st.metric("Avg Accuracy", f"{agg.get('avg_accuracy', 0):.2f}/10")
                        with col_m3:
                            st.metric("Avg Relevance", f"{agg.get('avg_relevance', 0):.2f}/10")
                        with col_m4:
                            st.metric("Avg Coherence", f"{agg.get('avg_coherence', 0):.2f}/10")
                        with col_m5:
                            st.metric("Avg Hallucination", f"{agg.get('avg_hallucination', 0):.2f}/10")
                        
                        st.metric("Avg Toxicity", f"{agg.get('avg_toxicity', 0):.2f}/10")
                    
                    # Results table
                    st.markdown("### 📋 Detailed Results")
                    
                    # Create results dataframe
                    results_data = []
                    for case_result in result.get("case_results", []):
                        row = {
                            "Index": case_result.get("index"),
                            "Question": case_result.get("question", "")[:50] + "..." if len(case_result.get("question", "")) > 50 else case_result.get("question", ""),
                            "Status": "✅ Success" if case_result.get("success") else "❌ Failed",
                            "Error": case_result.get("error", "")
                        }
                        
                        if case_result.get("success") and case_result.get("evaluation"):
                            if eval_type == "comprehensive":
                                row["Overall Score"] = f"{case_result['evaluation'].get('overall_score', 0):.2f}/10"
                            else:
                                row["Evaluation"] = "Completed"
                        
                        results_data.append(row)
                    
                    results_df = pd.DataFrame(results_data)
                    st.dataframe(results_df, use_container_width=True, height=400)
                    
                    # Failed cases
                    failed_cases = [r for r in result.get("case_results", []) if not r.get("success")]
                    if failed_cases:
                        with st.expander("❌ Failed Cases", expanded=False):
                            for case in failed_cases:
                                st.error(f"Case #{case.get('index')}: {case.get('error', 'Unknown error')}")
                    
                    # Export options
                    st.markdown("### 💾 Export Results")
                    col_exp1, col_exp2 = st.columns(2)
                    
                    with col_exp1:
                        # Export as JSON
                        json_str = json.dumps(result, indent=2, default=str)
                        st.download_button(
                            label="📥 Download Results (JSON)",
                            data=json_str,
                            file_name=f"batch_evaluation_{st.session_state.batch_run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    with col_exp2:
                        # Export results table as CSV
                        if len(results_data) > 0:
                            csv_str = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results (CSV)",
                                data=csv_str,
                                file_name=f"batch_evaluation_{st.session_state.batch_run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    
                    # Clear button
                    if st.button("🔄 New Batch Evaluation", key="new_batch"):
                        st.session_state.batch_result = None
                        st.session_state.batch_df = None
                        st.session_state.batch_run_id = None
                        st.rerun()
        
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.exception(e)

