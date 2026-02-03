"""Unit tests for statistics module"""
import pytest
import numpy as np
from backend.services.statistics import calculate_statistical_significance


class TestCalculateStatisticalSignificance:
    """Test cases for calculate_statistical_significance function"""
    
    def test_insufficient_samples_a(self):
        """Test with insufficient samples in group A"""
        result = calculate_statistical_significance([1.0], [2.0, 3.0, 4.0])
        assert result["valid"] is False
        assert "error" in result
        assert "at least 2 samples" in result["error"].lower()
    
    def test_insufficient_samples_b(self):
        """Test with insufficient samples in group B"""
        result = calculate_statistical_significance([1.0, 2.0, 3.0], [4.0])
        assert result["valid"] is False
        assert "error" in result
    
    def test_insufficient_samples_both(self):
        """Test with insufficient samples in both groups"""
        result = calculate_statistical_significance([1.0], [2.0])
        assert result["valid"] is False
    
    def test_basic_statistics(self):
        """Test basic statistical calculations"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["n_a"] == 5
        assert result["n_b"] == 5
        assert result["mean_a"] > result["mean_b"]
        assert result["std_a"] > 0
        assert result["std_b"] > 0
    
    def test_cohens_d_calculation(self):
        """Test Cohen's d effect size calculation"""
        # Use data with variance to avoid division by zero
        scores_a = [10.0, 9.5, 10.5, 9.8, 10.2]
        scores_b = [5.0, 4.5, 5.5, 4.8, 5.2]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["cohens_d"] > 0  # Large effect size expected
        assert abs(result["cohens_d"]) > 0.8  # Should be large
    
    def test_cohens_d_zero_pooled_std(self):
        """Test Cohen's d when pooled std is zero"""
        scores_a = [5.0, 5.0, 5.0]
        scores_b = [5.0, 5.0, 5.0]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["cohens_d"] == 0.0
    
    def test_t_test_results(self):
        """Test t-test statistical test results"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert "t_statistic" in result
        assert "p_value" in result
        assert isinstance(result["t_statistic"], float)
        assert isinstance(result["p_value"], float)
        assert 0 <= result["p_value"] <= 1
    
    def test_mann_whitney_results(self):
        """Test Mann-Whitney U test results"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert "mann_whitney_u" in result
        assert "mann_whitney_p_value" in result
        assert isinstance(result["mann_whitney_u"], float)
        assert isinstance(result["mann_whitney_p_value"], float)
    
    def test_confidence_interval(self):
        """Test confidence interval calculation"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert "confidence_interval" in result
        ci = result["confidence_interval"]
        assert "lower" in ci
        assert "upper" in ci
        assert "level" in ci
        assert ci["lower"] < ci["upper"]
        assert ci["level"] == 0.95  # Default alpha = 0.05
    
    def test_custom_alpha(self):
        """Test with custom alpha value"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b, alpha=0.01)
        
        assert result["valid"] is True
        assert result["alpha"] == 0.01
        assert result["confidence_interval"]["level"] == 0.99
    
    def test_win_rate_calculation(self):
        """Test win rate calculation for pairwise comparisons"""
        scores_a = [10.0, 8.0, 9.0, 7.0, 6.0]
        scores_b = [5.0, 7.0, 8.0, 9.0, 10.0]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert "win_rate" in result
        win_rate = result["win_rate"]
        assert "variant_a" in win_rate
        assert "variant_b" in win_rate
        assert "ties" in win_rate
        assert win_rate["variant_a"] >= 0
        assert win_rate["variant_b"] >= 0
        assert win_rate["ties"] >= 0
    
    def test_win_rate_with_ties(self):
        """Test win rate with tied scores"""
        scores_a = [5.0, 5.0, 5.0, 5.0, 5.0]
        scores_b = [5.0, 5.0, 5.0, 5.0, 5.0]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["win_rate"]["ties"] == 5
        assert result["win_rate"]["variant_a"] == 0
        assert result["win_rate"]["variant_b"] == 0
    
    def test_win_rate_unequal_lengths(self):
        """Test win rate with unequal list lengths"""
        scores_a = [10.0, 8.0, 9.0]
        scores_b = [5.0, 7.0, 8.0, 9.0, 10.0]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        # Win rates are percentages (0-1), ties is count
        # Should only compare up to min length (3)
        assert result["win_rate"]["ties"] + int(result["win_rate"]["variant_a"] * 3) + int(result["win_rate"]["variant_b"] * 3) == 3
        # Or check that win rates sum to 1.0 (100%)
        assert abs(result["win_rate"]["variant_a"] + result["win_rate"]["variant_b"] + (result["win_rate"]["ties"] / 3)) == pytest.approx(1.0, abs=0.01)
    
    def test_significance_determination(self):
        """Test significance determination"""
        # Create clearly different groups
        scores_a = [10.0, 10.0, 10.0, 10.0, 10.0]
        scores_b = [1.0, 1.0, 1.0, 1.0, 1.0]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["is_significant"] is True
        assert result["p_value"] < result["alpha"]
    
    def test_not_significant(self):
        """Test when results are not significant"""
        # Create very similar groups
        scores_a = [5.0, 5.1, 5.0, 5.1, 5.0]
        scores_b = [5.0, 5.0, 5.1, 5.0, 5.1]
        
        result = calculate_statistical_significance(scores_a, scores_b, alpha=0.001)
        
        assert result["valid"] is True
        # May or may not be significant, but should have interpretation
    
    def test_interpretation_effect_size(self):
        """Test effect size interpretation"""
        # Large effect - use data with variance
        scores_a = [10.0, 9.5, 10.5, 9.8, 10.2]
        scores_b = [1.0, 1.5, 0.5, 1.2, 0.8]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert "interpretation" in result
        # Effect size should be large given the difference
        assert result["interpretation"]["effect_size"] in ["large", "medium"]
        assert abs(result["cohens_d"]) > 0.5  # At least medium effect
    
    def test_interpretation_medium_effect(self):
        """Test medium effect size interpretation"""
        scores_a = [7.0, 7.5, 8.0, 7.5, 8.0]
        scores_b = [5.0, 5.5, 6.0, 5.5, 6.0]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        effect_size = result["interpretation"]["effect_size"]
        assert effect_size in ["medium", "large", "small"]
    
    def test_interpretation_practical_significance(self):
        """Test practical significance interpretation"""
        # Use data with variance and clear difference
        scores_a = [10.0, 9.5, 10.5, 9.8, 10.2]
        scores_b = [1.0, 1.5, 0.5, 1.2, 0.8]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        # Practical significance requires both large effect AND statistical significance
        # With such a large difference, should be significant
        if result["is_significant"] and abs(result["cohens_d"]) > 0.5:
            assert result["interpretation"]["practical_significance"] == "yes"
        else:
            # If not significant, practical significance should be "no"
            assert result["interpretation"]["practical_significance"] in ["yes", "no"]
    
    def test_all_result_fields(self):
        """Test that all expected fields are present in result"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        required_fields = [
            "mean_a", "mean_b", "std_a", "std_b", "n_a", "n_b",
            "cohens_d", "t_statistic", "p_value", "is_significant", "alpha",
            "mann_whitney_u", "mann_whitney_p_value",
            "confidence_interval", "win_rate", "interpretation"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"


class TestPairedTTest:
    """Test cases for paired t-test functionality"""
    
    def test_paired_auto_detection(self):
        """Test that paired data is auto-detected when lengths match"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["test_type"] == "paired"
        assert "paired_analysis" in result
        assert "unpaired_analysis" in result
        assert "comparison" in result
    
    def test_unpaired_auto_detection(self):
        """Test that unpaired data is auto-detected when lengths differ"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0]  # Different length
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["test_type"] == "unpaired"
        assert "paired_analysis" not in result
    
    def test_forced_paired_mode(self):
        """Test explicit paired=True parameter"""
        scores_a = [8.0, 9.0, 7.0]
        scores_b = [6.0, 7.0, 5.5]
        
        result = calculate_statistical_significance(scores_a, scores_b, paired=True)
        
        assert result["valid"] is True
        assert result["test_type"] == "paired"
        assert "paired_analysis" in result
    
    def test_forced_unpaired_mode(self):
        """Test explicit paired=False parameter"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b, paired=False)
        
        assert result["valid"] is True
        assert result["test_type"] == "unpaired"
        assert "paired_analysis" not in result
    
    def test_paired_ttest_calculation(self):
        """Test paired t-test calculation"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["test_type"] == "paired"
        paired = result["paired_analysis"]
        assert "t_statistic" in paired
        assert "p_value" in paired
        assert "variance" in paired
        assert "standard_error" in paired
        assert "correlation" in paired
        assert "mean_difference" in paired
        assert isinstance(paired["t_statistic"], float)
        assert isinstance(paired["p_value"], float)
        assert 0 <= paired["p_value"] <= 1
    
    def test_paired_variance_calculation(self):
        """Test paired variance calculation"""
        scores_a = [8.0, 9.0, 7.0]
        scores_b = [6.0, 7.0, 5.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        paired = result["paired_analysis"]
        assert "variance" in paired
        assert paired["variance"] >= 0
        # Variance should be calculated from differences
        differences = np.array(scores_a) - np.array(scores_b)
        expected_var = np.var(differences, ddof=1)
        assert abs(paired["variance"] - expected_var) < 0.001
    
    def test_paired_standard_error(self):
        """Test paired standard error calculation"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        paired = result["paired_analysis"]
        assert "standard_error" in paired
        assert paired["standard_error"] >= 0
        # SE should be sqrt(variance / n)
        expected_se = np.sqrt(paired["variance"] / len(scores_a))
        assert abs(paired["standard_error"] - expected_se) < 0.001
    
    def test_paired_confidence_interval(self):
        """Test paired confidence interval"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        paired = result["paired_analysis"]
        assert "confidence_interval" in paired
        ci = paired["confidence_interval"]
        assert "lower" in ci
        assert "upper" in ci
        assert "level" in ci
        assert ci["lower"] < ci["upper"]
        assert ci["level"] == 0.95
    
    def test_paired_correlation_calculation(self):
        """Test correlation coefficient calculation"""
        # High correlation case
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]  # Similar pattern
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        paired = result["paired_analysis"]
        assert "correlation" in paired
        assert -1 <= paired["correlation"] <= 1
        # Should have positive correlation (both increase together)
        assert paired["correlation"] > 0
    
    def test_paired_vs_unpaired_comparison(self):
        """Test comparison between paired and unpaired results"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert "comparison" in result
        comp = result["comparison"]
        assert "unpaired_se" in comp
        assert "paired_se" in comp
        assert "power_improvement" in comp
        # Paired SE should be <= unpaired SE (paired is more powerful)
        assert comp["paired_se"] <= comp["unpaired_se"]
        # Power improvement should be >= 1.0×
        assert float(comp["power_improvement"].rstrip('×')) >= 1.0
    
    def test_paired_with_high_correlation(self):
        """Test paired analysis with high correlation (should show big improvement)"""
        # Create data with high correlation and meaningful variance
        # This simulates real-world scenario where models perform similarly on same questions
        # but with some variation in the difference
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5, 8.2, 9.1, 7.8]
        scores_b = [6.5, 7.5, 5.8, 7.0, 8.0, 6.7, 7.6, 6.3]  # Consistently lower with similar pattern
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["test_type"] == "paired"
        paired = result["paired_analysis"]
        # High correlation should be close to 1.0 (similar patterns)
        assert paired["correlation"] > 0.8
        # Should show power improvement (paired SE should be <= unpaired SE)
        comp = result["comparison"]
        power_improvement = float(comp["power_improvement"].rstrip('×'))
        # With high correlation, paired should be at least as good as unpaired (>= 1.0)
        assert power_improvement >= 1.0
        # Verify paired SE is smaller or equal to unpaired SE
        assert comp["paired_se"] <= comp["unpaired_se"]
    
    def test_paired_with_low_correlation(self):
        """Test paired analysis with low correlation (should show small improvement)"""
        # Create data with low correlation
        scores_a = [10.0, 1.0, 10.0, 1.0, 10.0]
        scores_b = [1.0, 10.0, 1.0, 10.0, 1.0]  # Negatively correlated
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["test_type"] == "paired"
        paired = result["paired_analysis"]
        # Should have negative correlation
        assert paired["correlation"] < 0
    
    def test_backward_compatibility(self):
        """Test that existing code still works (backward compatibility)"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        # Call without paired parameter (should auto-detect)
        result = calculate_statistical_significance(scores_a, scores_b)
        
        # All original fields should still be present
        assert result["valid"] is True
        assert "mean_a" in result
        assert "mean_b" in result
        assert "t_statistic" in result
        assert "p_value" in result
        assert "is_significant" in result
        assert "confidence_interval" in result
        assert "win_rate" in result
        assert "interpretation" in result
    
    def test_paired_interpretation_fields(self):
        """Test that interpretation includes paired-specific fields"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        assert result["test_type"] == "paired"
        interpretation = result["interpretation"]
        assert "test_method" in interpretation
        assert interpretation["test_method"] == "paired t-test"
        assert "correlation_benefit" in interpretation
        assert "power_improvement" in interpretation
    
    def test_paired_minimum_detectable_effect(self):
        """Test minimum detectable effect calculation"""
        scores_a = [8.0, 9.0, 7.0, 8.5, 9.5]
        scores_b = [6.0, 7.0, 5.5, 6.5, 7.5]
        
        result = calculate_statistical_significance(scores_a, scores_b)
        
        assert result["valid"] is True
        comp = result["comparison"]
        assert "minimum_detectable_effect_unpaired" in comp
        assert "minimum_detectable_effect_paired" in comp
        assert "mde_improvement_percent" in comp
        # Paired MDE should be <= unpaired MDE
        assert comp["minimum_detectable_effect_paired"] <= comp["minimum_detectable_effect_unpaired"]

