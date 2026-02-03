"""Router Evaluation UI page"""
import streamlit as st
import json
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_router_eval_page(evaluation_service: EvaluationService):
    """Render the Router Evaluation page"""
    # Import helper functions from backend services
    from backend.services.data_service import (
        save_router_evaluation,
        get_router_evaluations
    )
    # TODO: evaluate_router_decision is a complex wrapper - refactor to use EvaluationService directly
    from backend.services.evaluation_functions import evaluate_router_decision  # type: ignore
    
    st.header("🔀 Router Evaluation")
    st.markdown("Evaluate routing decisions and tool selection in AI agent systems.")
    
    eval_mode = st.radio(
        "Evaluation Mode:",
        ["Evaluate Router Decision", "View All Router Evaluations"],
        horizontal=True
    )
    
    if eval_mode == "Evaluate Router Decision":
        st.markdown("### 📝 Evaluate Tool Selection")
        
        # Query/Request
        query = st.text_area(
            "Query/Request *",
            height=100,
            placeholder="What task or request is the agent trying to accomplish?",
            key="router_query"
        )
        
        # Context (optional)
        context = st.text_area(
            "Context (optional)",
            height=80,
            placeholder="Additional context about the request or conversation history...",
            key="router_context"
        )
        
        # Available Tools
        st.markdown("### 🛠️ Available Tools")
        st.markdown("Add the tools/functions available to the router:")
        
        num_tools = st.number_input("Number of Tools", min_value=1, max_value=20, value=3, step=1, key="router_num_tools")
        
        available_tools = []
        for i in range(num_tools):
            with st.expander(f"Tool {i+1}", expanded=(i < 3)):
                tool_name = st.text_input(f"Tool Name *", key=f"router_tool_name_{i}", placeholder="e.g., search_database")
                tool_desc = st.text_area(
                    f"Tool Description *",
                    key=f"router_tool_desc_{i}",
                    height=80,
                    placeholder="Describe what this tool does..."
                )
                if tool_name and tool_desc:
                    available_tools.append({
                        "name": tool_name,
                        "description": tool_desc
                    })
        
        if available_tools:
            st.success(f"✅ {len(available_tools)} tool(s) configured")
        
        # Selected Tool
        st.markdown("### 🎯 Router Decision")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_tool = st.selectbox(
                "Selected Tool *",
                [""] + [tool["name"] for tool in available_tools],
                help="Which tool did the router select?",
                key="router_selected_tool"
            )
        
        with col2:
            expected_tool = st.selectbox(
                "Expected Tool (optional)",
                [""] + ["None"] + [tool["name"] for tool in available_tools],
                help="Which tool should have been selected? (for accuracy evaluation)",
                key="router_expected_tool"
            )
            if expected_tool == "None":
                expected_tool = None
        
        # Routing Strategy (optional)
        routing_strategy = st.text_input(
            "Routing Strategy (optional)",
            placeholder="e.g., semantic_similarity, rule_based, llm_router",
            key="router_strategy"
        )
        
        # Get available models from session state or sidebar
        available_models = st.session_state.get('available_models', ['llama3', 'mistral', 'gpt-oss-safeguard:20b'])
        model = st.selectbox("Judge Model", available_models, index=0 if available_models else None, key="router_judge_model")
        
        # Save to DB option
        save_enabled = st.checkbox("💾 Save to Database", value=True, key="save_router")
        
        # Initialize session state
        if 'router_eval_result' not in st.session_state:
            st.session_state.router_eval_result = None
        
        # Evaluate button
        if st.button("⚖️ Evaluate Router Decision", type="primary", use_container_width=True):
            if not query:
                st.error("Please provide a query/request")
            elif not available_tools:
                st.error("Please add at least one available tool")
            elif not selected_tool:
                st.error("Please select the tool that was chosen")
            elif not model:
                st.error("Please select a judge model")
            else:
                # Run evaluation synchronously with status updates
                with st.status("⚖️ Evaluating router decision...", expanded=True) as status:
                    status.write("📝 Analyzing routing decision...")
                    status.write("🔍 Evaluating tool selection...")
                    status.write("🧠 Assessing reasoning quality...")
                    try:
                        result = evaluate_router_decision(
                            query=query,
                            available_tools=available_tools,
                            selected_tool=selected_tool,
                            context=context if context else None,
                            expected_tool=expected_tool if expected_tool else None,
                            routing_strategy=routing_strategy if routing_strategy else None,
                            judge_model=model
                        )
                        status.update(label="✅ Router evaluation complete", state="complete")
                        st.session_state.router_eval_result = result
                    except Exception as e:
                        status.update(label="❌ Router evaluation failed", state="error")
                        st.session_state.router_eval_result = {"success": False, "error": str(e)}
                        st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.router_eval_result is not None:
            result = st.session_state.router_eval_result
            
            if result.get("success"):
                st.success("✅ Router evaluation completed!")
                
                # Display metrics
                st.markdown("### 📊 Evaluation Results")
                execution_time = result.get("execution_time", 0)
                if execution_time > 0:
                    st.caption(f"⏱️ Execution Time: {execution_time:.2f}s")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Tool Accuracy", f"{result['tool_accuracy_score']:.2f}/10")
                with col2:
                    st.metric("Routing Quality", f"{result['routing_quality_score']:.2f}/10")
                with col3:
                    st.metric("Reasoning Quality", f"{result['reasoning_score']:.2f}/10")
                with col4:
                    st.metric("Overall Score", f"{result['overall_score']:.2f}/10")
                
                # Display judgment
                st.markdown("### 📝 Detailed Judgment")
                st.markdown(result['judgment_text'])
                
                # Save to database if enabled
                if save_enabled:
                    try:
                        save_router_evaluation(
                            query=query,
                            available_tools=available_tools,
                            selected_tool=selected_tool,
                            tool_accuracy_score=result['tool_accuracy_score'],
                            routing_quality_score=result['routing_quality_score'],
                            reasoning_score=result['reasoning_score'],
                            overall_score=result['overall_score'],
                            judgment_text=result['judgment_text'],
                            metrics_json=json.dumps(result['metrics']),
                            trace_json=json.dumps(result['trace']),
                            evaluation_id=result['evaluation_id'],
                            context=context if context else None,
                            expected_tool=expected_tool if expected_tool else None,
                            routing_strategy=routing_strategy if routing_strategy else None
                        )
                        st.success(f"💾 Evaluation saved to database! (ID: {result['evaluation_id']})")
                    except Exception as e:
                        st.warning(f"Evaluation completed but failed to save: {str(e)}")
                
                # Show trace
                with st.expander("🔍 View Evaluation Trace"):
                    st.json(result['trace'])
                
                if st.button("🔄 New Evaluation", key="new_router_eval"):
                    st.session_state.router_eval_result = None
                    st.session_state.router_eval_running = False
                    st.rerun()
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                if st.button("🔄 Retry", key="retry_router_eval"):
                    st.session_state.router_eval_result = None
                    st.session_state.router_eval_running = False
                    st.rerun()
    
    else:  # View All Router Evaluations
        st.markdown("### 📋 All Router Evaluations")
        
        evaluations = get_router_evaluations(limit=100)
        
        if not evaluations:
            st.info("No router evaluations found. Create some evaluations first!")
        else:
            st.success(f"Found {len(evaluations)} router evaluation(s)")
            
            for eval_item in evaluations:
                with st.expander(f"🔀 Router Evaluation - {eval_item.get('query', 'N/A')[:50]}... - {eval_item.get('created_at', '')}", expanded=False):
                    col_info, col_metrics = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"**Query:** {eval_item.get('query', 'N/A')}")
                        if eval_item.get('context'):
                            st.write(f"**Context:** {eval_item.get('context', 'N/A')}")
                        st.write(f"**Selected Tool:** {eval_item.get('selected_tool', 'N/A')}")
                        if eval_item.get('expected_tool'):
                            st.write(f"**Expected Tool:** {eval_item.get('expected_tool', 'N/A')}")
                        if eval_item.get('routing_strategy'):
                            st.write(f"**Routing Strategy:** {eval_item.get('routing_strategy', 'N/A')}")
                        
                        # Show available tools
                        try:
                            tools = json.loads(eval_item.get('available_tools_json', '[]'))
                            st.write(f"**Available Tools:** {', '.join([t.get('name', 'Unknown') for t in tools])}")
                        except:
                            pass
                    
                    with col_metrics:
                        st.metric("Tool Accuracy", f"{eval_item.get('tool_accuracy_score', 0):.2f}/10")
                        st.metric("Routing Quality", f"{eval_item.get('routing_quality_score', 0):.2f}/10")
                        st.metric("Reasoning Quality", f"{eval_item.get('reasoning_score', 0):.2f}/10")
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

