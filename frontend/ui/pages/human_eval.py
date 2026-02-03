"""Human Evaluation UI page"""
import streamlit as st
import json
import pandas as pd
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_human_eval_page(evaluation_service: EvaluationService):
    """Render the Human Evaluation page"""
    # Import helper functions from backend services
    from backend.services.data_service import (
        save_human_annotation,
        get_human_annotations,
        get_all_judgments,
        get_annotations_for_comparison,
        calculate_agreement_metrics
    )
    
    st.header("👤 Human Evaluation")
    st.markdown("Add human annotations to evaluate responses. Compare human judgments with LLM evaluations.")
    
    eval_mode = st.radio(
        "Evaluation Mode:",
        ["New Evaluation", "Compare with LLM Judgment", "View All Annotations"],
        horizontal=True,
        key="human_eval_mode"
    )
    
    if eval_mode == "New Evaluation":
        st.markdown("### 📝 Create New Human Annotation")
        
        col_info, col_eval = st.columns([1, 1])
        
        with col_info:
            annotator_name = st.text_input("Annotator Name *", placeholder="John Doe", key="human_annotator_name")
            annotator_email = st.text_input("Annotator Email (optional)", placeholder="john@example.com", key="human_annotator_email")
        
        with col_eval:
            eval_type = st.selectbox(
                "Evaluation Type *",
                ["comprehensive", "single", "pairwise"],
                help="comprehensive: 5 metrics | single: overall score | pairwise: compare two responses",
                key="human_eval_type"
            )
        
        question = st.text_area(
            "Question/Task *",
            height=100,
            placeholder="What is machine learning?",
            key="human_question"
        )
        
        if eval_type == "pairwise":
            col_a, col_b = st.columns(2)
            with col_a:
                response_a = st.text_area("Response A *", height=150, key="human_resp_a")
            with col_b:
                response_b = st.text_area("Response B *", height=150, key="human_resp_b")
            response = None
        else:
            response = st.text_area("Response *", height=200, placeholder="Enter the response to evaluate", key="human_response")
            response_a = None
            response_b = None
        
        if eval_type == "comprehensive":
            st.markdown("### 📊 Rate Each Metric (0-10 scale)")
            col1, col2 = st.columns(2)
            
            with col1:
                accuracy_score = st.slider("Accuracy", 0.0, 10.0, 5.0, 0.1, 
                                            help="How factually correct is the response?",
                                            key="human_accuracy")
                relevance_score = st.slider("Relevance", 0.0, 10.0, 5.0, 0.1,
                                            help="How relevant is the response to the question?",
                                            key="human_relevance")
                coherence_score = st.slider("Coherence", 0.0, 10.0, 5.0, 0.1,
                                            help="How well-structured and coherent is the response?",
                                            key="human_coherence")
            
            with col2:
                hallucination_score = st.slider("Hallucination Risk", 0.0, 10.0, 5.0, 0.1,
                                                help="How likely is the response to contain false information? (Lower is better)",
                                                key="human_hallucination")
                toxicity_score = st.slider("Toxicity Risk", 0.0, 10.0, 0.0, 0.1,
                                           help="How likely is the response to contain toxic content? (Lower is better)",
                                           key="human_toxicity")
            
            overall_score = None  # Will be calculated
        elif eval_type == "single":
            overall_score = st.slider("Overall Score", 0.0, 10.0, 5.0, 0.1,
                                     help="Overall quality of the response",
                                     key="human_overall")
            accuracy_score = None
            relevance_score = None
            coherence_score = None
            hallucination_score = None
            toxicity_score = None
        else:  # pairwise
            winner = st.radio("Which response is better?", ["Response A", "Response B", "Tie"], key="human_winner")
            overall_score = st.slider("Overall Quality Difference", 0.0, 10.0, 5.0, 0.1,
                                     help="How much better is the winning response?",
                                     key="human_quality_diff")
            accuracy_score = None
            relevance_score = None
            coherence_score = None
            hallucination_score = None
            toxicity_score = None
        
        feedback_text = st.text_area(
            "Additional Feedback (optional)",
            height=100,
            placeholder="Add any additional comments or observations...",
            key="human_feedback"
        )
        
        if st.button("💾 Save Human Annotation", type="primary", use_container_width=True, key="save_human_annotation"):
            if not annotator_name or not question:
                st.error("Please fill in required fields (Annotator Name and Question)")
            elif eval_type != "pairwise" and not response:
                st.error("Please provide a response to evaluate")
            elif eval_type == "pairwise" and (not response_a or not response_b):
                st.error("Please provide both Response A and Response B")
            else:
                try:
                    annotation_id = save_human_annotation(
                        annotator_name=annotator_name,
                        annotator_email=annotator_email if annotator_email else None,
                        question=question,
                        evaluation_type=eval_type,
                        response=response,
                        response_a=response_a,
                        response_b=response_b,
                        accuracy_score=accuracy_score,
                        relevance_score=relevance_score,
                        coherence_score=coherence_score,
                        hallucination_score=hallucination_score,
                        toxicity_score=toxicity_score,
                        overall_score=overall_score,
                        feedback_text=feedback_text if feedback_text else None
                    )
                    st.success(f"✅ Human annotation saved successfully! (ID: {annotation_id})")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error saving annotation: {str(e)}")
                    st.exception(e)
    
    elif eval_mode == "Compare with LLM Judgment":
        st.markdown("### 🔄 Compare Human vs LLM Evaluations")
        
        # Get all judgments
        judgments = get_all_judgments(limit=100)
        
        if not judgments:
            st.info("No LLM judgments found. Create some evaluations first!")
        else:
            judgment_options = {f"ID {j['id']}: {j['question'][:50]}...": j['id'] for j in judgments}
            selected_judgment = st.selectbox("Select LLM Judgment to Compare", list(judgment_options.keys()), key="human_judgment_select")
            judgment_id = judgment_options[selected_judgment] if selected_judgment else None
            
            if judgment_id:
                comparison_data = get_annotations_for_comparison(judgment_id=judgment_id)
                human_annotations = comparison_data['human_annotations']
                llm_judgments = comparison_data['llm_judgments']
                
                if llm_judgments:
                    llm_judgment = llm_judgments[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🤖 LLM Evaluation")
                        st.write(f"**Question:** {llm_judgment.get('question', 'N/A')}")
                        st.write(f"**Type:** {llm_judgment.get('judgment_type', 'N/A')}")
                        
                        if llm_judgment.get('metrics_json'):
                            try:
                                metrics = json.loads(llm_judgment['metrics_json'])
                                st.write("**Metrics:**")
                                if isinstance(metrics, dict):
                                    if 'overall_score' in metrics:
                                        st.metric("Overall Score", f"{metrics['overall_score']:.2f}/10")
                                    for key, value in metrics.items():
                                        if key != 'overall_score' and isinstance(value, dict) and 'score' in value:
                                            st.write(f"- {key.capitalize()}: {value['score']:.2f}/10")
                            except:
                                st.write("**Judgment:**", llm_judgment.get('judgment', 'N/A'))
                        else:
                            st.write("**Judgment:**", llm_judgment.get('judgment', 'N/A'))
                    
                    with col2:
                        st.markdown("#### 👤 Human Annotations")
                        
                        # Check if user clicked "Add Human Annotation" button
                        if st.session_state.get('add_annotation_for_judgment') == judgment_id:
                            st.markdown("---")
                            st.markdown("### ➕ Add Human Annotation")
                            
                            col_info, col_eval = st.columns([1, 1])
                            with col_info:
                                annotator_name = st.text_input("Annotator Name *", placeholder="John Doe", key="human_annotator_name_compare")
                                annotator_email = st.text_input("Annotator Email (optional)", placeholder="john@example.com", key="human_annotator_email_compare")
                            
                            with col_eval:
                                # Determine evaluation type from LLM judgment
                                llm_type = llm_judgment.get('judgment_type', 'comprehensive')
                                if llm_type in ['pairwise_manual', 'pairwise_auto']:
                                    eval_type = "pairwise"
                                elif llm_type == 'single':
                                    eval_type = "single"
                                else:
                                    eval_type = "comprehensive"
                                
                                st.selectbox(
                                    "Evaluation Type *",
                                    [eval_type],
                                    disabled=True,
                                    help=f"Matches LLM judgment type: {llm_type}",
                                    key="human_eval_type_compare"
                                )
                            
                            # Pre-fill question from LLM judgment
                            question = st.text_area(
                                "Question/Task *",
                                value=llm_judgment.get('question', ''),
                                height=100,
                                key="human_question_compare"
                            )
                            
                            # Handle different evaluation types
                            if eval_type == "pairwise":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    response_a = st.text_area("Response A *", value=llm_judgment.get('response_a', ''), height=150, key="human_resp_a_compare")
                                with col_b:
                                    response_b = st.text_area("Response B *", value=llm_judgment.get('response_b', ''), height=150, key="human_resp_b_compare")
                                response = None
                            else:
                                response = st.text_area("Response *", value=llm_judgment.get('response_a', ''), height=200, key="human_response_compare")
                                response_a = None
                                response_b = None
                            
                            if eval_type == "comprehensive":
                                st.markdown("### 📊 Rate Each Metric (0-10 scale)")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    accuracy_score = st.slider("Accuracy", 0.0, 10.0, 5.0, 0.1, key="human_accuracy_compare")
                                    relevance_score = st.slider("Relevance", 0.0, 10.0, 5.0, 0.1, key="human_relevance_compare")
                                    coherence_score = st.slider("Coherence", 0.0, 10.0, 5.0, 0.1, key="human_coherence_compare")
                                
                                with col2:
                                    hallucination_score = st.slider("Hallucination Risk", 0.0, 10.0, 5.0, 0.1, key="human_hallucination_compare")
                                    toxicity_score = st.slider("Toxicity Risk", 0.0, 10.0, 0.0, 0.1, key="human_toxicity_compare")
                                
                                overall_score = None
                            elif eval_type == "single":
                                overall_score = st.slider("Overall Score", 0.0, 10.0, 5.0, 0.1, key="human_overall_compare")
                                accuracy_score = None
                                relevance_score = None
                                coherence_score = None
                                hallucination_score = None
                                toxicity_score = None
                            else:  # pairwise
                                winner = st.radio("Which response is better?", ["Response A", "Response B", "Tie"], key="human_winner_compare")
                                overall_score = st.slider("Overall Quality Difference", 0.0, 10.0, 5.0, 0.1, key="human_quality_diff_compare")
                                accuracy_score = None
                                relevance_score = None
                                coherence_score = None
                                hallucination_score = None
                                toxicity_score = None
                            
                            feedback_text = st.text_area(
                                "Additional Feedback (optional)",
                                height=100,
                                placeholder="Add any additional comments or observations...",
                                key="human_feedback_compare"
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("💾 Save Human Annotation", type="primary", use_container_width=True, key="save_human_annotation_compare"):
                                    if not annotator_name or not question:
                                        st.error("Please fill in required fields (Annotator Name and Question)")
                                    elif eval_type != "pairwise" and not response:
                                        st.error("Please provide a response to evaluate")
                                    elif eval_type == "pairwise" and (not response_a or not response_b):
                                        st.error("Please provide both Response A and Response B")
                                    else:
                                        try:
                                            annotation_id = save_human_annotation(
                                                annotator_name=annotator_name,
                                                annotator_email=annotator_email if annotator_email else None,
                                                question=question,
                                                evaluation_type=eval_type,
                                                response=response,
                                                response_a=response_a,
                                                response_b=response_b,
                                                accuracy_score=accuracy_score,
                                                relevance_score=relevance_score,
                                                coherence_score=coherence_score,
                                                hallucination_score=hallucination_score,
                                                toxicity_score=toxicity_score,
                                                overall_score=overall_score,
                                                feedback_text=feedback_text if feedback_text else None,
                                                judgment_id=judgment_id  # Link to LLM judgment
                                            )
                                            st.success(f"✅ Human annotation saved successfully! (ID: {annotation_id})")
                                            st.balloons()
                                            # Clear the session state to hide the form
                                            del st.session_state.add_annotation_for_judgment
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error saving annotation: {str(e)}")
                            with col_btn2:
                                if st.button("❌ Cancel", use_container_width=True, key="cancel_annotation_compare"):
                                    del st.session_state.add_annotation_for_judgment
                                    st.rerun()
                        
                        # Display existing annotations
                        if human_annotations:
                            for i, annotation in enumerate(human_annotations, 1):
                                with st.expander(f"Annotation {i} by {annotation.get('annotator_name', 'Unknown')}"):
                                    st.write(f"**Overall Score:** {annotation.get('overall_score', 'N/A')}/10")
                                    if annotation.get('accuracy_score') is not None:
                                        st.write(f"- Accuracy: {annotation.get('accuracy_score')}/10")
                                    if annotation.get('relevance_score') is not None:
                                        st.write(f"- Relevance: {annotation.get('relevance_score')}/10")
                                    if annotation.get('coherence_score') is not None:
                                        st.write(f"- Coherence: {annotation.get('coherence_score')}/10")
                                    if annotation.get('feedback_text'):
                                        st.write(f"**Feedback:** {annotation.get('feedback_text')}")
                        elif not st.session_state.get('add_annotation_for_judgment'):
                            st.info("No human annotations for this judgment yet.")
                            if st.button("➕ Add Human Annotation", key="add_annotation_compare"):
                                st.session_state.add_annotation_for_judgment = judgment_id
                                st.rerun()
                
                # Agreement metrics if multiple annotations
                if len(human_annotations) >= 2:
                    st.markdown("### 📊 Inter-Annotator Agreement")
                    agreement = calculate_agreement_metrics(human_annotations)
                    if agreement.get('agreement_available'):
                        st.write(f"**Number of Annotators:** {agreement['num_annotators']}")
                        if agreement.get('metrics'):
                            metrics_df = pd.DataFrame(agreement['metrics']).T
                            st.dataframe(metrics_df, use_container_width=True)
    
    else:  # View All Annotations
        st.markdown("### 📋 All Human Annotations")
        
        annotations = get_human_annotations(limit=100)
        
        if not annotations:
            st.info("No human annotations found. Create some evaluations!")
        else:
            st.success(f"Found {len(annotations)} annotation(s)")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("Filter by Type", ["All"] + list(set(a.get('evaluation_type', '') for a in annotations)), key="human_filter_type")
            with col2:
                filter_annotator = st.selectbox("Filter by Annotator", ["All"] + list(set(a.get('annotator_name', '') for a in annotations)), key="human_filter_annotator")
            
            filtered_annotations = annotations
            if filter_type != "All":
                filtered_annotations = [a for a in filtered_annotations if a.get('evaluation_type') == filter_type]
            if filter_annotator != "All":
                filtered_annotations = [a for a in filtered_annotations if a.get('annotator_name') == filter_annotator]
            
            for annotation in filtered_annotations:
                with st.expander(f"Annotation by {annotation.get('annotator_name', 'Unknown')} - {annotation.get('created_at', '')}"):
                    st.write(f"**Question:** {annotation.get('question', 'N/A')}")
                    st.write(f"**Type:** {annotation.get('evaluation_type', 'N/A')}")
                    st.write(f"**Overall Score:** {annotation.get('overall_score', 'N/A')}/10")
                    
                    if annotation.get('accuracy_score') is not None:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Accuracy", f"{annotation.get('accuracy_score')}/10")
                        with col2:
                            st.metric("Relevance", f"{annotation.get('relevance_score')}/10")
                        with col3:
                            st.metric("Coherence", f"{annotation.get('coherence_score')}/10")
                    
                    if annotation.get('feedback_text'):
                        st.write(f"**Feedback:** {annotation.get('feedback_text')}")

