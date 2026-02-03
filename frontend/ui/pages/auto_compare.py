"""Auto Pairwise Comparison UI page"""
import re
import streamlit as st
from typing import List


def render_auto_compare_page(evaluation_service, available_models: List[str]):
    """Render the Auto Pairwise Comparison page"""
    st.header("Auto Pairwise Comparison")
    st.markdown("Automatically generate responses from two different models and have a judge evaluate them.")
    
    question = st.text_area(
        "Question/Task:",
        height=100,
        placeholder="What is the capital of France?",
        key="auto_question"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model A (Response Generator)")
        model_a = st.selectbox(
            "Select Model A:",
            available_models,
            index=0,
            key="model_a"
        )
        st.info(f"Model A will generate Response A")
    
    with col2:
        st.subheader("Model B (Response Generator)")
        # Make sure Model B is different from Model A
        model_b_index = 1 if len(available_models) > 1 else 0
        if model_b_index >= len(available_models):
            model_b_index = 0
        model_b = st.selectbox(
            "Select Model B:",
            available_models,
            index=model_b_index,
            key="model_b"
        )
        st.info(f"Model B will generate Response B")
    
    if model_a == model_b:
        st.warning("⚠️ Model A and Model B are the same. Please select different models for comparison.")
    
    # Position bias mitigation options
    with st.expander("⚙️ Advanced Options", expanded=False):
        conservative_mode = st.checkbox(
            "Conservative Position Bias Mitigation",
            value=False,
            help="Call judge twice with swapped positions. Only declare a win if both agree, else tie. "
                 "More accurate but uses 2x API calls (MT-Bench paper recommendation).",
            key="auto_compare_conservative_mode"
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
            key="auto_compare_reference_answer"
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
            key="auto_compare_chain_of_thought"
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
            key="auto_compare_few_shot_examples"
        )
        if few_shot_examples:
            st.warning("⚠️ Few-shot examples significantly increase prompt length and API costs (approximately 4×). "
                     "Use only when consistency is critical and cost is acceptable.")
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        generate_btn = st.button("🚀 Generate & Judge", type="primary", use_container_width=True, key="auto_generate_btn")
    
    with col_btn2:
        save_auto_enabled = st.checkbox("💾 Save to DB", value=True, key="save_auto")
    
    with col_btn3:
        if st.button("🔄 New Evaluation", key="auto_new_eval_top", use_container_width=True):
            try:
                st.session_state["auto_question"] = ""
                st.session_state["auto_compare_reference_answer"] = ""
                st.session_state["auto_compare_chain_of_thought"] = False
                st.session_state["auto_compare_few_shot_examples"] = False
                st.session_state["save_auto"] = True
            except Exception:
                pass
            st.rerun()
    
    if generate_btn:
        if not question:
            st.warning("Please enter a question.")
        elif model_a == model_b:
            st.warning("Please select two different models.")
        else:
            # Import functions from core services
            from core.services.llm_service import generate_response
            from core.services.judgment_service import save_judgment
            import re
            
            # Get judge model from session state
            judge_model = st.session_state.get("judge_model", "llama3")
            
            # Step 1: Generate Response A
            with st.status(f"🤖 Generating Response A using {model_a}...", expanded=True) as status_a:
                st.write("Sending request to model...")
                result_a = generate_response(question, model_a)
                if not result_a["success"]:
                    status_a.update(label=f"❌ Error generating Response A", state="error")
                    st.error(f"❌ Error generating Response A: {result_a['error']}")
                    st.stop()
                response_a = result_a["response"]
                status_a.update(label=f"✅ Response A generated", state="complete")
            
            # Step 2: Generate Response B
            with st.status(f"🤖 Generating Response B using {model_b}...", expanded=True) as status_b:
                st.write("Sending request to model...")
                result_b = generate_response(question, model_b)
                if not result_b["success"]:
                    status_b.update(label=f"❌ Error generating Response B", state="error")
                    st.error(f"❌ Error generating Response B: {result_b['error']}")
                    st.stop()
                response_b = result_b["response"]
                status_b.update(label=f"✅ Response B generated", state="complete")
            
            # Display generated responses
            st.success("✅ Responses Generated!")
            
            col_resp1, col_resp2 = st.columns(2)
            
            with col_resp1:
                st.markdown(f"### 📝 Response A (from {model_a})")
                st.text_area(
                    "Response A:",
                    value=response_a,
                    height=400,  # Increased height to show more content
                    key="auto_response_a",
                    disabled=True,
                    help="Full response from Model A. Scroll to see all content."
                )
            
            with col_resp2:
                st.markdown(f"### 📝 Response B (from {model_b})")
                st.text_area(
                    "Response B:",
                    value=response_b,
                    height=400,  # Increased height to show more content
                    key="auto_response_b",
                    disabled=True,
                    help="Full response from Model B. Scroll to see all content."
                )
            
            # Step 3: Judge the responses using the same EvaluationService pairwise pipeline
            spinner_text = f"⚖️ Judging responses using {judge_model}..."
            if conservative_mode:
                spinner_text = f"⚖️ Judging responses using {judge_model} (conservative mode: 2 evaluations)..."
            elif chain_of_thought:
                spinner_text = f"⚖️ Judging responses using {judge_model} (generating Chain-of-Thought solution first)..."
            if conservative_mode and chain_of_thought:
                spinner_text = f"⚖️ Judging responses using {judge_model} (conservative mode + CoT: generating solution, then 2 evaluations)..."
            if few_shot_examples:
                if "few-shot" not in spinner_text.lower():
                    spinner_text += " (with few-shot examples)"
            with st.status(spinner_text, expanded=True) as status_judge:
                st.write("Sending judgment request...")
                result = evaluation_service.evaluate(
                    evaluation_type="pairwise",
                    question=question,
                    judge_model=judge_model,
                    response_a=response_a,
                    response_b=response_b,
                    options={
                        # Disable randomization for maximally deterministic judgments
                        "randomize_order": False,
                        "conservative_position_bias": conservative_mode,
                        "model_a": model_a,
                        "model_b": model_b,
                        "reference_answer": reference_answer.strip() if reference_answer else None,
                        "chain_of_thought": chain_of_thought,
                        "few_shot_examples": few_shot_examples
                    },
                    save_to_db=False,  # We handle saving explicitly below
                )

                if result.get("success"):
                    st.write("✅ Judgment received!")
                    status_judge.update(label="✅ Judgment Complete!", state="complete")
                else:
                    status_judge.update(label="❌ Error during judgment", state="error")

            if result.get("success"):
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
                    # Use expander for long judgments to avoid overwhelming the UI
                    with st.expander("📄 View Full Judgment", expanded=True):
                        st.markdown(cleaned_judgment)
                else:
                    st.warning("⚠️ Judgment content is empty. The model may not have generated a response.")

                score_a = result.get("score_a")
                score_b = result.get("score_b")
                winner = result.get("winner")

                # Display metrics if we have them
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

                # Save to database if enabled
                if save_auto_enabled:
                    try:
                        # Include scores in metrics_json via trace/metrics if needed later;
                        # for now, we mirror the manual pairwise behavior and store them in metrics_json.
                        metrics = {}
                        if score_a is not None:
                            metrics["score_a"] = score_a
                        if score_b is not None:
                            metrics["score_b"] = score_b
                        import json
                        metrics_json = json.dumps(metrics) if metrics else None

                        judgment_id = save_judgment(
                            question=question,
                            response_a=response_a,
                            response_b=response_b,
                            model_a=model_a,
                            model_b=model_b,
                            judge_model=judge_model,
                            judgment=judgment_text,
                            judgment_type="pairwise_auto",
                            evaluation_id=result.get("evaluation_id"),
                            metrics_json=metrics_json,
                            trace_json=None,
                        )
                        st.success(f"💾 Saved to database (ID: {judgment_id})")
                    except Exception as e:
                        st.warning(f"⚠️ Could not save to database: {str(e)}")
            else:
                st.error(f"❌ Error during judgment: {result.get('error', 'Unknown error')}")
                st.info("💡 **Tip:** If the operation is taking too long, you can refresh the page to stop it.")

