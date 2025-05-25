from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from app.models.rule import Rule
from app.schemas.rule import RuleTestResult
import numpy as np

class RuleTester:
    """Service for testing custom rules against sample data."""

    def __init__(self, db_session: Session):
        """
        Initialize the RuleTester.

        Args:
            db_session (Session): SQLAlchemy database session
        """
        self.db = db_session

    def test_rule(self, rule: Dict[str, Any], test_data: pd.DataFrame) -> RuleTestResult:
        """
        Test a rule against sample data.

        Args:
            rule (Dict[str, Any]): Rule to test
            test_data (pd.DataFrame): Sample data to test against

        Returns:
            RuleTestResult: Test results including matches and performance metrics
        """
        start_time = datetime.utcnow()
        matches = []
        errors = []

        try:
            # Apply each condition to the test data
            for condition in rule.get('conditions', []):
                condition_matches = self._apply_condition(condition, test_data)
                matches.extend(condition_matches)

            # Remove duplicates while preserving order
            matches = list(dict.fromkeys(matches))

            # Apply actions to matched rows
            for action in rule.get('actions', []):
                self._apply_action(action, test_data, matches)

            # Calculate performance metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            match_percentage = (len(matches) / len(test_data)) * 100 if len(test_data) > 0 else 0

            return RuleTestResult(
                rule_id=rule.get('id'),
                matches=matches,
                match_percentage=match_percentage,
                execution_time=execution_time,
                errors=errors,
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            errors.append(str(e))
            return RuleTestResult(
                rule_id=rule.get('id'),
                matches=[],
                match_percentage=0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                errors=errors,
                timestamp=datetime.utcnow().isoformat()
            )

    def _apply_condition(self, condition: Dict[str, Any], data: pd.DataFrame) -> List[int]:
        """Apply a condition to the data and return matching row indices."""
        field = condition['field']
        operator = condition['operator']
        value = condition['value']

        if field not in data.columns:
            raise ValueError(f"Field '{field}' not found in test data")

        if operator == 'equals':
            return data[data[field] == value].index.tolist()
        elif operator == 'not_equals':
            return data[data[field] != value].index.tolist()
        elif operator == 'contains':
            return data[data[field].astype(str).str.contains(str(value))].index.tolist()
        elif operator == 'not_contains':
            return data[~data[field].astype(str).str.contains(str(value))].index.tolist()
        elif operator == 'greater_than':
            return data[data[field] > value].index.tolist()
        elif operator == 'less_than':
            return data[data[field] < value].index.tolist()
        elif operator == 'between':
            return data[(data[field] >= value[0]) & (data[field] <= value[1])].index.tolist()
        elif operator == 'in_list':
            return data[data[field].isin(value)].index.tolist()
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _apply_action(self, action: Dict[str, Any], data: pd.DataFrame, matches: List[int]) -> None:
        """Apply an action to the matched rows."""
        action_type = action['type']
        value = action.get('value')

        if action_type == 'flag':
            # Add a flag column to the data
            data.loc[matches, 'flagged'] = True
            if value:
                data.loc[matches, 'flag_reason'] = value

        elif action_type == 'fix':
            # Apply the fix to the data
            if 'fix_field' in action and 'fix_value' in action:
                data.loc[matches, action['fix_field']] = action['fix_value']

        elif action_type == 'remove':
            # Mark rows for removal
            data.loc[matches, 'to_remove'] = True

        elif action_type == 'replace':
            # Replace values in the specified field
            if 'replace_field' in action and value is not None:
                data.loc[matches, action['replace_field']] = value

    def generate_test_data(self, rule: Dict[str, Any], num_samples: int = 100) -> pd.DataFrame:
        """
        Generate test data for a rule.

        Args:
            rule (Dict[str, Any]): Rule to generate test data for
            num_samples (int): Number of samples to generate

        Returns:
            pd.DataFrame: Generated test data
        """
        # Get all unique fields from conditions
        fields = set()
        for condition in rule.get('conditions', []):
            fields.add(condition['field'])

        # Create empty DataFrame with required columns
        data = pd.DataFrame(columns=list(fields))

        # Generate random data for each field
        for field in fields:
            # Determine field type from conditions
            field_type = self._infer_field_type(rule, field)
            data[field] = self._generate_field_data(field_type, num_samples)

        return data

    def _infer_field_type(self, rule: Dict[str, Any], field: str) -> str:
        """Infer the data type of a field from the rule conditions."""
        for condition in rule.get('conditions', []):
            if condition['field'] == field:
                if condition['operator'] in ['greater_than', 'less_than', 'between']:
                    return 'numeric'
                elif condition['operator'] in ['contains', 'not_contains']:
                    return 'text'
                elif isinstance(condition['value'], (int, float)):
                    return 'numeric'
                else:
                    return 'text'
        return 'text'  # Default to text if type cannot be inferred

    def _generate_field_data(self, field_type: str, num_samples: int) -> pd.Series:
        """Generate random data for a field based on its type."""
        if field_type == 'numeric':
            return pd.Series(np.random.normal(0, 1, num_samples))
        else:  # text
            return pd.Series([f"Sample {i}" for i in range(num_samples)]) 