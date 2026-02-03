"""Trajectory Evaluation UI page"""
import streamlit as st
import json
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_trajectory_eval_page(evaluation_service: EvaluationService):
    """Render the Trajectory Evaluation page"""
    # Import helper functions from backend services
    from backend.services.data_service import (
        save_trajectory_evaluation,
        get_trajectory_evaluations
    )
    # TODO: evaluate_trajectory is a complex wrapper - refactor to use EvaluationService directly
    from backend.services.evaluation_functions import evaluate_trajectory  # type: ignore
    
    st.header("🛤️ Trajectory Evaluation")
    st.markdown("Evaluate multi-step action sequences, agent trajectories, and reasoning chains.")
    
    eval_mode = st.radio(
        "Select Mode",
        ["Evaluate Trajectory", "View All Trajectory Evaluations"],
        horizontal=True,
        key="trajectory_eval_mode"
    )
    
    if eval_mode == "Evaluate Trajectory":
        st.markdown("### 📝 Create New Trajectory Evaluation")
        
        # Task description
        task_description = st.text_area(
            "Task Description",
            placeholder="Describe the overall task or goal for this trajectory...",
            height=100,
            key="trajectory_task_description"
        )
        
        # Trajectory type
        trajectory_type = st.selectbox(
            "Trajectory Type (Optional)",
            ["", "action_sequence", "reasoning_chain", "planning_path", "tool_usage", "other"],
            help="Categorize the type of trajectory being evaluated",
            key="trajectory_type"
        )
        
        # Trajectory input
        st.markdown("#### Actual Trajectory")
        st.markdown("Enter the trajectory steps. Each step should have an 'action' and 'description' field.")
        
        trajectory_input_mode = st.radio(
            "Input Mode",
            ["JSON Format", "Manual Entry"],
            horizontal=True,
            key="trajectory_input_mode"
        )
        
        # Initialize trajectory in session state
        if 'trajectory_parsed' not in st.session_state:
            st.session_state.trajectory_parsed = []
        if 'expected_trajectory_parsed' not in st.session_state:
            st.session_state.expected_trajectory_parsed = []
        
        trajectory = []
        expected_trajectory = []
        
        if trajectory_input_mode == "JSON Format":
            trajectory_json = st.text_area(
                "Trajectory JSON",
                placeholder='[{"action": "step1", "description": "First step"}, {"action": "step2", "description": "Second step"}]',
                height=200,
                key="trajectory_json"
            )
            
            if trajectory_json:
                try:
                    parsed = json.loads(trajectory_json)
                    if not isinstance(parsed, list):
                        st.error("Trajectory must be a JSON array")
                        st.session_state.trajectory_parsed = []
                        trajectory = []
                    else:
                        st.session_state.trajectory_parsed = parsed
                        trajectory = parsed
                        st.success(f"✅ Parsed {len(trajectory)} steps")
                        with st.expander("Preview Trajectory"):
                            for i, step in enumerate(trajectory):
                                st.write(f"**Step {i+1}:** {step.get('action', 'N/A')} - {step.get('description', 'N/A')}")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")
                    st.session_state.trajectory_parsed = []
                    trajectory = []
            else:
                # Use previously parsed trajectory if JSON is empty but we have stored one
                trajectory = st.session_state.trajectory_parsed
        else:
            # Manual entry
            num_steps = st.number_input("Number of Steps", min_value=1, max_value=50, value=3, key="trajectory_num_steps")
            for i in range(num_steps):
                with st.expander(f"Step {i+1}", expanded=(i == 0)):
                    action = st.text_input(f"Action/Step Name", key=f"traj_action_{i}", placeholder=f"step_{i+1}")
                    description = st.text_area(f"Description/Reasoning", key=f"traj_desc_{i}", placeholder=f"Description of step {i+1}")
                    if action and description:
                        trajectory.append({"action": action, "description": description})
            # Store manually entered trajectory
            if trajectory:
                st.session_state.trajectory_parsed = trajectory
        
        # Expected trajectory (optional)
        st.markdown("#### Expected Trajectory (Optional)")
        include_expected = st.checkbox("Include Expected Trajectory for Comparison", value=False, key="trajectory_include_expected")
        
        if include_expected:
            expected_trajectory_json = st.text_area(
                "Expected Trajectory JSON",
                placeholder='[{"action": "expected_step1", "description": "Expected first step"}]',
                height=150,
                key="expected_trajectory_json"
            )
            
            if expected_trajectory_json:
                try:
                    parsed_expected = json.loads(expected_trajectory_json)
                    if not isinstance(parsed_expected, list):
                        st.error("Expected trajectory must be a JSON array")
                        st.session_state.expected_trajectory_parsed = []
                        expected_trajectory = []
                    else:
                        st.session_state.expected_trajectory_parsed = parsed_expected
                        expected_trajectory = parsed_expected
                        st.success(f"✅ Parsed {len(expected_trajectory)} expected steps")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")
                    st.session_state.expected_trajectory_parsed = []
                    expected_trajectory = []
            else:
                # Use previously parsed expected trajectory if JSON is empty but we have stored one
                expected_trajectory = st.session_state.expected_trajectory_parsed
        else:
            # Clear expected trajectory when checkbox is unchecked
            st.session_state.expected_trajectory_parsed = []
        
        # Get available models from session state or sidebar
        available_models = st.session_state.get('available_models', ['llama3', 'mistral', 'gpt-oss-safeguard:20b'])
        model = st.selectbox(
            "Judge Model",
            available_models,
            key="trajectory_judge_model"
        )
        
        # Save to DB option
        save_enabled = st.checkbox("💾 Save to Database", value=True, key="save_trajectory")
        
        # Initialize session state
        if 'trajectory_eval_result' not in st.session_state:
            st.session_state.trajectory_eval_result = None
        
        # Evaluate button - use stored trajectory from session state
        evaluate_trajectory_btn = st.button("⚖️ Evaluate Trajectory", type="primary", use_container_width=True)
        
        if evaluate_trajectory_btn:
            # Use stored trajectory from session state (ensures we have the parsed version)
            trajectory_to_use = st.session_state.trajectory_parsed if st.session_state.trajectory_parsed else trajectory
            expected_to_use = st.session_state.expected_trajectory_parsed if include_expected and st.session_state.expected_trajectory_parsed else (expected_trajectory if include_expected else None)
            
            if not task_description:
                st.warning("Please provide a task description.")
            elif not trajectory_to_use:
                st.warning("Please provide a trajectory to evaluate. Make sure the JSON is valid and parsed.")
            elif not model:
                st.warning("Please select a judge model.")
            else:
                with st.status("🛤️ Evaluating trajectory...", expanded=True) as status:
                    status.write("📝 Step 1/3: Analyzing trajectory steps...")
                    try:
                        result = evaluate_trajectory(
                            task_description=task_description,
                            trajectory=trajectory_to_use,
                            expected_trajectory=expected_to_use,
                            trajectory_type=trajectory_type if trajectory_type else None,
                            judge_model=model
                        )
                        status.write("✅ Step 2/3: Evaluating step quality and path efficiency...")
                        status.write("✅ Step 3/3: Assessing reasoning chain and planning quality...")
                        status.update(label="✅ Trajectory evaluation complete", state="complete")
                        st.session_state.trajectory_eval_result = result
                    except Exception as e:
                        status.update(label="❌ Trajectory evaluation failed", state="error")
                        st.session_state.trajectory_eval_result = {"success": False, "error": str(e)}
                        st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.trajectory_eval_result is not None:
            result = st.session_state.trajectory_eval_result
            
            if result.get("success"):
                st.success("✅ Trajectory evaluation completed!")
                
                # Display metrics
                execution_time = result.get("execution_time", 0)
                if execution_time > 0:
                    st.caption(f"⏱️ Execution Time: {execution_time:.2f}s")
                st.markdown("### 📊 Evaluation Results")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Step Quality", f"{result.get('step_quality_score', 0):.2f}/10")
                with col2:
                    st.metric("Path Efficiency", f"{result.get('path_efficiency_score', 0):.2f}/10")
                with col3:
                    st.metric("Reasoning Chain", f"{result.get('reasoning_chain_score', 0):.2f}/10")
                with col4:
                    st.metric("Planning Quality", f"{result.get('planning_quality_score', 0):.2f}/10")
                with col5:
                    st.metric("Overall Score", f"{result.get('overall_score', 0):.2f}/10")
                
                st.markdown("---")
                st.markdown("### 📝 Detailed Judgment")
                st.markdown(result.get('judgment_text', 'N/A'))
                
                # Show trace
                if result.get('trace'):
                    with st.expander("View Evaluation Trace"):
                        st.json(result.get('trace'))
                
                # Save to database
                if save_enabled:
                    try:
                        # Use stored trajectory from session state
                        trajectory_to_save = st.session_state.trajectory_parsed if st.session_state.trajectory_parsed else trajectory
                        expected_to_save = st.session_state.expected_trajectory_parsed if include_expected and st.session_state.expected_trajectory_parsed else (expected_trajectory if include_expected else None)
                        
                        save_trajectory_evaluation(
                            task_description=task_description,
                            trajectory=trajectory_to_save,
                            step_quality_score=result.get('step_quality_score', 0),
                            path_efficiency_score=result.get('path_efficiency_score', 0),
                            reasoning_chain_score=result.get('reasoning_chain_score', 0),
                            planning_quality_score=result.get('planning_quality_score', 0),
                            overall_score=result.get('overall_score', 0),
                            judgment_text=result.get('judgment_text', ''),
                            metrics_json=json.dumps(result.get('metrics', {})),
                            trace_json=json.dumps(result.get('trace', {})),
                            evaluation_id=result.get('evaluation_id'),
                            expected_trajectory=expected_to_save,
                            trajectory_type=trajectory_type if trajectory_type else None
                        )
                        st.success(f"💾 Evaluation saved to database! (ID: {result.get('evaluation_id')})")
                    except Exception as e:
                        st.warning(f"Evaluation completed but failed to save: {str(e)}")
                
                if st.button("🔄 New Evaluation", key="new_trajectory_eval"):
                    st.session_state.trajectory_eval_result = None
                    st.rerun()
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                if st.button("🔄 Retry", key="retry_trajectory_eval"):
                    st.session_state.trajectory_eval_result = None
                    st.rerun()
    
    else:  # View All Trajectory Evaluations
        st.markdown("### 📋 All Trajectory Evaluations")
        
        # Filter by trajectory type
        filter_type = st.selectbox(
            "Filter by Trajectory Type",
            ["All"] + ["action_sequence", "reasoning_chain", "planning_path", "tool_usage", "other"],
            key="trajectory_filter_type"
        )
        
        trajectory_type_filter = filter_type if filter_type != "All" else None
        
        # Get evaluations
        evaluations = get_trajectory_evaluations(limit=100, trajectory_type=trajectory_type_filter)
        
        if not evaluations:
            st.info("No trajectory evaluations found. Create one using the 'Evaluate Trajectory' mode.")
        else:
            st.info(f"Found {len(evaluations)} trajectory evaluation(s)")
            
            for eval_item in evaluations:
                with st.container():
                    col_task, col_metrics = st.columns([2, 3])
                    
                    with col_task:
                        st.markdown(f"**Evaluation ID:** `{eval_item.get('evaluation_id', 'N/A')}`")
                        st.write(f"**Task:** {eval_item.get('task_description', 'N/A')}")
                        if eval_item.get('trajectory_type'):
                            st.write(f"**Type:** {eval_item.get('trajectory_type', 'N/A')}")
                        
                        # Show trajectory preview
                        try:
                            trajectory_data = json.loads(eval_item.get('trajectory_json', '[]'))
                            st.write(f"**Steps:** {len(trajectory_data)}")
                            with st.expander("View Trajectory"):
                                for i, step in enumerate(trajectory_data):
                                    st.write(f"**Step {i+1}:** {step.get('action', 'N/A')} - {step.get('description', 'N/A')}")
                        except:
                            pass
                        
                        if eval_item.get('expected_trajectory_json'):
                            with st.expander("View Expected Trajectory"):
                                try:
                                    expected_data = json.loads(eval_item.get('expected_trajectory_json', '[]'))
                                    for i, step in enumerate(expected_data):
                                        st.write(f"**Step {i+1}:** {step.get('action', 'N/A')} - {step.get('description', 'N/A')}")
                                except:
                                    pass
                    
                    with col_metrics:
                        st.metric("Step Quality", f"{eval_item.get('step_quality_score', 0):.2f}/10")
                        st.metric("Path Efficiency", f"{eval_item.get('path_efficiency_score', 0):.2f}/10")
                        st.metric("Reasoning Chain", f"{eval_item.get('reasoning_chain_score', 0):.2f}/10")
                        st.metric("Planning Quality", f"{eval_item.get('planning_quality_score', 0):.2f}/10")
                        st.metric("Overall Score", f"{eval_item.get('overall_score', 0):.2f}/10")
                    
                    st.markdown("---")
                    st.markdown("**Judgment:**")
                    st.markdown(eval_item.get('judgment_text', 'N/A'))
                    
                    # Show metrics if available
                    if eval_item.get('metrics_json'):
                        with st.expander("View Detailed Metrics"):
                            try:
                                metrics = json.loads(eval_item.get('metrics_json', '{}'))
                                st.json(metrics)
                            except:
                                pass
                    
                    # Show trace if available
                    if eval_item.get('trace_json'):
                        with st.expander("View Evaluation Trace"):
                            try:
                                trace = json.loads(eval_item.get('trace_json', '{}'))
                                st.json(trace)
                            except:
                                pass

