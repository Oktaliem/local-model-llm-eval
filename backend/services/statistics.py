"""
Statistical analysis utilities for A/B testing.
Extracted from app.py to separate backend concerns.

Supports both paired and unpaired t-tests. Paired analysis provides 3-6× improvement
in statistical power by accounting for correlations between paired observations
(same questions evaluated by different models/variants).
"""
import numpy as np
from scipy import stats
from typing import List, Dict, Any, Optional


def calculate_statistical_significance(
    scores_a: List[float], 
    scores_b: List[float], 
    alpha: float = 0.05,
    paired: Optional[bool] = None
) -> Dict[str, Any]:
    """Calculate statistical significance between two groups of scores.
    
    Supports both paired and unpaired analysis. Paired analysis is automatically
    used when both groups have the same length (same questions evaluated by
    different models/variants). Paired analysis provides 3-6× improvement in
    statistical power by accounting for correlations between observations.
    
    Args:
        scores_a: List of scores for variant A
        scores_b: List of scores for variant B
        alpha: Significance level (default 0.05)
        paired: Whether to use paired analysis. If None, auto-detects based on
                equal lengths. True forces paired, False forces unpaired.
    
    Returns:
        Dictionary with statistical test results including:
        - test_type: "paired" or "unpaired"
        - paired_analysis: Paired test results (if applicable)
        - unpaired_analysis: Unpaired test results (for comparison)
        - All existing fields for backward compatibility
    
    Example:
        # Paired data (same questions, different models)
        scores_a = [8.0, 9.0, 7.0]  # Model A on questions 1, 2, 3
        scores_b = [6.0, 7.0, 5.5]  # Model B on questions 1, 2, 3
        result = calculate_statistical_significance(scores_a, scores_b)
        # Auto-detects paired and uses paired t-test
        
        # Unpaired data (different questions)
        scores_a = [8.0, 9.0, 7.0]  # Model A on questions 1, 2, 3
        scores_b = [6.5, 7.5]       # Model B on questions 4, 5
        result = calculate_statistical_significance(scores_a, scores_b)
        # Auto-detects unpaired and uses unpaired t-test
    """
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {
            "error": "Need at least 2 samples in each group for statistical testing",
            "valid": False
        }
    
    scores_a = np.array(scores_a)
    scores_b = np.array(scores_b)
    
    # Auto-detect paired data if not explicitly specified
    if paired is None:
        paired = (len(scores_a) == len(scores_b) and len(scores_a) >= 2)
    
    # Calculate both paired and unpaired for comparison
    unpaired_result = _calculate_unpaired_significance(scores_a, scores_b, alpha)
    
    if paired and len(scores_a) == len(scores_b):
        # Paired analysis (MORE POWERFUL)
        paired_result = _calculate_paired_significance(scores_a, scores_b, alpha)
        
        # Combine results
        result = unpaired_result.copy()  # Start with unpaired for backward compatibility
        result.update({
            "test_type": "paired",
            "paired_analysis": paired_result["paired_analysis"],
            "unpaired_analysis": {
                "t_statistic": unpaired_result["t_statistic"],
                "p_value": unpaired_result["p_value"],
                "standard_error": unpaired_result.get("standard_error"),
                "is_significant": unpaired_result["is_significant"]
            },
            "comparison": paired_result["comparison"],
            # Update main fields with paired results (more accurate)
            "t_statistic": paired_result["paired_analysis"]["t_statistic"],
            "p_value": paired_result["paired_analysis"]["p_value"],
            "is_significant": paired_result["paired_analysis"]["is_significant"],
            "confidence_interval": paired_result["paired_analysis"]["confidence_interval"],
            "interpretation": paired_result["interpretation"]
        })
        return result
    else:
        # Unpaired analysis (original method)
        result = unpaired_result.copy()
        result["test_type"] = "unpaired"
        return result


def _calculate_paired_significance(
    scores_a: np.ndarray, 
    scores_b: np.ndarray, 
    alpha: float
) -> Dict[str, Any]:
    """Calculate paired t-test significance.
    
    Paired analysis accounts for correlation between observations, providing
    significantly more statistical power when observations are paired (e.g.,
    same questions evaluated by different models).
    """
    # Paired differences
    differences = scores_a - scores_b
    
    # Basic statistics
    mean_a = np.mean(scores_a)
    mean_b = np.mean(scores_b)
    mean_diff = np.mean(differences)
    std_a = np.std(scores_a, ddof=1)
    std_b = np.std(scores_b, ddof=1)
    n = len(scores_a)
    
    # Paired variance: Var[A-B] = Var[differences]
    paired_var = np.var(differences, ddof=1)
    
    # Paired standard error
    paired_se = np.sqrt(paired_var / n) if n > 0 else 0
    
    # Paired t-test
    t_stat, p_value = stats.ttest_rel(scores_a, scores_b)
    
    # Correlation coefficient (shows how much pairing helps)
    if std_a > 0 and std_b > 0:
        correlation = np.corrcoef(scores_a, scores_b)[0, 1]
    else:
        correlation = 0.0
    
    # Paired confidence interval
    t_critical = stats.t.ppf(1 - alpha/2, n - 1) if n > 1 else 0
    ci_lower = mean_diff - t_critical * paired_se
    ci_upper = mean_diff + t_critical * paired_se
    
    # Effect size (Cohen's d for paired)
    # Use pooled std from individual groups for Cohen's d
    pooled_std = np.sqrt(((n - 1) * std_a**2 + (n - 1) * std_b**2) / (2 * (n - 1))) if n > 1 else 1.0
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
    
    # Win rate (for pairwise comparisons)
    wins_a = np.sum(scores_a > scores_b)
    wins_b = np.sum(scores_b > scores_a)
    ties = np.sum(scores_a == scores_b)
    
    win_rate_a = wins_a / n if n > 0 else 0
    win_rate_b = wins_b / n if n > 0 else 0
    
    # Determine significance
    is_significant = p_value < alpha
    
    # Calculate unpaired SE for comparison
    unpaired_se = np.sqrt(std_a**2 / n + std_b**2 / n) if n > 0 else 0
    power_improvement = unpaired_se / paired_se if paired_se > 0 else 1.0
    
    # Minimum detectable effect sizes
    z_critical = stats.norm.ppf(1 - alpha/2)
    mde_unpaired = z_critical * unpaired_se * 2  # Two-sided
    mde_paired = z_critical * paired_se * 2  # Two-sided
    
    return {
        "valid": True,
        "mean_a": float(mean_a),
        "mean_b": float(mean_b),
        "std_a": float(std_a),
        "std_b": float(std_b),
        "n_a": int(n),
        "n_b": int(n),
        "cohens_d": float(cohens_d),
        "alpha": float(alpha),
        "win_rate": {
            "variant_a": float(win_rate_a),
            "variant_b": float(win_rate_b),
            "ties": int(ties)
        },
        "paired_analysis": {
            "variance": float(paired_var),
            "standard_error": float(paired_se),
            "correlation": float(correlation),
            "mean_difference": float(mean_diff),
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "is_significant": bool(is_significant),
            "confidence_interval": {
                "lower": float(ci_lower),
                "upper": float(ci_upper),
                "level": float(1 - alpha)
            }
        },
        "comparison": {
            "unpaired_se": float(unpaired_se),
            "paired_se": float(paired_se),
            "power_improvement": f"{power_improvement:.2f}×",
            "se_reduction_percent": float((1 - paired_se / unpaired_se) * 100) if unpaired_se > 0 else 0.0,
            "minimum_detectable_effect_unpaired": float(mde_unpaired),
            "minimum_detectable_effect_paired": float(mde_paired),
            "mde_improvement_percent": float((1 - mde_paired / mde_unpaired) * 100) if mde_unpaired > 0 else 0.0
        },
        "interpretation": {
            "test_method": "paired t-test",
            "effect_size": "large" if abs(cohens_d) > 0.8 else "medium" if abs(cohens_d) > 0.5 else "small",
            "significance": "significant" if is_significant else "not significant",
            "practical_significance": "yes" if abs(cohens_d) > 0.5 and is_significant else "no",
            "correlation_benefit": (
                f"High correlation ({correlation:.2f}) indicates pairing is beneficial" 
                if abs(correlation) > 0.5 
                else f"Low correlation ({correlation:.2f}) - pairing provides limited benefit"
            ),
            "power_improvement": f"{power_improvement:.2f}× more powerful than unpaired test"
        }
    }


def _calculate_unpaired_significance(
    scores_a: np.ndarray, 
    scores_b: np.ndarray, 
    alpha: float
) -> Dict[str, Any]:
    """Calculate unpaired (independent samples) t-test significance.
    
    This is the original method, maintained for backward compatibility and
    for cases where data is not naturally paired.
    """
    # Basic statistics
    mean_a = np.mean(scores_a)
    mean_b = np.mean(scores_b)
    std_a = np.std(scores_a, ddof=1)
    std_b = np.std(scores_b, ddof=1)
    n_a = len(scores_a)
    n_b = len(scores_b)
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2)) if (n_a + n_b) > 2 else 1.0
    cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0
    
    # T-test (independent samples)
    t_stat, p_value = stats.ttest_ind(scores_a, scores_b)
    
    # Mann-Whitney U test (non-parametric alternative)
    u_stat, u_p_value = stats.mannwhitneyu(scores_a, scores_b, alternative='two-sided')
    
    # Confidence interval for difference in means
    se_diff = np.sqrt(std_a**2 / n_a + std_b**2 / n_b) if (n_a > 0 and n_b > 0) else 0
    t_critical = stats.t.ppf(1 - alpha/2, n_a + n_b - 2) if (n_a + n_b) > 2 else 0
    ci_lower = (mean_a - mean_b) - t_critical * se_diff
    ci_upper = (mean_a - mean_b) + t_critical * se_diff
    
    # Win rate (for pairwise comparisons)
    wins_a = 0
    wins_b = 0
    ties = 0
    
    min_len = min(len(scores_a), len(scores_b))
    for i in range(min_len):
        if scores_a[i] > scores_b[i]:
            wins_a += 1
        elif scores_b[i] > scores_a[i]:
            wins_b += 1
        else:
            ties += 1
    
    win_rate_a = wins_a / min_len if min_len > 0 else 0
    win_rate_b = wins_b / min_len if min_len > 0 else 0
    
    # Determine significance
    is_significant = p_value < alpha
    
    return {
        "valid": True,
        "mean_a": float(mean_a),
        "mean_b": float(mean_b),
        "std_a": float(std_a),
        "std_b": float(std_b),
        "n_a": int(n_a),
        "n_b": int(n_b),
        "cohens_d": float(cohens_d),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "is_significant": bool(is_significant),
        "alpha": float(alpha),
        "standard_error": float(se_diff),
        "mann_whitney_u": float(u_stat),
        "mann_whitney_p_value": float(u_p_value),
        "confidence_interval": {
            "lower": float(ci_lower),
            "upper": float(ci_upper),
            "level": float(1 - alpha)
        },
        "win_rate": {
            "variant_a": float(win_rate_a),
            "variant_b": float(win_rate_b),
            "ties": int(ties)
        },
        "interpretation": {
            "test_method": "unpaired t-test",
            "effect_size": "large" if abs(cohens_d) > 0.8 else "medium" if abs(cohens_d) > 0.5 else "small",
            "significance": "significant" if is_significant else "not significant",
            "practical_significance": "yes" if abs(cohens_d) > 0.5 and is_significant else "no"
        }
    }

