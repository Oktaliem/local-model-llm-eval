"""Evaluation Templates UI page"""
import streamlit as st
from core.services.evaluation_service import EvaluationService

def render_templates_page(evaluation_service: EvaluationService):
    """Render the Evaluation Templates page"""
    # Import helper functions from backend services
    from backend.services.template_service import (
        get_all_evaluation_templates,
        create_evaluation_template,
        delete_evaluation_template
    )
    
    st.header("📋 Evaluation Templates")
    st.markdown("Create, manage, and apply reusable evaluation configurations.")
    
    template_mode = st.radio(
        "Select Mode",
        ["Browse Templates", "Create New Template", "Manage Templates"],
        horizontal=True,
        key="template_mode"
    )
    
    if template_mode == "Browse Templates":
        st.markdown("### 📚 Template Library")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_eval_type = st.selectbox(
                "Filter by Evaluation Type",
                ["All", "comprehensive", "code_evaluation", "router", "skills", "trajectory"],
                key="filter_eval_type"
            )
        with col2:
            filter_industry = st.selectbox(
                "Filter by Industry",
                ["All", "healthcare", "finance", "legal", "education", "software", "general"],
                key="filter_industry"
            )
        
        # Get templates
        eval_type_filter = None if filter_eval_type == "All" else filter_eval_type
        industry_filter = None if filter_industry == "All" else filter_industry
        
        templates = get_all_evaluation_templates(
            evaluation_type=eval_type_filter,
            industry=industry_filter,
            include_predefined=True
        )
        
        if not templates:
            st.info("No templates found. Create one or check filters.")
        else:
            st.success(f"Found {len(templates)} template(s)")
            
            for template in templates:
                with st.expander(f"{'⭐' if template['is_predefined'] else '📝'} {template['template_name']} - {template['evaluation_type']}"):
                    st.markdown(f"**Description:** {template.get('template_description', 'No description')}")
                    if template.get('industry'):
                        st.markdown(f"**Industry:** {template['industry']}")
                    st.markdown(f"**Evaluation Type:** {template['evaluation_type']}")
                    st.markdown(f"**Usage Count:** {template.get('usage_count', 0)}")
                    st.markdown(f"**Created:** {template.get('created_at', 'N/A')}")
                    
                    if st.button(f"View Configuration", key=f"view_{template['template_id']}"):
                        st.json(template['template_config'])
                    
                    if template['is_predefined']:
                        st.info("⭐ This is a predefined template and cannot be deleted.")
    
    elif template_mode == "Create New Template":
        st.markdown("### ✏️ Create New Evaluation Template")
        
        template_name = st.text_input("Template Name", placeholder="e.g., My Custom Template", key="new_template_name")
        template_description = st.text_area("Description (Optional)", placeholder="Describe what this template is for...", key="new_template_desc")
        
        col1, col2 = st.columns(2)
        with col1:
            eval_type = st.selectbox(
                "Evaluation Type",
                ["comprehensive", "code_evaluation", "router", "skills", "trajectory"],
                key="new_template_eval_type"
            )
        with col2:
            industry = st.selectbox(
                "Industry (Optional)",
                ["None", "healthcare", "finance", "legal", "education", "software", "general", "other"],
                key="new_template_industry"
            )
            industry = None if industry == "None" else industry
        
        st.markdown("### Template Configuration")
        st.info("Configure the template settings below. The configuration will be applied when using this template.")
        
        if eval_type == "comprehensive":
            st.markdown("#### Metric Weights (must sum to 1.0)")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                acc_weight = st.number_input("Accuracy Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="acc_w")
            with col2:
                rel_weight = st.number_input("Relevance Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="rel_w")
            with col3:
                coh_weight = st.number_input("Coherence Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="coh_w")
            with col4:
                hall_weight = st.number_input("Hallucination Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="hall_w")
            
            total_weight = acc_weight + rel_weight + coh_weight + hall_weight
            if abs(total_weight - 1.0) > 0.01:
                st.warning(f"⚠️ Weights sum to {total_weight:.2f}. They should sum to 1.0")
            
            task_type = st.selectbox(
                "Task Type",
                ["general", "technical", "creative", "analytical"],
                key="new_template_task_type"
            )
            
            system_prompt = st.text_area(
                "Custom System Prompt (Optional)",
                placeholder="Custom prompt for the judge model...",
                key="new_template_system_prompt"
            )
            
            template_config = {
                "metrics": {
                    "accuracy": {"weight": acc_weight},
                    "relevance": {"weight": rel_weight},
                    "coherence": {"weight": coh_weight},
                    "hallucination": {"weight": hall_weight}
                },
                "task_type": task_type
            }
            
            if system_prompt:
                template_config["prompt_modifiers"] = {
                    "system_prompt": system_prompt
                }
        
        elif eval_type == "code_evaluation":
            st.markdown("#### Quality Weights (must sum to 1.0)")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                syntax_weight = st.number_input("Syntax Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="syntax_w")
            with col2:
                exec_weight = st.number_input("Execution Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="exec_w")
            with col3:
                maint_weight = st.number_input("Maintainability Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="maint_w")
            with col4:
                read_weight = st.number_input("Readability Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="read_w")
            
            total_weight = syntax_weight + exec_weight + maint_weight + read_weight
            if abs(total_weight - 1.0) > 0.01:
                st.warning(f"⚠️ Weights sum to {total_weight:.2f}. They should sum to 1.0")
            
            strict_mode = st.checkbox("Strict Mode", key="new_template_strict")
            check_security = st.checkbox("Check Security", key="new_template_security")
            check_performance = st.checkbox("Check Performance", key="new_template_perf")
            
            template_config = {
                "quality_weights": {
                    "syntax": syntax_weight,
                    "execution": exec_weight,
                    "maintainability": maint_weight,
                    "readability": read_weight
                },
                "strict_mode": strict_mode,
                "check_security": check_security,
                "check_performance": check_performance
            }
        else:
            st.info(f"Template configuration for {eval_type} will be added in future updates.")
            template_config = {}
        
        if st.button("💾 Create Template", type="primary", key="create_template_btn"):
            if not template_name:
                st.error("Please provide a template name")
            elif eval_type == "comprehensive" and abs(total_weight - 1.0) > 0.01:
                st.error("Metric weights must sum to 1.0")
            elif eval_type == "code_evaluation" and abs(total_weight - 1.0) > 0.01:
                st.error("Quality weights must sum to 1.0")
            else:
                template_id = create_evaluation_template(
                    template_name=template_name,
                    evaluation_type=eval_type,
                    template_config=template_config,
                    template_description=template_description,
                    industry=industry,
                    created_by="user"
                )
                st.success(f"✅ Template created! Template ID: {template_id}")
                st.info("You can now use this template in evaluations.")
    
    else:  # Manage Templates
        st.markdown("### ⚙️ Manage Templates")
        
        user_templates = get_all_evaluation_templates(include_predefined=False)
        
        if not user_templates:
            st.info("No custom templates found. Create one in 'Create New Template' mode.")
        else:
            st.success(f"Found {len(user_templates)} custom template(s)")
            
            for template in user_templates:
                with st.expander(f"📝 {template['template_name']} - {template['evaluation_type']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Description:** {template.get('template_description', 'No description')}")
                        st.markdown(f"**Industry:** {template.get('industry', 'N/A')}")
                        st.markdown(f"**Usage Count:** {template.get('usage_count', 0)}")
                        st.markdown(f"**Created:** {template.get('created_at', 'N/A')}")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{template['template_id']}", type="secondary"):
                            if delete_evaluation_template(template['template_id']):
                                st.success("Template deleted!")
                                st.rerun()
                            else:
                                st.error("Could not delete template")
                    
                    if st.button(f"View Configuration", key=f"view_config_{template['template_id']}"):
                        st.json(template['template_config'])

