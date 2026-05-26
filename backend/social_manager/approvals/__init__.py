"""
Approvals and compliance layer.
Mandatory approval gates, role-based permissions, policy checks, audit logging.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Literal
from enum import Enum

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """Role-based access control."""
    ADMIN = "admin"
    MANAGER = "manager"
    CREATOR = "creator"
    VIEWER = "viewer"


class PolicyViolation:
    """Represents a policy check failure."""
    
    def __init__(self, rule_name: str, severity: Literal["warning", "error"], details: str):
        self.rule_name = rule_name
        self.severity = severity
        self.details = details
    
    def to_dict(self) -> Dict:
        return {
            "rule": self.rule_name,
            "severity": self.severity,
            "details": self.details,
        }


class DiscloseRequirement:
    """Mandatory disclosure requirement."""
    
    def __init__(self, keyword: str, disclosure_text: str):
        self.keyword = keyword
        self.disclosure_text = disclosure_text
    
    def check(self, content: str) -> Optional[str]:
        """Return required disclosure if keyword found."""
        if self.keyword.lower() in content.lower():
            return self.disclosure_text
        return None


class PolicyEngine:
    """Policy checking engine."""
    
    BANNED_WORDS = [
        "guarantee", "cure", "miracle", "clinically proven",  # health claims
        "free money", "guaranteed returns", "risk-free",  # financial claims
    ]
    
    DISCLOSURE_REQUIREMENTS = [
        DiscloseRequirement("sponsorship", "#ad #sponsored"),
        DiscloseRequirement("affiliate", "affiliate link"),
    ]
    
    def __init__(self):
        self.custom_banned_words: List[str] = []
        self.custom_disclosures: List[DiscloseRequirement] = []
    
    def add_banned_word(self, word: str):
        """Add custom banned word."""
        self.custom_banned_words.append(word.lower())
    
    def add_disclosure_requirement(self, keyword: str, disclosure: str):
        """Add custom disclosure requirement."""
        self.custom_disclosures.append(DiscloseRequirement(keyword, disclosure))
    
    def check_content(self, content: str) -> Dict:
        """
        Run all policy checks on content.
        
        Returns: {
            violations: [PolicyViolation],
            required_disclosures: [str],
            passed: bool,
        }
        """
        violations = []
        required_disclosures = []
        
        # Check banned words
        content_lower = content.lower()
        all_banned = self.BANNED_WORDS + self.custom_banned_words
        
        for word in all_banned:
            if word.lower() in content_lower:
                violations.append(PolicyViolation(
                    f"banned_word:{word}",
                    "error",
                    f"Banned word detected: '{word}'"
                ))
        
        # Check disclosure requirements
        all_disclosures = self.DISCLOSURE_REQUIREMENTS + self.custom_disclosures
        for req in all_disclosures:
            disclosure = req.check(content)
            if disclosure and disclosure not in required_disclosures:
                required_disclosures.append(disclosure)
        
        # Check for minimum length (warning)
        if len(content) < 20:
            violations.append(PolicyViolation(
                "min_length",
                "warning",
                "Content is very short (< 20 chars). Consider adding more context."
            ))
        
        passed = all(v.severity != "error" for v in violations)
        
        return {
            "violations": violations,
            "required_disclosures": required_disclosures,
            "passed": passed,
        }


class ApprovalWorkflow:
    """Approval workflow management."""
    
    def __init__(self):
        self.pending_approvals: Dict[int, Dict] = {}  # post_id -> approval_data
        self.approved_posts: Dict[int, Dict] = {}
        self.rejected_posts: Dict[int, Dict] = {}
        self.audit_log: List[Dict] = []
    
    def submit_for_approval(self, post_id: int, content: str, creator_id: str, required_approvers: List[str]) -> Dict:
        """Submit post for approval."""
        approval = {
            "post_id": post_id,
            "content": content,
            "creator_id": creator_id,
            "required_approvers": required_approvers,
            "approvals": {},  # {approver_id: {status, timestamp, notes}}
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        
        self.pending_approvals[post_id] = approval
        self._audit_log("post_submitted", post_id, creator_id, f"Submitted for approval by {len(required_approvers)} approvers")
        
        return approval
    
    def approve_post(self, post_id: int, approver_id: str, notes: str = "") -> Optional[Dict]:
        """Approve a pending post."""
        if post_id not in self.pending_approvals:
            return None
        
        approval = self.pending_approvals[post_id]
        approval["approvals"][approver_id] = {
            "status": "approved",
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes,
        }
        
        # Check if all required approvers have approved
        required_set = set(approval["required_approvers"])
        approved_set = set(approval["approvals"].keys())
        
        if required_set.issubset(approved_set):
            approval["status"] = "approved"
            self.approved_posts[post_id] = approval
            del self.pending_approvals[post_id]
            self._audit_log("post_approved", post_id, approver_id, f"Final approval from {approver_id}")
        
        self._audit_log("post_approved_by", post_id, approver_id, notes)
        
        return approval
    
    def reject_post(self, post_id: int, approver_id: str, reason: str) -> Optional[Dict]:
        """Reject a pending post."""
        if post_id not in self.pending_approvals:
            return None
        
        approval = self.pending_approvals[post_id]
        approval["status"] = "rejected"
        approval["rejected_by"] = approver_id
        approval["rejection_reason"] = reason
        approval["rejected_at"] = datetime.utcnow().isoformat()
        
        self.rejected_posts[post_id] = approval
        del self.pending_approvals[post_id]
        
        self._audit_log("post_rejected", post_id, approver_id, f"Rejected: {reason}")
        
        return approval
    
    def get_pending_approvals_for_user(self, user_id: str) -> List[Dict]:
        """Get pending approvals waiting for specific user."""
        result = []
        for approval in self.pending_approvals.values():
            if user_id in approval["required_approvers"] and user_id not in approval["approvals"]:
                result.append(approval)
        return result
    
    def _audit_log(self, action: str, post_id: int, user_id: str, details: str):
        """Record audit trail entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "post_id": post_id,
            "user_id": user_id,
            "details": details,
        }
        self.audit_log.append(entry)
        logger.info(f"[AUDIT] {action} - post:{post_id} user:{user_id} - {details}")
    
    def get_audit_log(self, post_id: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Get audit log entries."""
        if post_id:
            return [e for e in self.audit_log if e["post_id"] == post_id][-limit:]
        return self.audit_log[-limit:]


class RoleBasedAccessControl:
    """Role-based permission checking."""
    
    PERMISSIONS = {
        UserRole.ADMIN: ["create", "approve", "publish", "delete", "audit"],
        UserRole.MANAGER: ["create", "approve", "publish"],
        UserRole.CREATOR: ["create"],
        UserRole.VIEWER: ["view"],
    }
    
    @staticmethod
    def can_approve(user_role: UserRole) -> bool:
        """Check if role can approve posts."""
        return "approve" in RoleBasedAccessControl.PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def can_publish(user_role: UserRole) -> bool:
        """Check if role can publish posts."""
        return "publish" in RoleBasedAccessControl.PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def can_create(user_role: UserRole) -> bool:
        """Check if role can create posts."""
        return "create" in RoleBasedAccessControl.PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def get_permissions(user_role: UserRole) -> List[str]:
        """Get all permissions for role."""
        return RoleBasedAccessControl.PERMISSIONS.get(user_role, [])


# Global instances
policy_engine = PolicyEngine()
approval_workflow = ApprovalWorkflow()


__all__ = [
    "UserRole",
    "PolicyEngine",
    "ApprovalWorkflow",
    "RoleBasedAccessControl",
    "policy_engine",
    "approval_workflow",
]
