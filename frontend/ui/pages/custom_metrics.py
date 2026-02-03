"""Custom Metrics UI page"""
import streamlit as st
import json
from core.services.evaluation_service import EvaluationService

def render_custom_metrics_page(evaluation_service: EvaluationService, model: str):
    """Render the Custom Metrics page"""
    # Import helper functions from backend services
    from backend.services.custom_metric_service import (
        get_all_custom_metrics,
        create_custom_metric,
        get_custom_metric,
        evaluate_with_custom_metric,
        delete_custom_metric
    )
    
    st.header("🎯 Custom Metrics")
    st.markdown("Create, manage, and use custom evaluation metrics with domain-specific criteria.")
    
    metric_mode = st.radio(
        "Select Mode",
        ["Browse Metrics", "Create New Metric", "Evaluate with Metric", "Manage Metrics"],
        horizontal=True,
        key="metric_mode"
    )
    
    if metric_mode == "Browse Metrics":
        st.markdown("### 📚 Custom Metrics Library")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_eval_type = st.selectbox(
                "Filter by Evaluation Type",
                ["All", "comprehensive", "code_evaluation", "router", "skills", "trajectory", "general"],
                key="filter_metric_eval_type"
            )
        with col2:
            filter_domain = st.selectbox(
                "Filter by Domain",
                ["All", "healthcare", "finance", "legal", "education", "software", "general", "other"],
                key="filter_metric_domain"
            )
        with col3:
            filter_active = st.selectbox(
                "Filter by Status",
                ["Active Only", "All", "Inactive Only"],
                key="filter_metric_active"
            )
        
        # Get metrics
        eval_type_filter = None if filter_eval_type == "All" else filter_eval_type
        domain_filter = None if filter_domain == "All" else filter_domain
        active_filter = True if filter_active == "Active Only" else (False if filter_active == "Inactive Only" else None)
        
        metrics = get_all_custom_metrics(
            evaluation_type=eval_type_filter,
            domain=domain_filter,
            is_active=active_filter
        )
        
        if not metrics:
            st.info("No custom metrics found. Create one in 'Create New Metric' mode.")
        else:
            st.success(f"Found {len(metrics)} metric(s)")
            
            for metric in metrics:
                status_badge = "✅ Active" if metric['is_active'] else "❌ Inactive"
                with st.expander(f"{status_badge} {metric['metric_name']} - {metric['evaluation_type']}"):
                    st.markdown(f"**Description:** {metric.get('metric_description', 'No description')}")
                    if metric.get('domain'):
                        st.markdown(f"**Domain:** {metric['domain']}")
                    st.markdown(f"**Evaluation Type:** {metric['evaluation_type']}")
                    st.markdown(f"**Scale:** {metric['scale_min']} - {metric['scale_max']}")
                    st.markdown(f"**Weight:** {metric.get('weight', 1.0)}")
                    st.markdown(f"**Usage Count:** {metric.get('usage_count', 0)}")
                    st.markdown(f"**Created:** {metric.get('created_at', 'N/A')}")
                    
                    st.markdown("**Metric Definition:**")
                    st.text_area("", value=metric['metric_definition'], height=100, disabled=True, key=f"def_{metric['metric_id']}")
                    
                    if metric.get('criteria_json'):
                        st.markdown("**Criteria:**")
                        st.json(metric['criteria_json'])
    
    elif metric_mode == "Create New Metric":
        st.markdown("### ✏️ Create New Custom Metric")
        
        metric_name = st.text_input("Metric Name", placeholder="e.g., Empathy Score", key="new_metric_name")
        metric_description = st.text_area("Description (Optional)", placeholder="Brief description of what this metric measures...", key="new_metric_desc")
        
        col1, col2 = st.columns(2)
        with col1:
            eval_type = st.selectbox(
                "Evaluation Type",
                ["comprehensive", "code_evaluation", "router", "skills", "trajectory", "general"],
                key="new_metric_eval_type"
            )
        with col2:
            domain = st.selectbox(
                "Domain (Optional)",
                ["None", "healthcare", "finance", "legal", "education", "software", "general", "other"],
                key="new_metric_domain"
            )
            domain = None if domain == "None" else domain
        
        st.markdown("### Metric Definition")
        st.info("Define what this metric measures and how it should be evaluated.")
        metric_definition = st.text_area(
            "Metric Definition",
            height=150,
            placeholder="""Example: This metric evaluates the level of empathy demonstrated in the response. 
Consider factors such as:
- Acknowledgment of emotional context
- Use of supportive language
- Understanding of the user's perspective
- Appropriate emotional tone""",
            key="new_metric_definition"
        )
        
        st.markdown("### Scoring Configuration")
        col1, col2, col3 = st.columns(3)
        with col1:
            scale_min = st.number_input("Minimum Score", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="new_metric_min")
        with col2:
            scale_max = st.number_input("Maximum Score", min_value=0.0, max_value=100.0, value=10.0, step=0.5, key="new_metric_max")
        with col3:
            weight = st.number_input("Weight", min_value=0.0, max_value=10.0, value=1.0, step=0.1, key="new_metric_weight")
        
        if scale_max <= scale_min:
            st.warning("⚠️ Maximum score must be greater than minimum score")
        
        st.markdown("### Criteria (Optional)")
        st.info("Add specific criteria as JSON for structured evaluation.")
        criteria_json_text = st.text_area(
            "Criteria JSON (Optional)",
            height=100,
            placeholder='{"criterion1": "description", "criterion2": "description"}',
            key="new_metric_criteria"
        )
        
        criteria_json = None
        if criteria_json_text:
            try:
                criteria_json = json.loads(criteria_json_text)
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your criteria JSON.")
                criteria_json = None
        
        scoring_function = st.text_area(
            "Scoring Function Description (Optional)",
            height=80,
            placeholder="Describe how the score should be calculated (e.g., 'Average of all criteria scores')",
            key="new_metric_scoring"
        )
        
        if st.button("💾 Create Metric", type="primary", key="create_metric_btn"):
            if not metric_name:
                st.error("Please provide a metric name")
            elif not metric_definition:
                st.error("Please provide a metric definition")
            elif scale_max <= scale_min:
                st.error("Maximum score must be greater than minimum score")
            else:
                metric_id = create_custom_metric(
                    metric_name=metric_name,
                    evaluation_type=eval_type,
                    metric_definition=metric_definition,
                    metric_description=metric_description,
                    domain=domain,
                    scoring_function=scoring_function if scoring_function else None,
                    criteria_json=criteria_json,
                    weight=weight,
                    scale_min=scale_min,
                    scale_max=scale_max,
                    created_by="user"
                )
                st.success(f"✅ Custom metric created! Metric ID: {metric_id}")
                st.info("You can now use this metric in evaluations.")
    
    elif metric_mode == "Evaluate with Metric":
        st.markdown("### 🎯 Evaluate Response with Custom Metric")
        
        # Get active metrics
        active_metrics = get_all_custom_metrics(is_active=True)
        
        if not active_metrics:
            st.warning("No active custom metrics found. Create one in 'Create New Metric' mode.")
        else:
            metric_options = {f"{m['metric_name']} ({m.get('domain', 'general')})": m['metric_id'] for m in active_metrics}
            selected_metric_name = st.selectbox(
                "Select Custom Metric",
                ["Select a metric..."] + list(metric_options.keys()),
                key="eval_metric_select"
            )
            
            if selected_metric_name != "Select a metric...":
                selected_metric_id = metric_options[selected_metric_name]
                metric = get_custom_metric(selected_metric_id)
                
                if metric:
                    st.info(f"📋 Using metric: {metric['metric_name']}")
                    if metric.get('metric_description'):
                        st.caption(metric['metric_description'])
                    
                    question = st.text_area(
                        "Question/Task:",
                        height=100,
                        placeholder="Enter the question or task...",
                        key="custom_metric_question"
                    )
                    
                    response = st.text_area(
                        "Response to Evaluate:",
                        height=200,
                        placeholder="Enter the response to evaluate...",
                        key="custom_metric_response"
                    )
                    
                    use_reference = st.checkbox("Use Reference Answer", key="custom_metric_use_ref")
                    reference = None
                    if use_reference:
                        reference = st.text_area(
                            "Reference Answer (Optional):",
                            height=150,
                            placeholder="Reference answer for comparison...",
                            key="custom_metric_reference"
                        )
                    
                    if st.button("🎯 Evaluate with Custom Metric", type="primary", key="run_custom_metric_btn"):
                        if not question or not response:
                            st.warning("Please fill in the question and response fields.")
                        else:
                            with st.status("🎯 Evaluating with custom metric...", expanded=True) as status:
                                st.write(f"Using metric: {metric['metric_name']}")
                                st.write("Sending evaluation request...")
                                result = evaluate_with_custom_metric(
                                    metric_id=selected_metric_id,
                                    question=question,
                                    response=response,
                                    reference=reference,
                                    judge_model=model
                                )
                                
                                if result.get("success"):
                                    st.write("✅ Evaluation complete!")
                                    status.update(label="✅ Evaluation Complete!", state="complete")
                                else:
                                    status.update(label="❌ Error occurred", state="error")
                            
                            if result.get("success"):
                                st.markdown("### 📊 Evaluation Results")
                                
                                execution_time = result.get("execution_time", 0)
                                if execution_time > 0:
                                    st.caption(f"⏱️ Execution Time: {execution_time:.2f}s")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Score", f"{result['score']:.2f}", f"Scale: {result['scale']['min']}-{result['scale']['max']}")
                                with col2:
                                    st.metric("Normalized Score", f"{result['normalized_score']:.2f}", "Normalized to 0-10")
                                
                                st.markdown("### 📝 Detailed Evaluation")
                                st.markdown(result['explanation'])
                                
                                st.markdown("### ℹ️ Metric Information")
                                st.json({
                                    "metric_id": result['metric_id'],
                                    "metric_name": result['metric_name'],
                                    "scale": result['scale']
                                })
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    else:  # Manage Metrics
        st.markdown("### ⚙️ Manage Custom Metrics")
        
        user_metrics = get_all_custom_metrics()
        
        if not user_metrics:
            st.info("No custom metrics found. Create one in 'Create New Metric' mode.")
        else:
            st.success(f"Found {len(user_metrics)} custom metric(s)")
            
            for metric in user_metrics:
                status_badge = "✅ Active" if metric['is_active'] else "❌ Inactive"
                with st.expander(f"{status_badge} {metric['metric_name']} - {metric['evaluation_type']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Description:** {metric.get('metric_description', 'No description')}")
                        st.markdown(f"**Domain:** {metric.get('domain', 'N/A')}")
                        st.markdown(f"**Scale:** {metric['scale_min']} - {metric['scale_max']}")
                        st.markdown(f"**Weight:** {metric.get('weight', 1.0)}")
                        st.markdown(f"**Usage Count:** {metric.get('usage_count', 0)}")
                        st.markdown(f"**Created:** {metric.get('created_at', 'N/A')}")
                    
                    with col2:
                        if metric['is_active']:
                            if st.button("🗑️ Deactivate", key=f"deactivate_{metric['metric_id']}", type="secondary"):
                                if delete_custom_metric(metric['metric_id']):
                                    st.success("Metric deactivated!")
                                    st.rerun()
                                else:
                                    st.error("Could not deactivate metric")
                        else:
                            st.info("Metric is inactive")
                    
                    st.markdown("**Metric Definition:**")
                    st.text_area("", value=metric['metric_definition'], height=100, disabled=True, key=f"manage_def_{metric['metric_id']}")
                    
                    if metric.get('criteria_json'):
                        st.markdown("**Criteria:**")
                        st.json(metric['criteria_json'])


