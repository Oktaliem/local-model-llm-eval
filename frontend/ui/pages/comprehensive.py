"""Comprehensive Evaluation UI page"""
import streamlit as st
import threading
import time
import json
from queue import Queue
from core.services.evaluation_service import EvaluationService
from typing import Optional

# Thread-safe queue for passing results from background threads to main thread
_comp_eval_result_queue = Queue()

def render_comprehensive_page(evaluation_service: EvaluationService, model: str):
    """Render the Comprehensive Evaluation page"""
    # Import helper functions from backend services
    from backend.services.template_service import (
        get_all_evaluation_templates,
        get_evaluation_template
    )
    from backend.services.data_service import save_judgment
    # TODO: evaluate_comprehensive is a complex wrapper - refactor to use EvaluationService directly
    from backend.services.evaluation_functions import evaluate_comprehensive  # type: ignore
    
    st.header("🎯 Comprehensive Evaluation")
    st.markdown("Evaluate AI responses with comprehensive metrics: accuracy, relevance, coherence, hallucination detection, and toxicity checking.")
    
    # Template selection
    comprehensive_templates = get_all_evaluation_templates(evaluation_type="comprehensive", include_predefined=True)
    template_options = ["None (Use Default)"] + [f"{t['template_name']} ({t.get('industry', 'general')})" for t in comprehensive_templates]
    template_id_map = {f"{t['template_name']} ({t.get('industry', 'general')})": t['template_id'] for t in comprehensive_templates}
    
    selected_template_name = st.selectbox(
        "📋 Evaluation Template (Optional)",
        template_options,
        help="Select a template to apply custom evaluation configuration",
        key="comp_template_select"
    )
    
    selected_template_id = None
    if selected_template_name != "None (Use Default)":
        selected_template_id = template_id_map.get(selected_template_name)
        if selected_template_id:
            template = get_evaluation_template(selected_template_id)
            if template:
                st.info(f"📋 Using template: {template['template_name']}")
                if template.get('template_description'):
                    st.caption(template['template_description'])
    
    col_task, col_ref = st.columns(2)
    with col_task:
        # If template selected, use template's task_type, otherwise allow selection
        if selected_template_id:
            template = get_evaluation_template(selected_template_id)
            if template and template['template_config'].get('task_type'):
                task_type = template['template_config']['task_type']
                st.selectbox(
                    "Task Type",
                    [task_type],
                    help=f"Task type from template: {task_type}",
                    key="comp_task_type_template",
                    disabled=True
                )
            else:
                task_type = st.selectbox(
                    "Task Type",
                    ["general", "qa", "summarization", "code", "translation", "creative"],
                    help="Select the type of task for context-aware evaluation",
                    key="comp_task_type"
                )
        else:
            task_type = st.selectbox(
                "Task Type",
                ["general", "qa", "summarization", "code", "translation", "creative"],
                help="Select the type of task for context-aware evaluation",
                key="comp_task_type"
            )
    with col_ref:
        use_reference = st.checkbox("Use Reference Answer", help="Provide a reference answer for more accurate evaluation")
    
    # Additional properties toggle
    include_additional = st.checkbox(
        "✨ Include Additional Properties (Politeness, Bias, Tone, Sentiment)",
        value=True,
        help="Evaluate additional properties for comprehensive assessment",
        key="comp_include_additional"
    )
    
    question = st.text_area(
        "Question/Task:",
        height=100,
        placeholder="What is machine learning?",
        key="comp_question"
    )
    
    response = st.text_area(
        "Response to Evaluate:",
        height=200,
        placeholder="Machine learning is a subset of artificial intelligence...",
        key="comp_response"
    )
    
    reference = None
    if use_reference:
        reference = st.text_area(
            "Reference Answer (optional):",
            height=150,
            placeholder="Reference answer for comparison...",
            key="comp_reference"
        )
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        evaluate_comp_btn = st.button("🎯 Run Comprehensive Evaluation", type="primary", use_container_width=True)
    with col_btn2:
        save_comp_enabled = st.checkbox("💾 Save to DB", value=True, key="save_comp")
    
    # Initialize session state
    if 'comp_eval_running' not in st.session_state:
        st.session_state.comp_eval_running = False
    if 'comp_eval_result' not in st.session_state:
        st.session_state.comp_eval_result = None
    
    # Check for results from background thread (thread-safe module-level queue)
    try:
        while not _comp_eval_result_queue.empty():
            result = _comp_eval_result_queue.get_nowait()
            st.session_state.comp_eval_result = result
            st.session_state.comp_eval_running = False
    except:
        pass
    
    if evaluate_comp_btn:
        if not question or not response:
            st.warning("Please fill in the question and response fields.")
        else:
            # Store judge_model in session state so it's available after rerun
            st.session_state.comp_judge_model = model
            st.session_state.comp_eval_running = True
            st.session_state.comp_eval_result = None
            
            def run_comp_eval():
                # Get judge_model from session state (set above)
                judge_model = st.session_state.get('comp_judge_model', model)
                """Run comprehensive evaluation in background thread (thread-safe)"""
                try:
                    # Apply template if selected
                    final_task_type = task_type
                    if selected_template_id:
                        template = get_evaluation_template(selected_template_id)
                        if template and template['template_config'].get('task_type'):
                            final_task_type = template['template_config']['task_type']
                    
                    result = evaluate_comprehensive(
                        question, response, reference, judge_model, final_task_type,
                        include_additional_properties=include_additional
                    )
                    # Store result in thread-safe module-level queue (don't access session_state from thread)
                    _comp_eval_result_queue.put(result)
                except Exception as e:
                    # Store error result in thread-safe module-level queue
                    _comp_eval_result_queue.put({"success": False, "error": str(e)})
            
            thread = threading.Thread(target=run_comp_eval, daemon=True)
            thread.start()
            st.rerun()
    
    if st.session_state.comp_eval_running:
        with st.status("🎯 Running comprehensive evaluation...", expanded=True) as status:
            st.write("Evaluating accuracy...")
            st.write("Evaluating relevance...")
            st.write("Evaluating coherence...")
            st.write("Checking for hallucinations...")
            st.write("Checking for toxicity...")
            if include_additional:
                st.write("Evaluating politeness...")
                st.write("Detecting bias...")
                st.write("Analyzing tone...")
                st.write("Analyzing sentiment...")
            st.info("💡 This may take a few moments. The page will auto-refresh.")
        
        time.sleep(3)
        if st.session_state.comp_eval_running:
            st.rerun()
    
    elif st.session_state.comp_eval_result is not None:
        result = st.session_state.comp_eval_result
        
        if result.get("success"):
            st.success("✅ Comprehensive Evaluation Complete!")
            
            metrics = result.get("metrics", {})
            trace = result.get("trace", {})
            
            # Display metrics in columns
            st.markdown("### 📊 Evaluation Metrics")
            
            # Core metrics (always shown)
            st.markdown("#### Core Metrics")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                accuracy = metrics.get("accuracy", {}).get("score", 0)
                st.metric("Accuracy", f"{accuracy:.1f}/10", delta=f"{accuracy-5:.1f}")
            
            with col2:
                relevance = metrics.get("relevance", {}).get("score", 0)
                st.metric("Relevance", f"{relevance:.1f}/10", delta=f"{relevance-5:.1f}")
            
            with col3:
                coherence = metrics.get("coherence", {}).get("score", 0)
                st.metric("Coherence", f"{coherence:.1f}/10", delta=f"{coherence-5:.1f}")
            
            with col4:
                hallucination = metrics.get("hallucination", {}).get("score", 0)
                st.metric("Hallucination", f"{hallucination:.1f}/10", delta=f"{hallucination-5:.1f}")
            
            with col5:
                toxicity = metrics.get("toxicity", {}).get("score", 0)
                st.metric("Toxicity", f"{toxicity:.1f}/10", delta=f"{toxicity-5:.1f}")
            
            # Additional properties (if included)
            if metrics.get("politeness") or metrics.get("bias") or metrics.get("tone") or metrics.get("sentiment"):
                st.markdown("#### Additional Properties")
                col6, col7, col8, col9 = st.columns(4)
                
                with col6:
                    politeness = metrics.get("politeness", {}).get("score", 0)
                    if politeness > 0:
                        st.metric("Politeness", f"{politeness:.1f}/10", delta=f"{politeness-5:.1f}")
                
                with col7:
                    bias = metrics.get("bias", {}).get("score", 0)
                    if bias > 0:
                        st.metric("Bias (Fairness)", f"{bias:.1f}/10", delta=f"{bias-5:.1f}")
                
                with col8:
                    tone = metrics.get("tone", {}).get("score", 0)
                    if tone > 0:
                        st.metric("Tone", f"{tone:.1f}/10", delta=f"{tone-5:.1f}")
                
                with col9:
                    sentiment = metrics.get("sentiment", {}).get("score", 0)
                    if sentiment > 0:
                        st.metric("Sentiment", f"{sentiment:.1f}/10", delta=f"{sentiment-5:.1f}")
            
            overall = metrics.get("overall_score", 0)
            execution_time = result.get("execution_time", 0)
            
            col_score, col_time = st.columns([2, 1])
            with col_score:
                st.markdown(f"### 🎯 Overall Score: **{overall:.2f}/10**")
            with col_time:
                st.markdown(f"### ⏱️ Execution Time: **{execution_time:.2f}s**")
            
            # Detailed metrics
            with st.expander("📋 Detailed Metrics", expanded=True):
                for metric_name, metric_data in metrics.items():
                    if metric_name != "overall_score" and isinstance(metric_data, dict):
                        st.markdown(f"#### {metric_name.capitalize()}")
                        if "score" in metric_data:
                            st.write(f"**Score:** {metric_data['score']:.2f}/10")
                        if "risk_score" in metric_data:
                            st.write(f"**Risk Score:** {metric_data['risk_score']:.2f}/10")
                        if "explanation" in metric_data:
                            st.write(f"**Explanation:** {metric_data['explanation']}")
                        st.markdown("---")
            
            # Trace information
            with st.expander("🔍 Evaluation Trace", expanded=False):
                st.json(trace)
            
            # Save to database
            if save_comp_enabled:
                try:
                    if save_judgment:
                        # Get judge_model from session state (stored when evaluation started)
                        judge_model = st.session_state.get('comp_judge_model', model)
                        judgment_text = f"Comprehensive Evaluation - Overall Score: {overall:.2f}/10"
                        judgment_id = save_judgment(
                            question=question,
                            response_a=response,
                            response_b="",
                            model_a="Manual Entry",
                            model_b="",
                            judge_model=judge_model,
                            judgment=judgment_text,
                            judgment_type="comprehensive",
                            evaluation_id=result.get("evaluation_id"),
                            metrics_json=json.dumps(metrics),
                            trace_json=json.dumps(trace)
                        )
                        st.success(f"💾 Saved to database (ID: {judgment_id})")
                    else:
                        st.warning("⚠️ Could not import save_judgment function")
                except Exception as e:
                    st.warning(f"⚠️ Could not save to database: {str(e)}")
            
            if st.button("🔄 New Evaluation", key="new_comp_eval"):
                st.session_state.comp_eval_result = None
                st.session_state.comp_eval_running = False
                st.rerun()
        else:
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            if st.button("🔄 Retry", key="retry_comp_eval"):
                st.session_state.comp_eval_result = None
                st.session_state.comp_eval_running = False
                st.rerun()

