"""
A/B Testing Framework for optimizing post performance.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)


class TestStatus(str, Enum):
    """A/B test status."""
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class ABTestFramework:
    """Manage A/B testing for social content optimization."""
    
    def __init__(self):
        """Initialize A/B testing framework."""
        self.tests: Dict[int, Dict] = {}
        self.test_counter = 0
        self.min_sample_size = 100
        self.confidence_level = 0.95
    
    def create_test(
        self,
        name: str,
        variant_a: Dict,
        variant_b: Dict,
        metric: str = "engagement_rate",
        duration_days: int = 7,
        target_sample_size: int = 500
    ) -> Dict:
        """Create a new A/B test."""
        self.test_counter += 1
        test_id = self.test_counter
        
        test = {
            "id": test_id,
            "name": name,
            "status": TestStatus.PLANNED.value,
            "metric": metric,
            "variant_a": {
                **variant_a,
                "id": f"a_{test_id}",
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "engagement": 0,
                "data": []
            },
            "variant_b": {
                **variant_b,
                "id": f"b_{test_id}",
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "engagement": 0,
                "data": []
            },
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "ended_at": None,
            "target_sample_size": target_sample_size,
            "duration_days": duration_days,
            "winner": None,
            "confidence": 0.0,
            "statistical_significance": False,
            "analysis": {}
        }
        
        self.tests[test_id] = test
        return test
    
    def start_test(self, test_id: int) -> Dict:
        """Start a scheduled test."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        test["status"] = TestStatus.RUNNING.value
        test["started_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Test {test_id} started: {test['name']}")
        return {"success": True, "test_id": test_id}
    
    def record_impression(self, test_id: int, variant: str) -> Dict:
        """Record an impression for a test variant."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        variant_key = f"variant_{variant.lower()}"
        
        if variant_key not in test:
            return {"success": False, "error": "Invalid variant"}
        
        test[variant_key]["impressions"] += 1
        return {"success": True, "variant": variant}
    
    def record_click(self, test_id: int, variant: str) -> Dict:
        """Record a click for a test variant."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        variant_key = f"variant_{variant.lower()}"
        
        if variant_key not in test:
            return {"success": False, "error": "Invalid variant"}
        
        test[variant_key]["clicks"] += 1
        return {"success": True, "variant": variant}
    
    def record_conversion(self, test_id: int, variant: str, value: float = 1.0) -> Dict:
        """Record a conversion for a test variant."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        variant_key = f"variant_{variant.lower()}"
        
        if variant_key not in test:
            return {"success": False, "error": "Invalid variant"}
        
        test[variant_key]["conversions"] += value
        return {"success": True, "variant": variant}
    
    def record_engagement(self, test_id: int, variant: str, engagement_count: int = 1) -> Dict:
        """Record engagement (likes, comments, shares) for a variant."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        variant_key = f"variant_{variant.lower()}"
        
        if variant_key not in test:
            return {"success": False, "error": "Invalid variant"}
        
        test[variant_key]["engagement"] += engagement_count
        return {"success": True, "variant": variant, "engagement": engagement_count}
    
    def analyze_test(self, test_id: int) -> Dict:
        """Analyze test results and determine winner."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        variant_a = test["variant_a"]
        variant_b = test["variant_b"]
        
        # Calculate metrics
        metric = test["metric"]
        
        if metric == "engagement_rate":
            metric_a = variant_a["engagement"] / variant_a["impressions"] if variant_a["impressions"] > 0 else 0
            metric_b = variant_b["engagement"] / variant_b["impressions"] if variant_b["impressions"] > 0 else 0
        elif metric == "click_through_rate":
            metric_a = variant_a["clicks"] / variant_a["impressions"] if variant_a["impressions"] > 0 else 0
            metric_b = variant_b["clicks"] / variant_b["impressions"] if variant_b["impressions"] > 0 else 0
        elif metric == "conversion_rate":
            metric_a = variant_a["conversions"] / variant_a["clicks"] if variant_a["clicks"] > 0 else 0
            metric_b = variant_b["conversions"] / variant_b["clicks"] if variant_b["clicks"] > 0 else 0
        else:
            metric_a = 0
            metric_b = 0
        
        # Chi-square test for statistical significance
        is_significant, p_value = self._chi_square_test(variant_a, variant_b)
        
        # Determine winner
        winner = None
        confidence = 0.0
        
        if metric_a > metric_b:
            winner = "A"
            confidence = min(abs(metric_a - metric_b) / max(metric_b, 0.01), 1.0)
        elif metric_b > metric_a:
            winner = "B"
            confidence = min(abs(metric_b - metric_a) / max(metric_a, 0.01), 1.0)
        
        analysis = {
            "metric": metric,
            "variant_a_value": round(metric_a, 4),
            "variant_b_value": round(metric_b, 4),
            "improvement": round((metric_b - metric_a) / max(metric_a, 0.01) * 100, 2) if metric_a > 0 else 0,
            "sample_size_a": variant_a["impressions"],
            "sample_size_b": variant_b["impressions"],
            "p_value": round(p_value, 4),
            "statistically_significant": is_significant,
            "recommended_action": self._get_recommendation(winner, is_significant)
        }
        
        test["analysis"] = analysis
        test["winner"] = winner
        test["confidence"] = round(confidence, 2)
        test["statistical_significance"] = is_significant
        
        return {"success": True, "analysis": analysis, "winner": winner}
    
    def _chi_square_test(self, variant_a: Dict, variant_b: Dict) -> tuple:
        """Perform chi-square test for statistical significance."""
        # Simplified chi-square calculation
        conversions_a = max(variant_a["engagement"], 1)
        conversions_b = max(variant_b["engagement"], 1)
        total_a = max(variant_a["impressions"], 1)
        total_b = max(variant_b["impressions"], 1)
        
        expected_a = (conversions_a + conversions_b) / 2
        expected_b = (conversions_a + conversions_b) / 2
        
        chi_square = ((conversions_a - expected_a) ** 2 / expected_a) + ((conversions_b - expected_b) ** 2 / expected_b)
        
        # Simple p-value estimation (in production use scipy.stats)
        p_value = max(0.0001, min(1.0, 1 - (chi_square / 10)))
        is_significant = p_value < 0.05
        
        return is_significant, p_value
    
    def _get_recommendation(self, winner: Optional[str], is_significant: bool) -> str:
        """Get recommendation based on test results."""
        if not winner:
            return "No winner yet - continue testing"
        
        if is_significant:
            return f"Scale variant {winner} - statistically significant"
        else:
            return f"Variant {winner} leads but not statistically significant - continue testing"
    
    def end_test(self, test_id: int) -> Dict:
        """End a running test."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        test["status"] = TestStatus.COMPLETED.value
        test["ended_at"] = datetime.utcnow().isoformat()
        
        # Final analysis
        return self.analyze_test(test_id)
    
    def get_test_status(self, test_id: int) -> Dict:
        """Get current status of a test."""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        variant_a = test["variant_a"]
        variant_b = test["variant_b"]
        
        return {
            "success": True,
            "test_id": test_id,
            "name": test["name"],
            "status": test["status"],
            "variant_a": {
                "name": variant_a.get("name", "Variant A"),
                "impressions": variant_a["impressions"],
                "engagement": variant_a["engagement"],
                "engagement_rate": round(variant_a["engagement"] / variant_a["impressions"] * 100, 2) if variant_a["impressions"] > 0 else 0
            },
            "variant_b": {
                "name": variant_b.get("name", "Variant B"),
                "impressions": variant_b["impressions"],
                "engagement": variant_b["engagement"],
                "engagement_rate": round(variant_b["engagement"] / variant_b["impressions"] * 100, 2) if variant_b["impressions"] > 0 else 0
            },
            "winner": test["winner"],
            "confidence": test["confidence"]
        }


# Singleton instance
_ab_test_framework = None


def get_ab_test_framework() -> ABTestFramework:
    """Get or create A/B testing framework instance."""
    global _ab_test_framework
    if _ab_test_framework is None:
        _ab_test_framework = ABTestFramework()
    return _ab_test_framework
