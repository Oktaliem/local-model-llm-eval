"""Manual Pairwise Comparison UI page"""
import re
import streamlit as st
from core.services.evaluation_service import EvaluationService


def render_pairwise_page(evaluation_service: EvaluationService):
    """Render the manual pairwise comparison page"""
    st.header("Manual Pairwise Comparison")
    st.markdown("Enter a question and two responses to see which one is better.")

    question = st.text_area("Question/Task:", height=100, placeholder="What is the capital of France?", key="pairwise_question")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Response A")
        response_a = st.text_area("Response A:", height=200, placeholder="Paris is the capital of France.", key="pairwise_response_a")
    with col2:
        st.subheader("Response B")
        response_b = st.text_area(
            "Response B:", height=200, placeholder="The capital of France is Paris, a beautiful city known for its art and culture.", key="pairwise_response_b"
        )

    # Position bias mitigation options
    with st.expander("⚙️ Advanced Options", expanded=False):
        conservative_mode = st.checkbox(
            "Conservative Position Bias Mitigation",
            value=False,
            help="Call judge twice with swapped positions. Only declare a win if both agree, else tie. "
                 "More accurate but uses 2x API calls (MT-Bench paper recommendation).",
            key="pairwise_conservative_mode"
        )
        if conservative_mode:
            st.info("ℹ️ Conservative mode will call the judge twice (once with each order) to ensure consistency. "
                   "This is more accurate but takes longer and costs more.")
        
        st.markdown("---")
        st.markdown("**Reference-Guided Evaluation** (MT-Bench recommendation for math/reasoning)")
        reference_answer = st.text_area(
            "Reference Answer (Optional):",
            height=100,
            placeholder="Enter a reference answer to help the judge evaluate responses more accurately. "
                       "Especially useful for math and reasoning questions. "
                       "If not provided, the judge will evaluate without a reference.",
            help="Provide a reference answer to significantly improve evaluation accuracy for math/reasoning questions. "
                 "According to MT-Bench paper, this reduces failure rate from 70% to 15%.",
            key="pairwise_reference_answer"
        )
        if reference_answer:
            st.info("ℹ️ Reference answer will be included in the evaluation prompt to help the judge make more accurate assessments.")
        
        st.markdown("---")
        st.markdown("**Chain-of-Thought (CoT) Evaluation** (MT-Bench recommendation for math/reasoning)")
        chain_of_thought = st.checkbox(
            "Enable Chain-of-Thought",
            value=False,
            help="Generate judge's independent solution first, then use it to evaluate responses. "
                 "Helps reduce being misled by incorrect answers. "
                 "According to MT-Bench paper, this reduces failure rate from 70% to 30% for math/reasoning questions.",
            key="pairwise_chain_of_thought"
        )
        if chain_of_thought:
            st.info("ℹ️ Chain-of-Thought will generate the judge's solution independently first, then use it to evaluate responses. "
                   "This takes longer but improves accuracy for math and reasoning questions.")
        
        st.markdown("---")
        st.markdown("**Few-Shot Examples** (MT-Bench paper recommendation)")
        few_shot_examples = st.checkbox(
            "Enable Few-Shot Examples",
            value=False,
            help="Include 3 example judgments in the prompt to improve consistency. "
                 "According to MT-Bench paper, this improves consistency from 65% to 77.5%, "
                 "but increases cost approximately 4× due to longer prompts.",
            key="pairwise_few_shot_examples"
        )
        if few_shot_examples:
            st.warning("⚠️ Few-shot examples significantly increase prompt length and API costs (approximately 4×). "
                     "Use only when consistency is critical and cost is acceptable.")
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    with col_btn1:
        judge_btn = st.button("⚖️ Judge Responses", type="primary", use_container_width=True, key="pairwise_judge_btn")
    with col_btn2:
        save_enabled = st.checkbox("💾 Save to DB", value=True, key="save_pairwise_checkbox")
    with col_btn3:
        if st.button("🔄 New Evaluation", key="pairwise_new_eval_top", use_container_width=True):
                    try:
                        st.session_state["pairwise_question"] = ""
                        st.session_state["pairwise_response_a"] = ""
                        st.session_state["pairwise_response_b"] = ""
                        st.session_state["pairwise_reference_answer"] = ""
                        st.session_state["pairwise_chain_of_thought"] = False
                        st.session_state["save_pairwise_checkbox"] = True
                    except Exception:
                        pass
                    st.rerun()

    if judge_btn:
        if not question or not response_a or not response_b:
            st.warning("Please fill in all fields.")
        else:
            judge_model = st.session_state.get("judge_model", "llama3")
            spinner_text = "⚖️ Judging responses..."
            if conservative_mode:
                spinner_text = "⚖️ Judging responses (conservative mode: 2 evaluations)..."
            elif chain_of_thought:
                spinner_text = "⚖️ Judging responses (generating Chain-of-Thought solution first)..."
            if conservative_mode and chain_of_thought:
                spinner_text = "⚖️ Judging responses (conservative mode + CoT: generating solution, then 2 evaluations)..."
            if few_shot_examples:
                if "few-shot" not in spinner_text.lower():
                    spinner_text += " (with few-shot examples)"
            with st.spinner(spinner_text):
                result = evaluation_service.evaluate(
                    evaluation_type="pairwise",
                    question=question,
                    judge_model=judge_model,
                    response_a=response_a,
                    response_b=response_b,
                    # Conservative mode or disable randomization for maximally deterministic judgments
                    options={
                        "randomize_order": False,
                        "conservative_position_bias": conservative_mode,
                        "reference_answer": reference_answer.strip() if reference_answer else None,
                        "chain_of_thought": chain_of_thought,
                        "few_shot_examples": few_shot_examples
                    },
                    save_to_db=save_enabled,
                )
            if result.get("success"):
                st.success("✅ Judgment Complete!")
                st.markdown("### 🎯 Judgment")
                execution_time = result.get("execution_time", 0)
                if execution_time > 0:
                    st.caption(f"⏱️ Execution Time: {execution_time:.2f}s")
                # Show which features were used
                features_used = []
                if conservative_mode:
                    features_used.append("Conservative Position Bias Mitigation")
                if chain_of_thought:
                    features_used.append("Chain-of-Thought (CoT)")
                if few_shot_examples:
                    features_used.append("Few-Shot Examples")
                if features_used:
                    st.info("ℹ️ **Features Used:** " + " • ".join(features_used))
                judgment_text = result.get("judgment", "")
                if judgment_text and judgment_text.strip():
                    # Clean up MT-Bench format brackets for better readability
                    # Replace [[A]], [[B]], [[C]] with A, B, Tie in the displayed text
                    cleaned_judgment = re.sub(r'\[\[A\]\]', 'A', judgment_text)
                    cleaned_judgment = re.sub(r'\[\[B\]\]', 'B', cleaned_judgment)
                    cleaned_judgment = re.sub(r'\[\[C\]\]', 'Tie', cleaned_judgment)
                    # Also clean up "Winner: [[X]]" format
                    cleaned_judgment = re.sub(r'Winner:\s*\[\[A\]\]', 'Winner: A', cleaned_judgment, flags=re.IGNORECASE)
                    cleaned_judgment = re.sub(r'Winner:\s*\[\[B\]\]', 'Winner: B', cleaned_judgment, flags=re.IGNORECASE)
                    cleaned_judgment = re.sub(r'Winner:\s*\[\[C\]\]', 'Winner: Tie', cleaned_judgment, flags=re.IGNORECASE)
                    
                    # Add CSS to prevent table cell truncation in markdown tables
                    st.markdown("""
                    <style>
                    /* Prevent truncation in markdown tables */
                    .element-container table {
                        width: 100% !important;
                        table-layout: auto !important;
                    }
                    .element-container table th,
                    .element-container table td {
                        word-wrap: break-word !important;
                        overflow-wrap: break-word !important;
                        white-space: normal !important;
                        max-width: none !important;
                        padding: 8px !important;
                    }
                    /* Ensure tables can expand horizontally */
                    .element-container {
                        overflow-x: auto !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    # Use expander for long judgments (match Auto Compare UI)
                    with st.expander("📄 View Full Judgment", expanded=True):
                        st.markdown(cleaned_judgment)
                else:
                    st.warning("⚠️ Judgment content is empty. The model may not have generated a response.")
                score_a = result.get("score_a")
                score_b = result.get("score_b")
                winner = result.get("winner")
                if score_a is not None or score_b is not None or winner:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if score_a is not None:
                            st.metric("Score A", f"{score_a:.1f}")
                    with c2:
                        if score_b is not None:
                            st.metric("Score B", f"{score_b:.1f}")
                    with c3:
                        if winner:
                            st.metric("Winner", winner)
                if save_enabled:
                    st.success("💾 Saved to database")
                # New Evaluation button to reset inputs
                if st.button("🔄 New Evaluation", key="pairwise_new_evaluation_btn"):
                    try:
                        st.session_state["pairwise_question"] = ""
                        st.session_state["pairwise_response_a"] = ""
                        st.session_state["pairwise_response_b"] = ""
                        st.session_state["pairwise_reference_answer"] = ""
                        st.session_state["pairwise_chain_of_thought"] = False
                        st.session_state["save_pairwise_checkbox"] = True
                    except Exception:
                        pass
                    st.rerun()
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Note: single reset button is provided alongside controls above to avoid duplication.

