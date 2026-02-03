"""Advanced Analytics UI page"""
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.services.evaluation_service import EvaluationService
from typing import Optional, List, Dict, Any

def render_analytics_page(evaluation_service: EvaluationService):
    """Render the Advanced Analytics page"""
    # Import helper functions from backend services
    from backend.services.data_service import get_all_evaluation_data
    from backend.services.analytics_service import (
        calculate_aggregate_statistics,
        prepare_time_series_data
    )
    
    st.header("📈 Advanced Analytics & Visualization")
    st.markdown("Comprehensive analytics and visualizations for all evaluation data.")
    
    # Load data
    with st.spinner("Loading evaluation data..."):
        all_data = get_all_evaluation_data(limit=5000)
        stats = calculate_aggregate_statistics(all_data)
    
    # Overview metrics
    st.markdown("### 📊 Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_evaluations = (
        len(all_data["comprehensive"]) + 
        len(all_data["code_evaluations"]) + 
        len(all_data["router_evaluations"]) + 
        len(all_data["skills_evaluations"]) + 
        len(all_data["trajectory_evaluations"])
    )
    
    with col1:
        st.metric("Total Evaluations", total_evaluations)
    with col2:
        st.metric("Comprehensive", len(all_data["comprehensive"]))
    with col3:
        st.metric("Code Evaluations", len(all_data["code_evaluations"]))
    with col4:
        st.metric("Router Evaluations", len(all_data["router_evaluations"]))
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("Skills Evaluations", len(all_data["skills_evaluations"]))
    with col6:
        st.metric("Trajectory Evaluations", len(all_data["trajectory_evaluations"]))
    
    st.markdown("---")
    
    # Analytics sections
    analytics_section = st.selectbox(
        "Select Analytics View",
        [
            "Time Series Analysis",
            "Comparative Analytics",
            "Aggregate Statistics",
            "Performance Heatmaps",
            "Model Comparison",
            "Export Data"
        ],
        key="analytics_section"
    )
    
    if analytics_section == "Time Series Analysis":
        st.markdown("### 📈 Time Series Analysis")
        
        eval_type = st.selectbox(
            "Select Evaluation Type",
            ["comprehensive", "code_evaluations", "router_evaluations", "skills_evaluations", "trajectory_evaluations"],
            key="time_series_type"
        )
        
        df = prepare_time_series_data(all_data, eval_type)
        
        if not df.empty and "created_at" in df.columns and "overall_score" in df.columns:
            # Time series chart
            fig = px.line(
                df, 
                x="created_at", 
                y="overall_score",
                title=f"{eval_type.replace('_', ' ').title()} - Overall Score Over Time",
                labels={"created_at": "Date", "overall_score": "Overall Score"},
                markers=True
            )
            fig.update_traces(line_color="#1f77b4", line_width=2)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Rolling average
            if len(df) > 1:
                df["rolling_avg"] = df["overall_score"].rolling(window=min(7, len(df)), center=True).mean()
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=df["created_at"],
                    y=df["overall_score"],
                    mode="markers",
                    name="Individual Scores",
                    marker=dict(size=6, opacity=0.6)
                ))
                fig2.add_trace(go.Scatter(
                    x=df["created_at"],
                    y=df["rolling_avg"],
                    mode="lines",
                    name="7-Day Rolling Average",
                    line=dict(width=3, color="red")
                ))
                fig2.update_layout(
                    title=f"{eval_type.replace('_', ' ').title()} - Scores with Rolling Average",
                    xaxis_title="Date",
                    yaxis_title="Score",
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info(f"No time series data available for {eval_type}")
    
    elif analytics_section == "Comparative Analytics":
        st.markdown("### 🔀 Comparative Analytics")
        
        # Compare evaluation types
        eval_types_to_compare = st.multiselect(
            "Select Evaluation Types to Compare",
            ["comprehensive", "code_evaluations", "router_evaluations", "skills_evaluations", "trajectory_evaluations"],
            default=["comprehensive", "code_evaluations"],
            key="compare_types"
        )
        
        if eval_types_to_compare:
            comparison_data = []
            for eval_type in eval_types_to_compare:
                df = prepare_time_series_data(all_data, eval_type)
                if not df.empty and "overall_score" in df.columns:
                    comparison_data.append({
                        "type": eval_type.replace("_", " ").title(),
                        "avg_score": df["overall_score"].mean(),
                        "count": len(df),
                        "min_score": df["overall_score"].min(),
                        "max_score": df["overall_score"].max(),
                        "std_score": df["overall_score"].std()
                    })
            
            if comparison_data:
                comp_df = pd.DataFrame(comparison_data)
                
                # Bar chart
                fig = px.bar(
                    comp_df,
                    x="type",
                    y="avg_score",
                    title="Average Overall Score by Evaluation Type",
                    labels={"type": "Evaluation Type", "avg_score": "Average Score"},
                    color="avg_score",
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Comparison table
                st.dataframe(comp_df, use_container_width=True)
    
    elif analytics_section == "Aggregate Statistics":
        st.markdown("### 📊 Aggregate Statistics")
        
        if stats:
            # Comprehensive stats
            if "comprehensive" in stats:
                st.markdown("#### 🎯 Comprehensive Evaluation Statistics")
                comp_stats = stats["comprehensive"]
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("Count", comp_stats.get("count", 0))
                with col2:
                    st.metric("Avg Overall", f"{comp_stats.get('overall_avg', 0):.2f}")
                with col3:
                    st.metric("Avg Accuracy", f"{comp_stats.get('accuracy_avg', 0):.2f}")
                with col4:
                    st.metric("Avg Relevance", f"{comp_stats.get('relevance_avg', 0):.2f}")
                with col5:
                    st.metric("Avg Coherence", f"{comp_stats.get('coherence_avg', 0):.2f}")
                with col6:
                    st.metric("Avg Hallucination", f"{comp_stats.get('hallucination_avg', 0):.2f}")
                
                if comp_stats.get("by_model"):
                    st.markdown("**By Model:**")
                    model_df = pd.DataFrame(list(comp_stats["by_model"].items()), columns=["Model", "Avg Score"])
                    st.dataframe(model_df, use_container_width=True)
            
            # Code evaluation stats
            if "code_evaluations" in stats:
                st.markdown("#### 💻 Code Evaluation Statistics")
                code_stats = stats["code_evaluations"]
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Count", code_stats.get("count", 0))
                with col2:
                    st.metric("Avg Overall", f"{code_stats.get('overall_avg', 0):.2f}")
                with col3:
                    st.metric("Syntax Success", f"{code_stats.get('syntax_success_rate', 0):.1f}%")
                with col4:
                    st.metric("Execution Success", f"{code_stats.get('execution_success_rate', 0):.1f}%")
                with col5:
                    st.metric("Avg Maintainability", f"{code_stats.get('maintainability_avg', 0):.2f}")
            
            # Router evaluation stats
            if "router_evaluations" in stats:
                st.markdown("#### 🔀 Router Evaluation Statistics")
                router_stats = stats["router_evaluations"]
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Count", router_stats.get("count", 0))
                with col2:
                    st.metric("Avg Overall", f"{router_stats.get('overall_avg', 0):.2f}")
                with col3:
                    st.metric("Tool Accuracy", f"{router_stats.get('tool_accuracy_avg', 0):.2f}")
                with col4:
                    st.metric("Routing Quality", f"{router_stats.get('routing_quality_avg', 0):.2f}")
                with col5:
                    st.metric("Reasoning", f"{router_stats.get('reasoning_avg', 0):.2f}")
            
            # Skills evaluation stats
            if "skills_evaluations" in stats:
                st.markdown("#### 🎓 Skills Evaluation Statistics")
                skills_stats = stats["skills_evaluations"]
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("Count", skills_stats.get("count", 0))
                with col2:
                    st.metric("Avg Overall", f"{skills_stats.get('overall_avg', 0):.2f}")
                with col3:
                    st.metric("Correctness", f"{skills_stats.get('correctness_avg', 0):.2f}")
                with col4:
                    st.metric("Completeness", f"{skills_stats.get('completeness_avg', 0):.2f}")
                with col5:
                    st.metric("Clarity", f"{skills_stats.get('clarity_avg', 0):.2f}")
                with col6:
                    st.metric("Proficiency", f"{skills_stats.get('proficiency_avg', 0):.2f}")
                
                if skills_stats.get("by_skill_type"):
                    st.markdown("**By Skill Type:**")
                    skill_df = pd.DataFrame(list(skills_stats["by_skill_type"].items()), columns=["Skill Type", "Avg Score"])
                    fig = px.bar(skill_df, x="Skill Type", y="Avg Score", title="Average Score by Skill Type")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Trajectory evaluation stats
            if "trajectory_evaluations" in stats:
                st.markdown("#### 🛤️ Trajectory Evaluation Statistics")
                traj_stats = stats["trajectory_evaluations"]
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("Count", traj_stats.get("count", 0))
                with col2:
                    st.metric("Avg Overall", f"{traj_stats.get('overall_avg', 0):.2f}")
                with col3:
                    st.metric("Step Quality", f"{traj_stats.get('step_quality_avg', 0):.2f}")
                with col4:
                    st.metric("Path Efficiency", f"{traj_stats.get('path_efficiency_avg', 0):.2f}")
                with col5:
                    st.metric("Reasoning Chain", f"{traj_stats.get('reasoning_chain_avg', 0):.2f}")
                with col6:
                    st.metric("Planning Quality", f"{traj_stats.get('planning_quality_avg', 0):.2f}")
                
                if traj_stats.get("by_trajectory_type"):
                    st.markdown("**By Trajectory Type:**")
                    traj_df = pd.DataFrame(list(traj_stats["by_trajectory_type"].items()), columns=["Trajectory Type", "Avg Score"])
                    fig = px.bar(traj_df, x="Trajectory Type", y="Avg Score", title="Average Score by Trajectory Type")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No statistics available. Create some evaluations first!")
    
    elif analytics_section == "Performance Heatmaps":
        st.markdown("### 🔥 Performance Heatmaps")
        
        eval_type = st.selectbox(
            "Select Evaluation Type",
            ["comprehensive", "skills_evaluations", "trajectory_evaluations"],
            key="heatmap_type"
        )
        
        if eval_type == "comprehensive" and all_data["comprehensive"]:
            df = pd.DataFrame(all_data["comprehensive"])
            if not df.empty:
                metrics = ["accuracy", "relevance", "coherence", "hallucination", "toxicity"]
                heatmap_data = df[metrics].mean().values.reshape(1, -1)
                
                fig = go.Figure(data=go.Heatmap(
                    z=heatmap_data,
                    x=metrics,
                    y=["Average"],
                    colorscale="Viridis",
                    text=heatmap_data,
                    texttemplate="%{text:.2f}",
                    textfont={"size": 12}
                ))
                fig.update_layout(
                    title="Comprehensive Evaluation Metrics Heatmap",
                    height=200
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif eval_type == "skills_evaluations" and all_data["skills_evaluations"]:
            df = pd.DataFrame(all_data["skills_evaluations"])
            if not df.empty and "skill_type" in df.columns:
                metrics = ["correctness", "completeness", "clarity", "proficiency"]
                pivot_data = []
                for skill in df["skill_type"].unique():
                    skill_df = df[df["skill_type"] == skill]
                    pivot_data.append([skill_df[m].mean() if m in skill_df.columns else 0 for m in metrics])
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_data,
                    x=metrics,
                    y=df["skill_type"].unique(),
                    colorscale="Viridis",
                    text=pivot_data,
                    texttemplate="%{text:.2f}",
                    textfont={"size": 10}
                ))
                fig.update_layout(
                    title="Skills Evaluation Metrics Heatmap by Skill Type",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif eval_type == "trajectory_evaluations" and all_data["trajectory_evaluations"]:
            df = pd.DataFrame(all_data["trajectory_evaluations"])
            if not df.empty and "trajectory_type" in df.columns:
                metrics = ["step_quality", "path_efficiency", "reasoning_chain", "planning_quality"]
                pivot_data = []
                for traj_type in df["trajectory_type"].unique():
                    traj_df = df[df["trajectory_type"] == traj_type]
                    pivot_data.append([traj_df[m].mean() if m in traj_df.columns else 0 for m in metrics])
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_data,
                    x=metrics,
                    y=df["trajectory_type"].unique(),
                    colorscale="Viridis",
                    text=pivot_data,
                    texttemplate="%{text:.2f}",
                    textfont={"size": 10}
                ))
                fig.update_layout(
                    title="Trajectory Evaluation Metrics Heatmap by Type",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
    
    elif analytics_section == "Model Comparison":
        st.markdown("### 🤖 Model Comparison")
        
        if all_data["comprehensive"]:
            df = pd.DataFrame(all_data["comprehensive"])
            if "judge_model" in df.columns and "overall_score" in df.columns:
                model_comparison = df.groupby("judge_model")["overall_score"].agg(["mean", "count", "std"]).reset_index()
                model_comparison.columns = ["Model", "Avg Score", "Count", "Std Dev"]
                
                # Bar chart
                fig = px.bar(
                    model_comparison,
                    x="Model",
                    y="Avg Score",
                    error_y="Std Dev",
                    title="Model Performance Comparison",
                    labels={"Model": "Judge Model", "Avg Score": "Average Overall Score"},
                    color="Avg Score",
                    color_continuous_scale="RdYlGn"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                st.dataframe(model_comparison, use_container_width=True)
            else:
                st.info("No model comparison data available")
        else:
            st.info("No comprehensive evaluations available for model comparison")
    
    elif analytics_section == "Export Data":
        st.markdown("### 📥 Export Data")
        
        export_format = st.selectbox(
            "Select Export Format",
            ["CSV", "JSON"],
            key="export_format"
        )
        
        export_type = st.selectbox(
            "Select Data to Export",
            ["All Data", "Comprehensive", "Code Evaluations", "Router Evaluations", "Skills Evaluations", "Trajectory Evaluations", "Statistics"],
            key="export_type"
        )
        
        if st.button("📥 Export", type="primary", key="export_button"):
            if export_format == "CSV":
                if export_type == "All Data":
                    # Combine all data
                    all_dfs = []
                    if all_data["comprehensive"]:
                        all_dfs.append(("Comprehensive", pd.DataFrame(all_data["comprehensive"])))
                    if all_data["code_evaluations"]:
                        all_dfs.append(("Code", pd.DataFrame(all_data["code_evaluations"])))
                    if all_data["router_evaluations"]:
                        all_dfs.append(("Router", pd.DataFrame(all_data["router_evaluations"])))
                    if all_data["skills_evaluations"]:
                        all_dfs.append(("Skills", pd.DataFrame(all_data["skills_evaluations"])))
                    if all_data["trajectory_evaluations"]:
                        all_dfs.append(("Trajectory", pd.DataFrame(all_data["trajectory_evaluations"])))
                    
                    if all_dfs:
                        csv_data = "\n\n".join([f"=== {name} ===\n{df.to_csv(index=False)}" for name, df in all_dfs])
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"all_evaluations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key="download_csv_all"
                        )
                elif export_type == "Comprehensive" and all_data["comprehensive"]:
                    df = pd.DataFrame(all_data["comprehensive"])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"comprehensive_evaluations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_csv_comp"
                    )
                elif export_type == "Statistics":
                    stats_json = json.dumps(stats, indent=2, default=str)
                    st.download_button(
                        label="Download Statistics (JSON)",
                        data=stats_json,
                        file_name=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_stats_json"
                    )
            else:  # JSON
                if export_type == "All Data":
                    json_data = json.dumps(all_data, indent=2, default=str)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"all_evaluations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_json_all"
                    )
                elif export_type == "Statistics":
                    stats_json = json.dumps(stats, indent=2, default=str)
                    st.download_button(
                        label="Download Statistics",
                        data=stats_json,
                        file_name=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_stats_json2"
                    )

