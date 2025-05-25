from typing import Dict, List, Optional, Union
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Service for optimizing database queries and managing query performance."""

    def __init__(self, db_session: Session):
        """
        Initialize the QueryOptimizer.

        Args:
            db_session (Session): SQLAlchemy database session
        """
        self.db = db_session
        self.query_cache: Dict[str, Dict] = {}
        self.query_stats: Dict[str, Dict] = {}

    def analyze_query(self, query: str, params: Optional[Dict] = None) -> Dict:
        """
        Analyze a query's execution plan and performance.

        Args:
            query (str): SQL query to analyze
            params (Optional[Dict]): Query parameters

        Returns:
            Dict: Query analysis results including execution plan and statistics
        """
        try:
            # Get query execution plan
            explain_query = f"EXPLAIN ANALYZE {query}"
            result = self.db.execute(text(explain_query), params or {})
            plan = result.fetchall()

            # Get query statistics
            stats = self._get_query_stats(query)

            analysis = {
                'execution_plan': plan,
                'statistics': stats,
                'timestamp': datetime.utcnow().isoformat(),
                'query_hash': self._hash_query(query, params)
            }

            # Cache the analysis
            self.query_cache[analysis['query_hash']] = analysis
            self.query_stats[analysis['query_hash']] = stats

            return analysis

        except SQLAlchemyError as e:
            logger.error(f"Error analyzing query: {str(e)}")
            raise

    def optimize_query(self, query: str, params: Optional[Dict] = None) -> Dict:
        """
        Optimize a query based on analysis and best practices.

        Args:
            query (str): SQL query to optimize
            params (Optional[Dict]): Query parameters

        Returns:
            Dict: Optimization suggestions and improved query
        """
        try:
            # Analyze current query
            analysis = self.analyze_query(query, params)
            
            # Get optimization suggestions
            suggestions = self._generate_optimization_suggestions(analysis)
            
            # Generate optimized query
            optimized_query = self._apply_optimizations(query, suggestions)
            
            # Analyze optimized query
            optimized_analysis = self.analyze_query(optimized_query, params)
            
            return {
                'original_query': query,
                'optimized_query': optimized_query,
                'suggestions': suggestions,
                'improvement': self._calculate_improvement(
                    analysis['statistics'],
                    optimized_analysis['statistics']
                ),
                'timestamp': datetime.utcnow().isoformat()
            }

        except SQLAlchemyError as e:
            logger.error(f"Error optimizing query: {str(e)}")
            raise

    def get_query_performance(self, query_hash: str) -> Dict:
        """
        Get performance statistics for a specific query.

        Args:
            query_hash (str): Hash of the query to analyze

        Returns:
            Dict: Query performance statistics
        """
        return self.query_stats.get(query_hash, {})

    def _hash_query(self, query: str, params: Optional[Dict] = None) -> str:
        """Generate a unique hash for a query and its parameters."""
        import hashlib
        query_str = f"{query}{str(params or {})}"
        return hashlib.md5(query_str.encode()).hexdigest()

    def _get_query_stats(self, query: str) -> Dict:
        """Get query execution statistics."""
        try:
            # Get query execution time
            start_time = datetime.utcnow()
            self.db.execute(text(query))
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Get query plan statistics
            explain_query = f"EXPLAIN (FORMAT JSON) {query}"
            result = self.db.execute(text(explain_query))
            plan = result.fetchone()[0]

            return {
                'execution_time': execution_time,
                'plan': plan,
                'timestamp': datetime.utcnow().isoformat()
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting query stats: {str(e)}")
            raise

    def _generate_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """Generate optimization suggestions based on query analysis."""
        suggestions = []

        # Check for missing indexes
        if self._has_sequential_scan(analysis['execution_plan']):
            suggestions.append({
                'type': 'index',
                'description': 'Consider adding an index to improve scan performance',
                'severity': 'high'
            })

        # Check for inefficient joins
        if self._has_inefficient_joins(analysis['execution_plan']):
            suggestions.append({
                'type': 'join',
                'description': 'Optimize join conditions or add appropriate indexes',
                'severity': 'medium'
            })

        # Check for large result sets
        if self._has_large_result_set(analysis['execution_plan']):
            suggestions.append({
                'type': 'pagination',
                'description': 'Consider implementing pagination or limiting result set',
                'severity': 'medium'
            })

        return suggestions

    def _apply_optimizations(self, query: str, suggestions: List[Dict]) -> str:
        """Apply optimizations to the query based on suggestions."""
        optimized_query = query

        for suggestion in suggestions:
            if suggestion['type'] == 'pagination':
                # Add LIMIT clause if not present
                if 'LIMIT' not in query.upper():
                    optimized_query += ' LIMIT 1000'
            # Add more optimization applications as needed

        return optimized_query

    def _calculate_improvement(
        self,
        original_stats: Dict,
        optimized_stats: Dict
    ) -> Dict:
        """Calculate performance improvement between original and optimized queries."""
        time_improvement = (
            original_stats['execution_time'] - optimized_stats['execution_time']
        ) / original_stats['execution_time'] * 100

        return {
            'time_improvement_percentage': time_improvement,
            'original_execution_time': original_stats['execution_time'],
            'optimized_execution_time': optimized_stats['execution_time']
        }

    def _has_sequential_scan(self, plan: List) -> bool:
        """Check if query plan contains sequential scans."""
        return any('Seq Scan' in str(node) for node in plan)

    def _has_inefficient_joins(self, plan: List) -> bool:
        """Check if query plan contains inefficient joins."""
        return any('Nested Loop' in str(node) for node in plan)

    def _has_large_result_set(self, plan: List) -> bool:
        """Check if query plan indicates large result sets."""
        return any('rows=' in str(node) and int(str(node).split('rows=')[1].split()[0]) > 10000
                  for node in plan) 