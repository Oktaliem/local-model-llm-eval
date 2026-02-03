"""A/B Testing UI page"""
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_ab_testing_page(evaluation_service: EvaluationService):
    """Render the A/B Testing page"""
    # Import helper functions from backend services
    from backend.services.ab_test_service import (
        create_ab_test,
        get_all_ab_tests,
        get_ab_test,
        execute_ab_test
    )
    from backend.services.model_service import get_available_models
    
    st.header("🧪 A/B Testing Framework")
    st.markdown("Compare different models/configurations with statistical significance testing.")
    
    # Get available models with fallback (silent fallback like other pages)
    available_models = get_available_models()
    if not available_models:
        # Fallback to common model names if Ollama is not accessible
        available_models = ['llama3', 'mistral', 'gpt-oss-safeguard:20b', 'qwen2.5-coder:14b']
    
    # Find default index for "gpt-oss-safeguard:20b" (default model)
    default_model = "gpt-oss-safeguard:20b"
    default_index = 0
    if default_model in available_models:
        default_index = available_models.index(default_model)
    
    ab_mode = st.radio(
        "Select Mode",
        ["Create New A/B Test", "Run A/B Test", "View Test Results"],
        horizontal=True,
        key="ab_mode"
    )
    
    if ab_mode == "Create New A/B Test":
        st.markdown("### 📝 Create New A/B Test")
        
        test_name = st.text_input("Test Name", placeholder="e.g., Llama3 vs Mistral Comparison", key="ab_test_name")
        test_description = st.text_area("Test Description (Optional)", placeholder="Describe what you're testing...", key="ab_test_description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Variant A Configuration")
            variant_a_name = st.text_input("Variant A Name", value="Variant A", key="var_a_name")
            eval_type = st.selectbox(
                "Evaluation Type",
                ["comprehensive", "pairwise"],
                key="ab_eval_type"
            )
            
            if eval_type == "comprehensive":
                variant_a_model = st.selectbox(
                    "Model A (for generating responses)",
                    available_models,
                    index=default_index,
                    key="var_a_model"
                )
                variant_a_config = {
                    "model_a": variant_a_model,
                    "task_type": st.selectbox(
                        "Task Type",
                        ["general", "technical", "creative", "analytical"],
                        key="var_a_task"
                    )
                }
            else:
                variant_a_model = st.selectbox(
                    "Model A (for generating responses)",
                    available_models,
                    index=default_index,
                    key="var_a_model_pairwise"
                )
                variant_a_config = {"model_a": variant_a_model}
        
        with col2:
            st.markdown("#### Variant B Configuration")
            variant_b_name = st.text_input("Variant B Name", value="Variant B", key="var_b_name")
            
            if eval_type == "comprehensive":
                variant_b_model = st.selectbox(
                    "Model B (for generating responses)",
                    available_models,
                    index=default_index,
                    key="var_b_model"
                )
                variant_b_config = {
                    "model_b": variant_b_model,
                    "task_type": st.selectbox(
                        "Task Type",
                        ["general", "technical", "creative", "analytical"],
                        key="var_b_task"
                    )
                }
            else:
                variant_b_model = st.selectbox(
                    "Model B (for generating responses)",
                    available_models,
                    index=default_index,
                    key="var_b_model_pairwise"
                )
                variant_b_config = {"model_b": variant_b_model}
        
        st.markdown("---")
        st.markdown("### 📋 Test Cases")
        
        test_case_input = st.radio(
            "Input Method",
            ["Manual Entry", "Upload JSON/CSV"],
            horizontal=True,
            key="test_case_input"
        )
        
        test_cases = []
        
        if test_case_input == "Manual Entry":
            num_cases = st.number_input("Number of Test Cases", min_value=1, max_value=50, value=3, key="num_cases")
            
            for i in range(num_cases):
                with st.expander(f"Test Case {i+1}"):
                    question = st.text_area(f"Question {i+1}", key=f"ab_q_{i}")
                    if eval_type == "comprehensive":
                        if st.checkbox(f"Provide response for Variant A (optional)", key=f"ab_provide_a_{i}"):
                            response_a = st.text_area(f"Response A {i+1}", key=f"ab_resp_a_{i}")
                        else:
                            response_a = None
                        if st.checkbox(f"Provide response for Variant B (optional)", key=f"ab_provide_b_{i}"):
                            response_b = st.text_area(f"Response B {i+1}", key=f"ab_resp_b_{i}")
                        else:
                            response_b = None
                    else:
                        response_a = st.text_area(f"Response A {i+1}", key=f"ab_resp_a_pairwise_{i}")
                        response_b = st.text_area(f"Response B {i+1}", key=f"ab_resp_b_pairwise_{i}")
                    
                    if question:
                        test_case = {"question": question}
                        if response_a:
                            test_case["response_a"] = response_a
                        if response_b:
                            test_case["response_b"] = response_b
                        test_cases.append(test_case)
        else:
            uploaded_file = st.file_uploader("Upload Test Cases", type=["json", "csv"], key="ab_test_file")
            if uploaded_file:
                if uploaded_file.name.endswith('.json'):
                    test_cases = json.load(uploaded_file)
                    if not isinstance(test_cases, list):
                        st.error("JSON file must contain an array of test cases")
                        test_cases = []
                else:
                    df = pd.read_csv(uploaded_file)
                    if 'question' in df.columns:
                        test_cases = df.to_dict('records')
                    else:
                        st.error("CSV must have a 'question' column")
                        test_cases = []
                
                if test_cases:
                    st.success(f"Loaded {len(test_cases)} test cases")
                    st.dataframe(pd.DataFrame(test_cases).head())
        
        if st.button("💾 Create A/B Test", type="primary", key="create_ab_test"):
            if not test_name:
                st.error("Please provide a test name")
            elif not test_cases:
                st.error("Please provide at least one test case")
            else:
                test_id = create_ab_test(
                    test_name=test_name,
                    variant_a_name=variant_a_name,
                    variant_b_name=variant_b_name,
                    variant_a_config=variant_a_config,
                    variant_b_config=variant_b_config,
                    evaluation_type=eval_type,
                    test_cases=test_cases,
                    test_description=test_description
                )
                st.success(f"✅ A/B Test created! Test ID: {test_id}")
                st.info("Go to 'Run A/B Test' to execute it.")
    
    elif ab_mode == "Run A/B Test":
        st.markdown("### ▶️ Run A/B Test")
        
        all_tests = get_all_ab_tests(limit=100)
        
        if not all_tests:
            st.info("No A/B tests found. Create one first!")
        else:
            test_options = {f"{t['test_name']} ({t['status']})": t['test_id'] for t in all_tests}
            selected_test_name = st.selectbox("Select A/B Test", list(test_options.keys()), key="select_ab_test")
            selected_test_id = test_options[selected_test_name]
            
            test = get_ab_test(selected_test_id)
            
            if test:
                st.markdown("#### Test Configuration")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Test Name", test['test_name'])
                with col2:
                    st.metric("Status", test['status'])
                with col3:
                    st.metric("Total Cases", test['total_cases'])
                
                st.markdown(f"**Variant A:** {test['variant_a_name']}")
                st.markdown(f"**Variant B:** {test['variant_b_name']}")
                st.markdown(f"**Evaluation Type:** {test['evaluation_type']}")
                
                judge_model = st.selectbox(
                    "Judge Model",
                    available_models,
                    index=default_index,
                    key="ab_judge_model"
                )
                
                if test['status'] == 'completed':
                    st.warning("This test has already been completed. Running again will overwrite previous results.")
                
                # Initialize session state
                if 'ab_test_running' not in st.session_state:
                    st.session_state.ab_test_running = False
                if 'ab_test_result' not in st.session_state:
                    st.session_state.ab_test_result = None
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ Run A/B Test", type="primary", key="run_ab_test"):
                        if st.session_state.ab_test_running:
                            st.warning("Test is already running!")
                        else:
                            st.session_state.ab_test_running = True
                            st.session_state.ab_test_result = None
                            
                            def update_progress(current, total):
                                progress = current / total
                                st.progress(progress)
                                st.text(f"Processing {current}/{total} test cases...")
                            
                            try:
                                result = execute_ab_test(
                                    test_id=selected_test_id,
                                    judge_model=judge_model,
                                    progress_callback=update_progress
                                )
                                
                                if result.get('success'):
                                    st.session_state.ab_test_result = result
                                    st.session_state.ab_test_running = False
                                    st.success("✅ A/B Test completed!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                                    st.session_state.ab_test_running = False
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                st.session_state.ab_test_running = False
                
                with col2:
                    if st.button("⏹️ Stop", key="stop_ab_test"):
                        st.session_state.ab_test_running = False
                        st.warning("Stopping test...")
                        st.rerun()
                
                if st.session_state.ab_test_running:
                    st.info("⏳ A/B test is running... Please wait.")
    
    else:  # View Test Results
        st.markdown("### 📊 View A/B Test Results")
        
        all_tests = get_all_ab_tests(limit=100)
        
        if not all_tests:
            st.info("No A/B tests found.")
        else:
            test_options = {f"{t['test_name']} ({t['status']})": t['test_id'] for t in all_tests}
            selected_test_name = st.selectbox("Select A/B Test", list(test_options.keys()), key="view_ab_test")
            selected_test_id = test_options[selected_test_name]
            
            test = get_ab_test(selected_test_id)
            
            if test:
                st.markdown("#### Test Overview")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", test['status'])
                with col2:
                    st.metric("Total Cases", test['total_cases'])
                with col3:
                    st.metric("Completed", test['completed_cases'])
                with col4:
                    if test['status'] == 'completed':
                        win_rate_a = (test['variant_a_wins'] / test['total_cases'] * 100) if test['total_cases'] > 0 else 0
                        st.metric("Variant A Win Rate", f"{win_rate_a:.1f}%")
                
                st.markdown(f"**Variant A:** {test['variant_a_name']}")
                st.markdown(f"**Variant B:** {test['variant_b_name']}")
                
                if test['status'] == 'completed' and test.get('results_json'):
                    results = test['results_json']
                    stats_analysis = test.get('statistical_analysis_json', {})
                    
                    st.markdown("---")
                    st.markdown("#### 📈 Summary Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Variant A Wins", test['variant_a_wins'])
                    with col2:
                        st.metric("Variant B Wins", test['variant_b_wins'])
                    with col3:
                        st.metric("Ties", test['ties'])
                    
                    # Statistical Analysis
                    if stats_analysis and stats_analysis.get('valid'):
                        st.markdown("---")
                        st.markdown("#### 📊 Statistical Significance Analysis")
                        
                        # Handle both old and new format for backward compatibility
                        # Check for new format first (from backend/services/statistics.py)
                        if 'mean_a' in stats_analysis or 'test_type' in stats_analysis:
                            # New format (from backend/services/statistics.py)
                            mean_a = stats_analysis.get('mean_a', 0)
                            mean_b = stats_analysis.get('mean_b', 0)
                            std_a = stats_analysis.get('std_a', 0)
                            std_b = stats_analysis.get('std_b', 0)
                            n_a = stats_analysis.get('n_a', 0)
                            n_b = stats_analysis.get('n_b', 0)
                            mean_diff = mean_a - mean_b
                            percent_diff = (mean_diff / mean_b * 100) if mean_b != 0 else 0
                            ci = stats_analysis.get('confidence_interval', {})
                            ci_lower = ci.get('lower', 0) if isinstance(ci, dict) else 0
                            ci_upper = ci.get('upper', 0) if isinstance(ci, dict) else 0
                            test_type = stats_analysis.get('test_type', 'unpaired')
                            has_paired = test_type == 'paired' and 'paired_analysis' in stats_analysis
                        elif 'variant_a' in stats_analysis:
                            # Old format (from frontend/app.py)
                            variant_a_stats = stats_analysis.get('variant_a', {})
                            variant_b_stats = stats_analysis.get('variant_b', {})
                            mean_a = variant_a_stats.get('mean', 0)
                            mean_b = variant_b_stats.get('mean', 0)
                            std_a = variant_a_stats.get('std', 0)
                            std_b = variant_b_stats.get('std', 0)
                            n_a = variant_a_stats.get('n', 0)
                            n_b = variant_b_stats.get('n', 0)
                            diff = stats_analysis.get('difference', {})
                            mean_diff = diff.get('mean_diff', 0) if isinstance(diff, dict) else 0
                            percent_diff = diff.get('percent_diff', 0) if isinstance(diff, dict) else 0
                            ci_lower = diff.get('ci_lower', 0) if isinstance(diff, dict) else 0
                            ci_upper = diff.get('ci_upper', 0) if isinstance(diff, dict) else 0
                            test_type = "unpaired"  # Old format was always unpaired
                            has_paired = False
                        else:
                            # Fallback: try to extract from available keys
                            mean_a = stats_analysis.get('mean_a', stats_analysis.get('mean_a', 0))
                            mean_b = stats_analysis.get('mean_b', stats_analysis.get('mean_b', 0))
                            std_a = stats_analysis.get('std_a', 0)
                            std_b = stats_analysis.get('std_b', 0)
                            n_a = stats_analysis.get('n_a', 0)
                            n_b = stats_analysis.get('n_b', 0)
                            mean_diff = mean_a - mean_b
                            percent_diff = (mean_diff / mean_b * 100) if mean_b != 0 else 0
                            ci = stats_analysis.get('confidence_interval', {})
                            ci_lower = ci.get('lower', 0) if isinstance(ci, dict) else 0
                            ci_upper = ci.get('upper', 0) if isinstance(ci, dict) else 0
                            test_type = stats_analysis.get('test_type', 'unpaired')
                            has_paired = test_type == 'paired' and 'paired_analysis' in stats_analysis
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Variant A Statistics**")
                            st.write(f"- Mean: {mean_a:.2f}")
                            st.write(f"- Std Dev: {std_a:.2f}")
                            st.write(f"- N: {n_a}")
                        
                        with col2:
                            st.markdown("**Variant B Statistics**")
                            st.write(f"- Mean: {mean_b:.2f}")
                            st.write(f"- Std Dev: {std_b:.2f}")
                            st.write(f"- N: {n_b}")
                        
                        st.markdown("**Difference**")
                        st.write(f"- Mean Difference: {mean_diff:.2f} ({percent_diff:.1f}%)")
                        st.write(f"- 95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
                        
                        # Display test type and paired analysis if available
                        if has_paired:
                            paired = stats_analysis['paired_analysis']
                            comparison = stats_analysis.get('comparison', {})
                            
                            st.info(f"🔬 **Test Method:** {stats_analysis.get('interpretation', {}).get('test_method', 'paired t-test')} (Auto-detected paired data)")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Paired T-Test Results**")
                                st.write(f"- p-value: {paired['p_value']:.4f}")
                                st.write(f"- Significant: {'✅ Yes' if paired['is_significant'] else '❌ No'}")
                                st.write(f"- Standard Error: {paired['standard_error']:.4f}")
                                st.write(f"- Correlation: {paired['correlation']:.3f}")
                            
                            with col2:
                                st.markdown("**Power Improvement**")
                                power_improvement = comparison.get('power_improvement', '1.0×')
                                se_reduction = comparison.get('se_reduction_percent', 0)
                                st.metric("Power Improvement", power_improvement)
                                st.write(f"- SE Reduction: {se_reduction:.1f}%")
                                st.write(f"- Paired SE: {comparison.get('paired_se', 0):.4f}")
                                st.write(f"- Unpaired SE: {comparison.get('unpaired_se', 0):.4f}")
                            
                            # Interpretation
                            interpretation = stats_analysis.get('interpretation', {})
                            if 'correlation_benefit' in interpretation:
                                st.write(f"💡 {interpretation['correlation_benefit']}")
                            if 'power_improvement' in interpretation:
                                st.write(f"💡 {interpretation['power_improvement']}")
                            
                            # Show unpaired comparison if available
                            if 'unpaired_analysis' in stats_analysis:
                                with st.expander("📊 Compare with Unpaired Method"):
                                    unpaired = stats_analysis['unpaired_analysis']
                                    st.write(f"**Unpaired T-Test:** p-value = {unpaired.get('p_value', 0):.4f}, SE = {unpaired.get('standard_error', 0):.4f}")
                                    st.write(f"**Paired T-Test:** p-value = {paired['p_value']:.4f}, SE = {paired['standard_error']:.4f}")
                                    if paired['p_value'] < unpaired.get('p_value', 1.0):
                                        st.success("✅ Paired method shows stronger significance!")
                        else:
                            # Unpaired or old format
                            test_method = stats_analysis.get('interpretation', {}).get('test_method', 'unpaired t-test')
                            st.info(f"🔬 **Test Method:** {test_method}")
                            
                            # Statistical Tests
                            if 'statistical_tests' in stats_analysis:
                                # Old format
                                t_test = stats_analysis['statistical_tests']['t_test']
                                mw_test = stats_analysis['statistical_tests']['mann_whitney']
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**T-Test (Independent Samples)**")
                                    st.write(f"- p-value: {t_test['p_value']:.4f}")
                                    st.write(f"- Significant: {'✅ Yes' if t_test['significant'] else '❌ No'}")
                                    st.write(f"- Interpretation: {t_test['interpretation']}")
                                
                                with col2:
                                    st.markdown("**Mann-Whitney U Test**")
                                    st.write(f"- p-value: {mw_test['p_value']:.4f}")
                                    st.write(f"- Significant: {'✅ Yes' if mw_test['significant'] else '❌ No'}")
                                    st.write(f"- Interpretation: {mw_test['interpretation']}")
                            else:
                                # New format (unpaired)
                                st.markdown("**T-Test Results**")
                                st.write(f"- p-value: {stats_analysis.get('p_value', 0):.4f}")
                                st.write(f"- Significant: {'✅ Yes' if stats_analysis.get('is_significant', False) else '❌ No'}")
                                if 'mann_whitney_p_value' in stats_analysis:
                                    st.write(f"- Mann-Whitney p-value: {stats_analysis['mann_whitney_p_value']:.4f}")
                        
                        # Effect Size
                        cohens_d = stats_analysis.get('cohens_d', 0)
                        effect_interpretation = stats_analysis.get('interpretation', {}).get('effect_size', 'N/A')
                        st.markdown("**Effect Size (Cohen's d)**")
                        st.write(f"- Cohen's d: {cohens_d:.3f}")
                        st.write(f"- Interpretation: {effect_interpretation}")
                        
                        # Visualization
                        st.markdown("---")
                        st.markdown("#### 📊 Visualizations")
                        
                        # Score distribution comparison
                        scores_a = [r['score_a'] for r in results]
                        scores_b = [r['score_b'] for r in results]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Box(
                            y=scores_a,
                            name=test['variant_a_name'],
                            boxmean='sd'
                        ))
                        fig.add_trace(go.Box(
                            y=scores_b,
                            name=test['variant_b_name'],
                            boxmean='sd'
                        ))
                        fig.update_layout(
                            title="Score Distribution Comparison",
                            yaxis_title="Score",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Win rate pie chart
                        fig2 = go.Figure(data=[go.Pie(
                            labels=[test['variant_a_name'], test['variant_b_name'], 'Ties'],
                            values=[test['variant_a_wins'], test['variant_b_wins'], test['ties']],
                            hole=0.3
                        )])
                        fig2.update_layout(
                            title="Win Rate Distribution",
                            height=400
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Detailed Results Table
                    st.markdown("---")
                    st.markdown("#### 📋 Detailed Results")
                    
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df[['question', 'score_a', 'score_b', 'winner']], use_container_width=True)
                    
                    # Export results
                    if st.button("📥 Export Results", key="export_ab_results"):
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"ab_test_{test['test_id']}.csv",
                            mime="text/csv",
                            key="download_ab_csv"
                        )
                else:
                    st.info("Test not completed yet. Run the test first to see results.")

