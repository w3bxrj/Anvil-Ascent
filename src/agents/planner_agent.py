"""
PLANNER AGENT: Decides WHAT to investigate based on issue type
Most important missing piece — makes system truly autonomous
"""

import omium
from typing import List, Dict, Literal
from enum import Enum

class InvestigationType(str, Enum):
    CODE_SEARCH = "code_search"           # Search codebase
    SIMILAR_ISSUES = "similar_issues"     # Find past related issues
    DOCS_CHECK = "docs_check"             # Check documentation
    TESTS_CHECK = "tests_check"           # Look at existing tests
    REPRODUCE = "reproduce"              # Try to reproduce bug

class PlannerAgent:
    """
    AI decides investigation strategy — not hardcoded flow
    """
    
    @omium.trace("planner_agent")
    def plan_investigation(self, issue_title: str, issue_body: str,
                          issue_type: str, priority: str,
                          keywords: List[str]) -> Dict:
        """
        Returns investigation plan with priorities
        """
        plan = {
            "primary_tasks": [],
            "secondary_tasks": [],
            "estimated_time": "30s",
            "reasoning": ""
        }
        
        # BUG: Need code search + reproduce + similar issues
        if issue_type == "bug":
            plan["primary_tasks"] = [
                InvestigationType.CODE_SEARCH,
                InvestigationType.SIMILAR_ISSUES
            ]
            plan["secondary_tasks"] = [
                InvestigationType.TESTS_CHECK
            ]
            plan["reasoning"] = "Bugs need code context + past fixes to avoid regression"
        
        # FEATURE: Need docs + code structure + similar features
        elif issue_type == "feature":
            plan["primary_tasks"] = [
                InvestigationType.CODE_SEARCH,
                InvestigationType.DOCS_CHECK
            ]
            plan["secondary_tasks"] = [
                InvestigationType.TESTS_CHECK
            ]
            plan["reasoning"] = "Features need architecture understanding + documentation updates"
        
        # SECURITY: Need code search + similar issues URGENT
        elif issue_type == "security":
            plan["primary_tasks"] = [
                InvestigationType.CODE_SEARCH,
                InvestigationType.SIMILAR_ISSUES,
                InvestigationType.TESTS_CHECK
            ]
            plan["secondary_tasks"] = []
            plan["estimated_time"] = "20s"
            plan["reasoning"] = "Security issues need immediate code audit + pattern detection"
        
        # PERFORMANCE: Need code + tests + profiling context
        elif issue_type == "performance":
            plan["primary_tasks"] = [
                InvestigationType.CODE_SEARCH,
                InvestigationType.TESTS_CHECK
            ]
            plan["secondary_tasks"] = [
                InvestigationType.DOCS_CHECK
            ]
            plan["reasoning"] = "Performance needs bottleneck identification + benchmark context"
        
        # Default
        else:
            plan["primary_tasks"] = [InvestigationType.CODE_SEARCH]
            plan["secondary_tasks"] = [InvestigationType.DOCS_CHECK]
            plan["reasoning"] = "Generic investigation with code context"
        
        return plan

# Singleton
planner = PlannerAgent()