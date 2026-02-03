"""Saved Judgments & Dashboard UI page"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_saved_judgments_page(evaluation_service: EvaluationService):
    """Render the Saved Judgments & Dashboard page"""
    # Import helper functions from backend services
    from backend.services.data_service import (
        get_all_judgments,
        delete_judgment,
        get_human_annotations,
        get_router_evaluations,
        get_skills_evaluations,
        get_trajectory_evaluations
    )
    
    st.header("💾 Saved Judgments & Dashboard")
    st.markdown("View and manage your saved judgments from the database.")
    
    # Get all judgments
    judgments = get_all_judgments()
    
    if not judgments:
        st.info("No judgments saved yet. Start evaluating responses to see them here!")
    else:
        st.success(f"Found {len(judgments)} saved judgment(s)")
        
        # Dashboard metrics (include both comprehensive and batch_comprehensive)
        comprehensive_judgments = [j for j in judgments if j.get("judgment_type") in ["comprehensive", "batch_comprehensive"] and j.get("metrics_json")]
        if comprehensive_judgments:
            st.markdown("### 📊 Metrics Dashboard")
            metrics_data = []
            for j in comprehensive_judgments:
                try:
                    metrics = json.loads(j.get("metrics_json", "{}"))
                    if metrics:
                        metrics_data.append({
                            "id": j["id"],
                            "overall": metrics.get("overall_score", 0),
                            "accuracy": metrics.get("accuracy", {}).get("score", 0),
                            "relevance": metrics.get("relevance", {}).get("score", 0),
                            "coherence": metrics.get("coherence", {}).get("score", 0),
                            "hallucination": metrics.get("hallucination", {}).get("score", 0),
                            "toxicity": metrics.get("toxicity", {}).get("score", 0),
                            "created_at": j.get("created_at", "")
                        })
                except:
                    pass
            
            if metrics_data:
                metrics_df = pd.DataFrame(metrics_data)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Evaluations", len(metrics_data))
                with col2:
                    avg_overall = metrics_df["overall"].mean()
                    st.metric("Avg Overall Score", f"{avg_overall:.2f}/10")
                with col3:
                    avg_accuracy = metrics_df["accuracy"].mean()
                    st.metric("Avg Accuracy", f"{avg_accuracy:.2f}/10")
                with col4:
                    avg_hallucination = metrics_df["hallucination"].mean()
                    st.metric("Avg Hallucination Score", f"{avg_hallucination:.2f}/10")
                
                st.markdown("---")
        
        # Filter options
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "pairwise_manual", "pairwise_auto", "single", "comprehensive", "code_evaluation", "batch_comprehensive", "batch_single", "skills_evaluation"],
                key="saved_filter_type"
            )
        with col_filter2:
            limit = st.slider("Show last N judgments", 10, 100, 50, key="saved_limit_slider")
        
        # Filter judgments
        filtered_judgments = judgments[:limit]
        if filter_type != "All":
            filtered_judgments = [j for j in filtered_judgments if j.get("judgment_type") == filter_type]
        
        # Display judgments
        for idx, judgment in enumerate(filtered_judgments):
            with st.expander(f"📋 Judgment #{judgment['id']} - {judgment['judgment_type']} - {judgment['created_at']}", expanded=False):
                col_info, col_action = st.columns([4, 1])
                
                with col_info:
                    st.markdown(f"**Question:** {judgment['question']}")
                    st.markdown(f"**Judge Model:** {judgment['judge_model']}")
                    st.markdown(f"**Created:** {judgment['created_at']}")
                    
                    if judgment['judgment_type'] in ['pairwise_manual', 'pairwise_auto']:
                        st.markdown("---")
                        col_resp1, col_resp2 = st.columns(2)
                        with col_resp1:
                            st.markdown(f"**Response A** (from {judgment['model_a']}):")
                            st.text_area("Response A", judgment['response_a'], height=100, key=f"resp_a_{judgment['id']}", disabled=True, label_visibility="collapsed")
                        with col_resp2:
                            st.markdown(f"**Response B** (from {judgment['model_b']}):")
                            st.text_area("Response B", judgment['response_b'], height=100, key=f"resp_b_{judgment['id']}", disabled=True, label_visibility="collapsed")
                    elif judgment['judgment_type'] == 'single':
                        st.markdown("---")
                        st.markdown("**Response:**")
                        st.text_area("Response", judgment['response_a'], height=100, key=f"resp_single_{judgment['id']}", disabled=True, label_visibility="collapsed")
                    elif judgment['judgment_type'] == 'comprehensive':
                        st.markdown("---")
                        st.markdown("**Response:**")
                        st.text_area("Response", judgment['response_a'], height=100, key=f"resp_comp_{judgment['id']}", disabled=True, label_visibility="collapsed")
                        
                        # Show metrics if available
                        if judgment.get('metrics_json'):
                            try:
                                metrics = json.loads(judgment['metrics_json'])
                                st.markdown("**Metrics:**")
                                col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                                with col_m1:
                                    st.metric("Accuracy", f"{metrics.get('accuracy', {}).get('score', 0):.1f}")
                                with col_m2:
                                    st.metric("Relevance", f"{metrics.get('relevance', {}).get('score', 0):.1f}")
                                with col_m3:
                                    st.metric("Coherence", f"{metrics.get('coherence', {}).get('score', 0):.1f}")
                                with col_m4:
                                    st.metric("Hallucination", f"{metrics.get('hallucination', {}).get('score', 0):.1f}")
                                with col_m5:
                                    st.metric("Toxicity", f"{metrics.get('toxicity', {}).get('score', 0):.1f}")
                                st.metric("Overall Score", f"{metrics.get('overall_score', 0):.2f}/10")
                                
                                with st.expander("View Detailed Metrics"):
                                    st.json(metrics)
                            except:
                                pass
                        
                        # Show trace if available
                        if judgment.get('trace_json'):
                            with st.expander("View Evaluation Trace"):
                                try:
                                    trace = json.loads(judgment['trace_json'])
                                    st.json(trace)
                                except:
                                    pass
                    elif judgment['judgment_type'] == 'code_evaluation':
                        st.markdown("---")
                        st.markdown("**Code:**")
                        st.code(judgment['response_a'], language="python")
                        
                        # Show code evaluation results if available
                        if judgment.get('metrics_json'):
                            try:
                                results = json.loads(judgment['metrics_json'])
                                st.markdown("**Code Evaluation Results:**")
                                
                                # Syntax
                                syntax = results.get('syntax', {})
                                if syntax.get('valid'):
                                    st.success(f"✅ Valid syntax | Complexity: {syntax.get('complexity', 0)}")
                                else:
                                    st.error("❌ Syntax errors found")
                                
                                # Execution
                                execution = results.get('execution', {})
                                if execution.get('success'):
                                    st.success(f"✅ Execution successful ({execution.get('execution_time', 0):.3f}s)")
                                elif execution.get('skipped'):
                                    st.info("⏭️ Execution skipped")
                                else:
                                    st.error("❌ Execution failed")
                                
                                # Quality
                                quality = results.get('quality', {})
                                col_q1, col_q2, col_q3 = st.columns(3)
                                with col_q1:
                                    st.metric("Maintainability", f"{quality.get('maintainability', 0):.1f}/10")
                                with col_q2:
                                    st.metric("Readability", f"{quality.get('readability', 0):.1f}/10")
                                with col_q3:
                                    st.metric("Overall Score", f"{results.get('overall_score', 0):.2f}/10")
                                
                                with st.expander("View Detailed Results"):
                                    st.json(results)
                            except:
                                pass
                        
                        # Show trace if available
                        if judgment.get('trace_json'):
                            with st.expander("View Evaluation Trace"):
                                try:
                                    trace = json.loads(judgment['trace_json'])
                                    st.json(trace)
                                except:
                                    pass
                    elif judgment['judgment_type'] in ['batch_comprehensive', 'batch_single']:
                        st.markdown("---")
                        st.markdown("**Response:**")
                        st.text_area("Response", judgment['response_a'], height=100, key=f"resp_batch_{judgment['id']}", disabled=True, label_visibility="collapsed")
                        
                        # Show batch evaluation results
                        if judgment.get('metrics_json'):
                            try:
                                if judgment['judgment_type'] == 'batch_comprehensive':
                                    metrics = json.loads(judgment['metrics_json'])
                                    st.markdown("**Batch Comprehensive Evaluation Metrics:**")
                                    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                                    with col_m1:
                                        st.metric("Accuracy", f"{metrics.get('accuracy', {}).get('score', 0):.1f}")
                                    with col_m2:
                                        st.metric("Relevance", f"{metrics.get('relevance', {}).get('score', 0):.1f}")
                                    with col_m3:
                                        st.metric("Coherence", f"{metrics.get('coherence', {}).get('score', 0):.1f}")
                                    with col_m4:
                                        st.metric("Hallucination", f"{metrics.get('hallucination', {}).get('score', 0):.1f}")
                                    with col_m5:
                                        st.metric("Toxicity", f"{metrics.get('toxicity', {}).get('score', 0):.1f}")
                                    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.2f}/10")
                                    
                                    with st.expander("View Detailed Metrics"):
                                        st.json(metrics)
                                else:
                                    st.info("Batch single evaluation - see judgment text for details")
                            except:
                                pass
                    elif judgment['judgment_type'] == 'skills_evaluation':
                        st.markdown("---")
                        st.markdown("**Response:**")
                        st.text_area("Response", judgment['response_a'], height=100, key=f"resp_skills_{judgment['id']}", disabled=True, label_visibility="collapsed")
                        
                        # Show skills evaluation metrics if available
                        if judgment.get('metrics_json'):
                            try:
                                metrics = json.loads(judgment['metrics_json'])
                                st.markdown("**Skills Evaluation Metrics:**")
                                col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
                                with col_s1:
                                    st.metric("Correctness", f"{metrics.get('correctness_score', 0):.2f}/10")
                                with col_s2:
                                    st.metric("Completeness", f"{metrics.get('completeness_score', 0):.2f}/10")
                                with col_s3:
                                    st.metric("Clarity", f"{metrics.get('clarity_score', 0):.2f}/10")
                                with col_s4:
                                    st.metric("Proficiency", f"{metrics.get('proficiency_score', 0):.2f}/10")
                                with col_s5:
                                    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.2f}/10")
                                
                                with st.expander("View Detailed Metrics"):
                                    st.json(metrics)
                            except:
                                pass
                        
                        # Show trace if available
                        if judgment.get('trace_json'):
                            with st.expander("View Evaluation Trace"):
                                try:
                                    trace = json.loads(judgment['trace_json'])
                                    st.json(trace)
                                except:
                                    pass
                    
                    st.markdown("---")
                    st.markdown("**Judgment:**")
                    st.markdown(judgment['judgment'])
                    
                    # Show human annotations for this judgment
                    human_annotations = get_human_annotations(judgment_id=judgment['id'], limit=10)
                    if human_annotations:
                        st.markdown("---")
                        st.markdown("### 👤 Human Annotations")
                        for ann in human_annotations:
                            with st.expander(f"Annotation by {ann.get('annotator_name', 'Unknown')} ({ann.get('created_at', '')})"):
                                st.write(f"**Overall Score:** {ann.get('overall_score', 'N/A')}/10")
                                if ann.get('accuracy_score') is not None:
                                    col_a1, col_a2, col_a3 = st.columns(3)
                                    with col_a1:
                                        st.metric("Accuracy", f"{ann.get('accuracy_score')}/10")
                                    with col_a2:
                                        st.metric("Relevance", f"{ann.get('relevance_score')}/10")
                                    with col_a3:
                                        st.metric("Coherence", f"{ann.get('coherence_score')}/10")
                                if ann.get('feedback_text'):
                                    st.write(f"**Feedback:** {ann.get('feedback_text')}")
                    else:
                        st.markdown("---")
                        st.caption("👤 No human annotations yet. Add one in the Human Evaluation tab.")
                
                with col_action:
                    if st.button("🗑️ Delete", key=f"delete_{judgment['id']}", use_container_width=True):
                        delete_judgment(judgment['id'])
                        st.success("Deleted!")
                        st.rerun()
        
        # Download option
        if st.button("📥 Export All as JSON", use_container_width=True, key="export_judgments"):
            json_str = json.dumps(judgments, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"judgments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_judgments_json"
            )
    
    # Display Router Evaluations
    st.markdown("---")
    st.markdown("### 🔀 Router Evaluations")
    router_evals = get_router_evaluations(limit=50)
    if router_evals:
        st.info(f"Found {len(router_evals)} router evaluation(s)")
        for eval_item in router_evals[:10]:  # Show first 10
            with st.expander(f"Router Evaluation: {eval_item.get('evaluation_id', 'N/A')[:8]}... - {eval_item.get('created_at', '')}"):
                st.write(f"**Query:** {eval_item.get('query', 'N/A')}")
                st.write(f"**Selected Tool:** {eval_item.get('selected_tool', 'N/A')}")
                if eval_item.get('expected_tool'):
                    st.write(f"**Expected Tool:** {eval_item.get('expected_tool', 'N/A')}")
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                with col_r1:
                    st.metric("Tool Accuracy", f"{eval_item.get('tool_accuracy_score', 0):.2f}/10")
                with col_r2:
                    st.metric("Routing Quality", f"{eval_item.get('routing_quality_score', 0):.2f}/10")
                with col_r3:
                    st.metric("Reasoning", f"{eval_item.get('reasoning_score', 0):.2f}/10")
                with col_r4:
                    st.metric("Overall", f"{eval_item.get('overall_score', 0):.2f}/10")
                st.markdown(f"**Judgment:** {eval_item.get('judgment_text', 'N/A')}")
    else:
        st.caption("No router evaluations found.")
    
    # Display Skills Evaluations
    st.markdown("---")
    st.markdown("### 🎓 Skills Evaluations")
    skills_evals = get_skills_evaluations(limit=50)
    if skills_evals:
        st.info(f"Found {len(skills_evals)} skills evaluation(s)")
        for eval_item in skills_evals[:10]:  # Show first 10
            with st.expander(f"Skills Evaluation: {eval_item.get('skill_type', 'N/A')} - {eval_item.get('evaluation_id', 'N/A')[:8]}... - {eval_item.get('created_at', '')}"):
                st.write(f"**Skill Type:** {eval_item.get('skill_type', 'N/A')}")
                if eval_item.get('domain'):
                    st.write(f"**Domain:** {eval_item.get('domain', 'N/A')}")
                st.write(f"**Question:** {eval_item.get('question', 'N/A')[:200]}...")
                col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
                with col_s1:
                    st.metric("Correctness", f"{eval_item.get('correctness_score', 0):.2f}/10")
                with col_s2:
                    st.metric("Completeness", f"{eval_item.get('completeness_score', 0):.2f}/10")
                with col_s3:
                    st.metric("Clarity", f"{eval_item.get('clarity_score', 0):.2f}/10")
                with col_s4:
                    st.metric("Proficiency", f"{eval_item.get('proficiency_score', 0):.2f}/10")
                with col_s5:
                    st.metric("Overall", f"{eval_item.get('overall_score', 0):.2f}/10")
                st.markdown(f"**Judgment:** {eval_item.get('judgment_text', 'N/A')[:300]}...")
    else:
        st.caption("No skills evaluations found.")
    
    # Display Trajectory Evaluations
    st.markdown("---")
    st.markdown("### 🛤️ Trajectory Evaluations")
    trajectory_evals = get_trajectory_evaluations(limit=50)
    if trajectory_evals:
        st.info(f"Found {len(trajectory_evals)} trajectory evaluation(s)")
        for eval_item in trajectory_evals[:10]:  # Show first 10
            with st.expander(f"Trajectory Evaluation: {eval_item.get('trajectory_type', 'N/A')} - {eval_item.get('evaluation_id', 'N/A')[:8]}... - {eval_item.get('created_at', '')}"):
                st.write(f"**Task:** {eval_item.get('task_description', 'N/A')}")
                if eval_item.get('trajectory_type'):
                    st.write(f"**Type:** {eval_item.get('trajectory_type', 'N/A')}")
                try:
                    trajectory_data = json.loads(eval_item.get('trajectory_json', '[]'))
                    st.write(f"**Steps:** {len(trajectory_data)}")
                except:
                    pass
                col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
                with col_t1:
                    st.metric("Step Quality", f"{eval_item.get('step_quality_score', 0):.2f}/10")
                with col_t2:
                    st.metric("Path Efficiency", f"{eval_item.get('path_efficiency_score', 0):.2f}/10")
                with col_t3:
                    st.metric("Reasoning Chain", f"{eval_item.get('reasoning_chain_score', 0):.2f}/10")
                with col_t4:
                    st.metric("Planning Quality", f"{eval_item.get('planning_quality_score', 0):.2f}/10")
                with col_t5:
                    st.metric("Overall", f"{eval_item.get('overall_score', 0):.2f}/10")
                st.markdown(f"**Judgment:** {eval_item.get('judgment_text', 'N/A')[:300]}...")
    else:
        st.caption("No trajectory evaluations found.")

