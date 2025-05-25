from typing import List, Dict, Any
from datetime import datetime
import re
from sqlalchemy.orm import Session
from app.models.rule import Rule
from app.schemas.rule import RuleValidation

class RuleValidator:
    """Service for validating custom rules."""

    def __init__(self, db_session: Session):
        """
        Initialize the RuleValidator.

        Args:
            db_session (Session): SQLAlchemy database session
        """
        self.db = db_session

    def validate_rule(self, rule: Dict[str, Any]) -> List[RuleValidation]:
        """
        Validate a rule and return a list of validation results.

        Args:
            rule (Dict[str, Any]): Rule to validate

        Returns:
            List[RuleValidation]: List of validation results
        """
        validations = []

        # Validate basic fields
        validations.extend(self._validate_basic_fields(rule))

        # Validate conditions
        validations.extend(self._validate_conditions(rule.get('conditions', [])))

        # Validate actions
        validations.extend(self._validate_actions(rule.get('actions', [])))

        # Validate rule logic
        validations.extend(self._validate_rule_logic(rule))

        return validations

    def _validate_basic_fields(self, rule: Dict[str, Any]) -> List[RuleValidation]:
        """Validate basic rule fields."""
        validations = []

        # Validate name
        if not rule.get('name'):
            validations.append(RuleValidation(
                isValid=False,
                message="Rule name is required",
                details="Please provide a name for the rule"
            ))
        elif len(rule['name']) > 100:
            validations.append(RuleValidation(
                isValid=False,
                message="Rule name is too long",
                details="Rule name must be less than 100 characters"
            ))

        # Validate description
        if not rule.get('description'):
            validations.append(RuleValidation(
                isValid=False,
                message="Rule description is required",
                details="Please provide a description for the rule"
            ))

        # Validate category
        valid_categories = ['data_quality', 'validation', 'transformation']
        if not rule.get('category') or rule['category'] not in valid_categories:
            validations.append(RuleValidation(
                isValid=False,
                message="Invalid rule category",
                details=f"Category must be one of: {', '.join(valid_categories)}"
            ))

        # Validate severity
        valid_severities = ['low', 'medium', 'high']
        if not rule.get('severity') or rule['severity'] not in valid_severities:
            validations.append(RuleValidation(
                isValid=False,
                message="Invalid rule severity",
                details=f"Severity must be one of: {', '.join(valid_severities)}"
            ))

        return validations

    def _validate_conditions(self, conditions: List[Dict[str, Any]]) -> List[RuleValidation]:
        """Validate rule conditions."""
        validations = []

        if not conditions:
            validations.append(RuleValidation(
                isValid=False,
                message="At least one condition is required",
                details="Please add at least one condition to the rule"
            ))
            return validations

        for i, condition in enumerate(conditions):
            # Validate field
            if not condition.get('field'):
                validations.append(RuleValidation(
                    isValid=False,
                    message=f"Condition {i + 1}: Field is required",
                    details="Please specify a field for the condition"
                ))

            # Validate operator
            valid_operators = [
                'equals', 'not_equals', 'contains', 'not_contains',
                'greater_than', 'less_than', 'between', 'in_list'
            ]
            if not condition.get('operator') or condition['operator'] not in valid_operators:
                validations.append(RuleValidation(
                    isValid=False,
                    message=f"Condition {i + 1}: Invalid operator",
                    details=f"Operator must be one of: {', '.join(valid_operators)}"
                ))

            # Validate value
            if 'value' not in condition:
                validations.append(RuleValidation(
                    isValid=False,
                    message=f"Condition {i + 1}: Value is required",
                    details="Please specify a value for the condition"
                ))
            elif condition['operator'] == 'between' and (
                not isinstance(condition['value'], list) or
                len(condition['value']) != 2
            ):
                validations.append(RuleValidation(
                    isValid=False,
                    message=f"Condition {i + 1}: Invalid value for 'between' operator",
                    details="Value must be a list with exactly two elements"
                ))

        return validations

    def _validate_actions(self, actions: List[Dict[str, Any]]) -> List[RuleValidation]:
        """Validate rule actions."""
        validations = []

        if not actions:
            validations.append(RuleValidation(
                isValid=False,
                message="At least one action is required",
                details="Please add at least one action to the rule"
            ))
            return validations

        for i, action in enumerate(actions):
            # Validate type
            valid_types = ['flag', 'fix', 'remove', 'replace']
            if not action.get('type') or action['type'] not in valid_types:
                validations.append(RuleValidation(
                    isValid=False,
                    message=f"Action {i + 1}: Invalid type",
                    details=f"Type must be one of: {', '.join(valid_types)}"
                ))

            # Validate value for replace action
            if action.get('type') == 'replace' and 'value' not in action:
                validations.append(RuleValidation(
                    isValid=False,
                    message=f"Action {i + 1}: Value is required for replace action",
                    details="Please specify a replacement value"
                ))

        return validations

    def _validate_rule_logic(self, rule: Dict[str, Any]) -> List[RuleValidation]:
        """Validate rule logic and potential conflicts."""
        validations = []

        # Check for conflicting conditions
        conditions = rule.get('conditions', [])
        for i, cond1 in enumerate(conditions):
            for j, cond2 in enumerate(conditions[i + 1:], i + 1):
                if self._are_conditions_conflicting(cond1, cond2):
                    validations.append(RuleValidation(
                        isValid=False,
                        message="Conflicting conditions detected",
                        details=f"Conditions {i + 1} and {j + 1} may conflict with each other"
                    ))

        # Check for redundant actions
        actions = rule.get('actions', [])
        for i, action1 in enumerate(actions):
            for j, action2 in enumerate(actions[i + 1:], i + 1):
                if self._are_actions_redundant(action1, action2):
                    validations.append(RuleValidation(
                        isValid=False,
                        message="Redundant actions detected",
                        details=f"Actions {i + 1} and {j + 1} may be redundant"
                    ))

        return validations

    def _are_conditions_conflicting(self, cond1: Dict[str, Any], cond2: Dict[str, Any]) -> bool:
        """Check if two conditions conflict with each other."""
        if cond1['field'] != cond2['field']:
            return False

        # Check for direct contradictions
        if (
            (cond1['operator'] == 'equals' and cond2['operator'] == 'not_equals' and
             cond1['value'] == cond2['value']) or
            (cond1['operator'] == 'contains' and cond2['operator'] == 'not_contains' and
             cond1['value'] == cond2['value'])
        ):
            return True

        # Check for range conflicts
        if cond1['operator'] == 'between' and cond2['operator'] == 'between':
            range1 = cond1['value']
            range2 = cond2['value']
            if (
                range1[0] > range2[1] or  # range1 is completely after range2
                range1[1] < range2[0]     # range1 is completely before range2
            ):
                return True

        return False

    def _are_actions_redundant(self, action1: Dict[str, Any], action2: Dict[str, Any]) -> bool:
        """Check if two actions are redundant."""
        if action1['type'] != action2['type']:
            return False

        # Check for redundant replace actions
        if action1['type'] == 'replace' and action1.get('value') == action2.get('value'):
            return True

        # Check for redundant flag actions
        if action1['type'] == 'flag' and action1.get('value') == action2.get('value'):
            return True

        return False 