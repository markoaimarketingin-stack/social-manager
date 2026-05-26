"""
Analytics and metrics ingestion layer.
Periodic metric collection, KPI computation, insights, dashboards, exports.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from statistics import mean, median

logger = logging.getLogger(__name__)


class MetricsIngestionService:
    """Collects and aggregates metrics from platforms."""
    
    def __init__(self):
        self.metric_snapshots: List[Dict] = []  # Time-series metric data
        self.platform_metrics: Dict[str, List] = {}  # By platform
        self.last_ingestion: Dict[str, datetime] = {}  # Last fetch per platform
    
    async def ingest_metrics(self, platform: str, post_id: str, metrics: Dict):
        """Record metric snapshot."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "platform": platform,
            "post_id": post_id,
            **metrics
        }
        
        self.metric_snapshots.append(snapshot)
        
        if platform not in self.platform_metrics:
            self.platform_metrics[platform] = []
        self.platform_metrics[platform].append(snapshot)
        
        self.last_ingestion[platform] = datetime.utcnow()
        logger.info(f"Ingested metrics for {platform} post {post_id}")
    
    def get_metrics_for_post(self, post_id: str) -> List[Dict]:
        """Get all metric snapshots for a post."""
        return [m for m in self.metric_snapshots if m["post_id"] == post_id]
    
    def get_metrics_for_platform(self, platform: str, hours: int = 24) -> List[Dict]:
        """Get recent metrics for a platform."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            m for m in self.platform_metrics.get(platform, [])
            if datetime.fromisoformat(m["timestamp"]) >= cutoff
        ]


class KPIComputer:
    """Computes key performance indicators."""
    
    @staticmethod
    def compute_engagement_rate(likes: int, comments: int, reach: int) -> float:
        """Calculate engagement rate %."""
        if reach == 0:
            return 0.0
        return ((likes + comments) / reach) * 100
    
    @staticmethod
    def compute_reach_per_follower(reach: int, follower_count: int) -> float:
        """Compute organic reach per 1000 followers."""
        if follower_count == 0:
            return 0.0
        return (reach / follower_count) * 1000
    
    @staticmethod
    def compute_click_through_rate(clicks: int, impressions: int) -> float:
        """Calculate CTR %."""
        if impressions == 0:
            return 0.0
        return (clicks / impressions) * 100
    
    @staticmethod
    def aggregate_metrics(metrics_list: List[Dict]) -> Dict:
        """Aggregate multiple metric snapshots."""
        if not metrics_list:
            return {}
        
        numeric_keys = ["likes", "comments", "shares", "reach", "impressions"]
        result = {}
        
        for key in numeric_keys:
            values = [m.get(key, 0) for m in metrics_list if key in m]
            if values:
                result[f"{key}_avg"] = mean(values)
                result[f"{key}_max"] = max(values)
                result[f"{key}_min"] = min(values)
                result[f"{key}_total"] = sum(values)
        
        return result
    
    @staticmethod
    def compute_campaign_kpis(posts_metrics: List[List[Dict]]) -> Dict:
        """Compute KPIs for entire campaign."""
        all_metrics = []
        for post_metrics in posts_metrics:
            all_metrics.extend(post_metrics)
        
        aggregated = KPIComputer.aggregate_metrics(all_metrics)
        
        return {
            **aggregated,
            "total_posts": len(posts_metrics),
            "total_engagement": aggregated.get("likes_total", 0) + aggregated.get("comments_total", 0),
            "average_engagement_rate": KPIComputer.compute_engagement_rate(
                int(aggregated.get("likes_total", 0)),
                int(aggregated.get("comments_total", 0)),
                int(aggregated.get("reach_total", 1))
            ),
        }


class InsightsEngine:
    """Generates actionable insights from metrics."""
    
    @staticmethod
    def get_top_performers(metrics_list: List[Dict], metric_key: str = "engagement_rate", top_n: int = 5) -> List[Dict]:
        """Get top performing posts."""
        sorted_metrics = sorted(metrics_list, key=lambda m: m.get(metric_key, 0), reverse=True)
        return sorted_metrics[:top_n]
    
    @staticmethod
    def get_trends(metrics_list: List[Dict], metric_key: str = "engagement_rate") -> Dict:
        """Compute trend for a metric (up/down/stable)."""
        if len(metrics_list) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics_list, key=lambda m: m.get("timestamp", ""))
        
        first_half = sorted_metrics[:len(sorted_metrics)//2]
        second_half = sorted_metrics[len(sorted_metrics)//2:]
        
        first_avg = mean([m.get(metric_key, 0) for m in first_half if metric_key in m])
        second_avg = mean([m.get(metric_key, 0) for m in second_half if metric_key in m])
        
        change_pct = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        if change_pct > 10:
            trend = "up"
        elif change_pct < -10:
            trend = "down"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percent": change_pct,
            "first_period_avg": first_avg,
            "second_period_avg": second_avg,
        }
    
    @staticmethod
    def recommend_next_actions(metrics: Dict, campaign_kpis: Dict) -> List[str]:
        """Generate recommendations based on performance."""
        recommendations = []
        
        engagement = campaign_kpis.get("average_engagement_rate", 0)
        if engagement < 1.0:
            recommendations.append("Engagement rate is low. Consider A/B testing different copy styles.")
        
        reach = campaign_kpis.get("reach_avg", 0)
        if reach < 1000:
            recommendations.append("Reach is limited. Try using more hashtags or posting at peak hours.")
        
        # More rules could be added
        
        if not recommendations:
            recommendations.append("Performance is strong! Continue current strategy.")
        
        return recommendations


class DashboardGenerator:
    """Generates dashboard data for UI visualization."""
    
    @staticmethod
    def generate_summary(campaign_id: int, metrics: Dict, kpis: Dict) -> Dict:
        """Generate dashboard summary."""
        return {
            "campaign_id": campaign_id,
            "generated_at": datetime.utcnow().isoformat(),
            "kpis": kpis,
            "top_metrics": {
                k: v for k, v in metrics.items() if "_total" in k or "_avg" in k
            },
            "recommendations": InsightsEngine.recommend_next_actions(metrics, kpis),
        }
    
    @staticmethod
    def generate_platform_comparison(platform_metrics: Dict[str, Dict]) -> Dict:
        """Compare performance across platforms."""
        comparison = {}
        for platform, metrics in platform_metrics.items():
            comparison[platform] = {
                "total_engagement": metrics.get("likes_total", 0) + metrics.get("comments_total", 0),
                "avg_engagement_rate": metrics.get("engagement_rate_avg", 0),
                "reach": metrics.get("reach_total", 0),
            }
        
        return comparison


class MetricsExporter:
    """Export metrics in various formats."""
    
    @staticmethod
    def export_to_csv(metrics_list: List[Dict]) -> str:
        """Export metrics to CSV format."""
        if not metrics_list:
            return ""
        
        import csv
        import io
        
        output = io.StringIO()
        keys = metrics_list[0].keys()
        writer = csv.DictWriter(output, fieldnames=keys)
        
        writer.writeheader()
        writer.writerows(metrics_list)
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(metrics_list: List[Dict]) -> str:
        """Export metrics to JSON."""
        import json
        return json.dumps(metrics_list, indent=2)


# Global instances
metrics_service = MetricsIngestionService()
kpi_computer = KPIComputer()
insights_engine = InsightsEngine()
dashboard_generator = DashboardGenerator()
metrics_exporter = MetricsExporter()

__all__ = [
    "MetricsIngestionService",
    "KPIComputer",
    "InsightsEngine",
    "DashboardGenerator",
    "MetricsExporter",
    "metrics_service",
    "kpi_computer",
    "insights_engine",
    "dashboard_generator",
    "metrics_exporter",
]
