"""
Analytics service for calculating aggregate statistics.
Extracted from app.py to separate backend concerns.
"""
import pandas as pd
from typing import Dict, Any


def calculate_aggregate_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate aggregate statistics from evaluation data."""
    stats = {}
    
    # Comprehensive evaluation stats
    if data["comprehensive"]:
        comp_df = pd.DataFrame(data["comprehensive"])
        stats["comprehensive"] = {
            "count": len(comp_df),
            "overall_avg": comp_df["overall_score"].mean() if "overall_score" in comp_df.columns else 0,
            "accuracy_avg": comp_df["accuracy"].mean() if "accuracy" in comp_df.columns else 0,
            "relevance_avg": comp_df["relevance"].mean() if "relevance" in comp_df.columns else 0,
            "coherence_avg": comp_df["coherence"].mean() if "coherence" in comp_df.columns else 0,
            "hallucination_avg": comp_df["hallucination"].mean() if "hallucination" in comp_df.columns else 0,
            "toxicity_avg": comp_df["toxicity"].mean() if "toxicity" in comp_df.columns else 0,
            "by_model": comp_df.groupby("judge_model")["overall_score"].mean().to_dict() if "judge_model" in comp_df.columns else {}
        }
    
    # Code evaluation stats
    if data["code_evaluations"]:
        code_df = pd.DataFrame(data["code_evaluations"])
        stats["code_evaluations"] = {
            "count": len(code_df),
            "overall_avg": code_df["overall_score"].mean() if "overall_score" in code_df.columns else 0,
            "syntax_success_rate": (code_df["syntax_valid"].sum() / len(code_df) * 100) if "syntax_valid" in code_df.columns else 0,
            "execution_success_rate": (code_df["execution_success"].sum() / len(code_df) * 100) if "execution_success" in code_df.columns else 0,
            "maintainability_avg": code_df["maintainability"].mean() if "maintainability" in code_df.columns else 0,
            "readability_avg": code_df["readability"].mean() if "readability" in code_df.columns else 0
        }
    
    # Router evaluation stats
    if data["router_evaluations"]:
        router_df = pd.DataFrame(data["router_evaluations"])
        stats["router_evaluations"] = {
            "count": len(router_df),
            "overall_avg": router_df["overall_score"].mean() if "overall_score" in router_df.columns else 0,
            "tool_accuracy_avg": router_df["tool_accuracy"].mean() if "tool_accuracy" in router_df.columns else 0,
            "routing_quality_avg": router_df["routing_quality"].mean() if "routing_quality" in router_df.columns else 0,
            "reasoning_avg": router_df["reasoning"].mean() if "reasoning" in router_df.columns else 0
        }
    
    # Skills evaluation stats
    if data["skills_evaluations"]:
        skills_df = pd.DataFrame(data["skills_evaluations"])
        stats["skills_evaluations"] = {
            "count": len(skills_df),
            "overall_avg": skills_df["overall_score"].mean() if "overall_score" in skills_df.columns else 0,
            "by_skill_type": skills_df.groupby("skill_type")["overall_score"].mean().to_dict() if "skill_type" in skills_df.columns else {},
            "correctness_avg": skills_df["correctness"].mean() if "correctness" in skills_df.columns else 0,
            "completeness_avg": skills_df["completeness"].mean() if "completeness" in skills_df.columns else 0,
            "clarity_avg": skills_df["clarity"].mean() if "clarity" in skills_df.columns else 0,
            "proficiency_avg": skills_df["proficiency"].mean() if "proficiency" in skills_df.columns else 0
        }
    
    # Trajectory evaluation stats
    if data["trajectory_evaluations"]:
        traj_df = pd.DataFrame(data["trajectory_evaluations"])
        stats["trajectory_evaluations"] = {
            "count": len(traj_df),
            "overall_avg": traj_df["overall_score"].mean() if "overall_score" in traj_df.columns else 0,
            "by_trajectory_type": traj_df.groupby("trajectory_type")["overall_score"].mean().to_dict() if "trajectory_type" in traj_df.columns else {},
            "step_quality_avg": traj_df["step_quality"].mean() if "step_quality" in traj_df.columns else 0,
            "path_efficiency_avg": traj_df["path_efficiency"].mean() if "path_efficiency" in traj_df.columns else 0,
            "reasoning_chain_avg": traj_df["reasoning_chain"].mean() if "reasoning_chain" in traj_df.columns else 0,
            "planning_quality_avg": traj_df["planning_quality"].mean() if "planning_quality" in traj_df.columns else 0
        }
    
    return stats


def prepare_time_series_data(data: Dict[str, Any], evaluation_type: str = "comprehensive") -> pd.DataFrame:
    """Prepare time series data for a specific evaluation type."""
    if evaluation_type == "comprehensive" and data["comprehensive"]:
        df = pd.DataFrame(data["comprehensive"])
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.sort_values("created_at")
        return df
    elif evaluation_type == "code_evaluations" and data["code_evaluations"]:
        df = pd.DataFrame(data["code_evaluations"])
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.sort_values("created_at")
        return df
    elif evaluation_type == "router_evaluations" and data["router_evaluations"]:
        df = pd.DataFrame(data["router_evaluations"])
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.sort_values("created_at")
        return df
    elif evaluation_type == "skills_evaluations" and data["skills_evaluations"]:
        df = pd.DataFrame(data["skills_evaluations"])
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.sort_values("created_at")
        return df
    elif evaluation_type == "trajectory_evaluations" and data["trajectory_evaluations"]:
        df = pd.DataFrame(data["trajectory_evaluations"])
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.sort_values("created_at")
        return df
    return pd.DataFrame()

