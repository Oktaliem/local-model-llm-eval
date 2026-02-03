"""Single Response Grading UI page"""
import streamlit as st
from core.services.evaluation_service import EvaluationService
from typing import Optional


def render_single_page(evaluation_service: EvaluationService):
    """Render the Single Response Grading page"""
    st.header("Grade Single Response")
    st.markdown("Evaluate a single response with detailed feedback and scoring.")
    
    question = st.text_area(
        "Question/Task:",
        height=100,
        placeholder="Explain the concept of machine learning in simple terms.",
        key="single_question"
    )
    
    response = st.text_area(
        "Response to Evaluate:",
        height=200,
        placeholder="Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed...",
        key="single_response"
    )
    
    criteria = st.text_area(
        "Custom Evaluation Criteria (optional):",
        height=100,
        placeholder="Focus on clarity, use of examples, and accessibility to non-technical audiences.",
        key="criteria"
    )
    
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        evaluate_btn = st.button("📊 Evaluate Response", type="primary", use_container_width=True)
    
    with col_btn2:
        save_single_enabled = st.checkbox("💾 Save to DB", value=True, key="save_single")
    
    if evaluate_btn:
        if not question or not response:
            st.warning("Please fill in the question and response fields.")
        else:
            judge_model = st.session_state.get("judge_model", "llama3")
            with st.spinner("📊 Evaluating response..."):
                result = evaluation_service.evaluate(
                    evaluation_type="single",
                    question=question,
                    judge_model=judge_model,
                    response=response,
                    options={"criteria": criteria if criteria else None},
                    save_to_db=save_single_enabled,
                )
            
            if result.get("success"):
                st.success("✅ Evaluation Complete!")
                st.markdown("### 📋 Evaluation Results")
                execution_time = result.get("execution_time", 0)
                if execution_time > 0:
                    st.caption(f"⏱️ Execution Time: {execution_time:.2f}s")
                judgment_text = result.get("judgment", "")
                if judgment_text and judgment_text.strip():
                    # Use expander for better readability of long judgments
                    with st.expander("📄 View Full Evaluation", expanded=True):
                        st.markdown(judgment_text)
                else:
                    st.warning("⚠️ Evaluation content is empty. The model may not have generated a response.")
                
                # Extract and display score if available
                score = result.get("score")
                if score is not None:
                    st.metric("Score", f"{score:.1f}/10")
                
                if save_single_enabled:
                    st.success("💾 Saved to database")
                
                # New Evaluation button to reset inputs
                if st.button("🔄 New Evaluation", key="single_new_evaluation_btn"):
                    try:
                        st.session_state["single_question"] = ""
                        st.session_state["single_response"] = ""
                        st.session_state["criteria"] = ""
                        st.session_state["save_single"] = True
                    except Exception:
                        pass
                    st.rerun()
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

