from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.rule import Rule, RuleVersion
from app.schemas.rule import RuleVersionInfo

class RuleVersionControl:
    """Service for managing rule versions and history."""

    def __init__(self, db_session: Session):
        """
        Initialize the RuleVersionControl.

        Args:
            db_session (Session): SQLAlchemy database session
        """
        self.db = db_session

    def create_version(self, rule: Dict[str, Any], user_id: str, comment: Optional[str] = None) -> RuleVersion:
        """
        Create a new version of a rule.

        Args:
            rule (Dict[str, Any]): Rule to version
            user_id (str): ID of the user creating the version
            comment (Optional[str]): Comment describing the changes

        Returns:
            RuleVersion: Created version
        """
        # Get the current version number
        current_version = self.db.query(RuleVersion)\
            .filter(RuleVersion.rule_id == rule['id'])\
            .order_by(RuleVersion.version_number.desc())\
            .first()

        version_number = (current_version.version_number + 1) if current_version else 1

        # Create new version
        version = RuleVersion(
            rule_id=rule['id'],
            version_number=version_number,
            rule_data=rule,
            created_by=user_id,
            comment=comment,
            created_at=datetime.utcnow()
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)

        return version

    def get_version(self, rule_id: str, version_number: int) -> Optional[RuleVersion]:
        """
        Get a specific version of a rule.

        Args:
            rule_id (str): ID of the rule
            version_number (int): Version number to retrieve

        Returns:
            Optional[RuleVersion]: Requested version if found
        """
        return self.db.query(RuleVersion)\
            .filter(RuleVersion.rule_id == rule_id)\
            .filter(RuleVersion.version_number == version_number)\
            .first()

    def get_version_history(self, rule_id: str) -> List[RuleVersionInfo]:
        """
        Get the version history of a rule.

        Args:
            rule_id (str): ID of the rule

        Returns:
            List[RuleVersionInfo]: List of version information
        """
        versions = self.db.query(RuleVersion)\
            .filter(RuleVersion.rule_id == rule_id)\
            .order_by(RuleVersion.version_number.desc())\
            .all()

        return [
            RuleVersionInfo(
                version_number=v.version_number,
                created_at=v.created_at,
                created_by=v.created_by,
                comment=v.comment
            )
            for v in versions
        ]

    def compare_versions(self, rule_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """
        Compare two versions of a rule.

        Args:
            rule_id (str): ID of the rule
            version1 (int): First version number
            version2 (int): Second version number

        Returns:
            Dict[str, Any]: Comparison results
        """
        v1 = self.get_version(rule_id, version1)
        v2 = self.get_version(rule_id, version2)

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        changes = {
            'added': [],
            'removed': [],
            'modified': []
        }

        # Compare basic fields
        for field in ['name', 'description', 'category', 'severity']:
            if v1.rule_data[field] != v2.rule_data[field]:
                changes['modified'].append({
                    'field': field,
                    'old_value': v1.rule_data[field],
                    'new_value': v2.rule_data[field]
                })

        # Compare conditions
        v1_conditions = {str(c) for c in v1.rule_data['conditions']}
        v2_conditions = {str(c) for c in v2.rule_data['conditions']}

        for condition in v2_conditions - v1_conditions:
            changes['added'].append({
                'type': 'condition',
                'value': condition
            })

        for condition in v1_conditions - v2_conditions:
            changes['removed'].append({
                'type': 'condition',
                'value': condition
            })

        # Compare actions
        v1_actions = {str(a) for a in v1.rule_data['actions']}
        v2_actions = {str(a) for a in v2.rule_data['actions']}

        for action in v2_actions - v1_actions:
            changes['added'].append({
                'type': 'action',
                'value': action
            })

        for action in v1_actions - v2_actions:
            changes['removed'].append({
                'type': 'action',
                'value': action
            })

        return {
            'version1': version1,
            'version2': version2,
            'changes': changes,
            'timestamp': datetime.utcnow().isoformat()
        }

    def rollback_to_version(self, rule_id: str, version_number: int, user_id: str) -> Rule:
        """
        Rollback a rule to a specific version.

        Args:
            rule_id (str): ID of the rule
            version_number (int): Version number to rollback to
            user_id (str): ID of the user performing the rollback

        Returns:
            Rule: Updated rule
        """
        version = self.get_version(rule_id, version_number)
        if not version:
            raise ValueError(f"Version {version_number} not found")

        # Get the current rule
        rule = self.db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        # Update rule with version data
        for key, value in version.rule_data.items():
            setattr(rule, key, value)

        # Create a new version for the rollback
        self.create_version(
            rule=version.rule_data,
            user_id=user_id,
            comment=f"Rollback to version {version_number}"
        )

        self.db.commit()
        self.db.refresh(rule)

        return rule 