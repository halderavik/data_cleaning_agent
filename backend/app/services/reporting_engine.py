from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from app.models.issue import Issue
from app.models.rule import Rule
from app.models.comment import Comment

class ReportingEngine:
    """Service for generating comprehensive reports and analytics."""
    
    def __init__(self, db: Session):
        self.db = db

    def generate_quality_scorecard(self, project_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive data quality scorecard.
        
        Args:
            project_id: The project ID to generate the scorecard for
            start_date: Optional start date for the reporting period
            end_date: Optional end date for the reporting period
            
        Returns:
            Dict containing scorecard metrics and details
        """
        # Get issues within date range
        query = self.db.query(Issue).filter(Issue.project_id == project_id)
        if start_date:
            query = query.filter(Issue.created_at >= start_date)
        if end_date:
            query = query.filter(Issue.created_at <= end_date)
        
        issues = query.all()
        
        # Calculate metrics
        total_issues = len(issues)
        severity_counts = self._count_by_severity(issues)
        category_distribution = self._get_category_distribution(issues)
        resolution_stats = self._get_resolution_stats(issues)
        
        # Calculate quality score (0-100)
        quality_score = self._calculate_quality_score(issues)
        
        return {
            "quality_score": quality_score,
            "total_issues": total_issues,
            "severity_distribution": severity_counts,
            "category_distribution": category_distribution,
            "resolution_stats": resolution_stats,
            "period": {
                "start": start_date,
                "end": end_date
            }
        }

    def generate_trend_report(self, project_id: str, metric: str, interval: str = "daily", days: int = 30) -> Dict[str, Any]:
        """
        Generate trend analysis for specified metric.
        
        Args:
            project_id: The project ID
            metric: The metric to analyze (e.g., "issues", "quality_score")
            interval: Time interval for grouping ("daily", "weekly", "monthly")
            days: Number of days to analyze
            
        Returns:
            Dict containing trend data and analysis
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get issues within date range
        issues = self.db.query(Issue).filter(
            Issue.project_id == project_id,
            Issue.created_at >= start_date,
            Issue.created_at <= end_date
        ).all()
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'date': issue.created_at,
            'severity': issue.severity,
            'category': issue.category,
            'status': issue.status
        } for issue in issues])
        
        # Group by time interval
        if interval == "daily":
            df['period'] = df['date'].dt.date
        elif interval == "weekly":
            df['period'] = df['date'].dt.isocalendar().week
        else:  # monthly
            df['period'] = df['date'].dt.to_period('M')
        
        # Calculate trends
        trends = self._calculate_trends(df, metric)
        
        return {
            "metric": metric,
            "interval": interval,
            "trends": trends,
            "period": {
                "start": start_date,
                "end": end_date
            }
        }

    def generate_custom_report(self, project_id: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a custom report based on specified template.
        
        Args:
            project_id: The project ID
            template: Report template specifying metrics and visualizations
            
        Returns:
            Dict containing custom report data
        """
        report_data = {}
        
        for section in template.get("sections", []):
            section_type = section.get("type")
            if section_type == "scorecard":
                report_data[section["name"]] = self.generate_quality_scorecard(
                    project_id,
                    section.get("start_date"),
                    section.get("end_date")
                )
            elif section_type == "trend":
                report_data[section["name"]] = self.generate_trend_report(
                    project_id,
                    section["metric"],
                    section.get("interval", "daily"),
                    section.get("days", 30)
                )
            elif section_type == "distribution":
                report_data[section["name"]] = self._generate_distribution_report(
                    project_id,
                    section["dimension"]
                )
        
        return report_data

    def _count_by_severity(self, issues: List[Issue]) -> Dict[str, int]:
        """Count issues by severity level."""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity_counts[issue.severity] += 1
        return severity_counts

    def _get_category_distribution(self, issues: List[Issue]) -> Dict[str, int]:
        """Get distribution of issues by category."""
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        return category_counts

    def _get_resolution_stats(self, issues: List[Issue]) -> Dict[str, Any]:
        """Get statistics about issue resolution."""
        total = len(issues)
        resolved = sum(1 for issue in issues if issue.status == "resolved")
        avg_resolution_time = self._calculate_avg_resolution_time(issues)
        
        return {
            "total": total,
            "resolved": resolved,
            "resolution_rate": (resolved / total * 100) if total > 0 else 0,
            "avg_resolution_time": avg_resolution_time
        }

    def _calculate_quality_score(self, issues: List[Issue]) -> float:
        """Calculate overall quality score (0-100)."""
        if not issues:
            return 100.0
            
        # Weight factors for different severity levels
        weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        
        # Calculate weighted score
        total_weight = sum(weights[issue.severity] for issue in issues)
        max_possible_weight = len(issues) * 1.0  # Assuming all issues are critical
        
        # Convert to 0-100 scale
        score = 100 * (1 - (total_weight / max_possible_weight))
        return round(score, 2)

    def _calculate_trends(self, df: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """Calculate trend analysis for specified metric."""
        if metric == "issues":
            trend_data = df.groupby('period').size().to_dict()
        elif metric == "quality_score":
            # Calculate quality score for each period
            trend_data = {}
            for period, group in df.groupby('period'):
                issues = [Issue(**row) for row in group.to_dict('records')]
                trend_data[period] = self._calculate_quality_score(issues)
        
        return {
            "data": trend_data,
            "analysis": self._analyze_trend(trend_data)
        }

    def _analyze_trend(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trend data and provide insights."""
        values = list(trend_data.values())
        if not values:
            return {"direction": "stable", "change_percentage": 0}
            
        first_value = values[0]
        last_value = values[-1]
        change_percentage = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        
        return {
            "direction": "increasing" if change_percentage > 0 else "decreasing" if change_percentage < 0 else "stable",
            "change_percentage": round(change_percentage, 2)
        }

    def _calculate_avg_resolution_time(self, issues: List[Issue]) -> float:
        """Calculate average resolution time in hours."""
        resolved_issues = [issue for issue in issues if issue.status == "resolved" and issue.resolved_at]
        if not resolved_issues:
            return 0.0
            
        total_hours = sum(
            (issue.resolved_at - issue.created_at).total_seconds() / 3600
            for issue in resolved_issues
        )
        return round(total_hours / len(resolved_issues), 2)

    def _generate_distribution_report(self, project_id: str, dimension: str) -> Dict[str, Any]:
        """Generate distribution report for specified dimension."""
        issues = self.db.query(Issue).filter(Issue.project_id == project_id).all()
        
        if dimension == "severity":
            return self._count_by_severity(issues)
        elif dimension == "category":
            return self._get_category_distribution(issues)
        elif dimension == "status":
            status_counts = {}
            for issue in issues:
                status_counts[issue.status] = status_counts.get(issue.status, 0) + 1
            return status_counts
        
        return {} 