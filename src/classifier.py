import re
import omium
from typing import List, Tuple, Optional
from .models import IssueType, Priority, ParsedIssue

class IssueClassifier:
    """Rule-based + heuristic classifier for MVP"""
    
    # Keywords mapped to issue types
    TYPE_KEYWORDS = {
        IssueType.BUG: [
            "bug", "error", "crash", "exception", "broken", "not working",
            "fails", "failure", "fix", "issue", "problem", "wrong", "unexpected",
            "null pointer", "undefined", "traceback", "stack trace", "regression"
        ],
        IssueType.FEATURE: [
            "feature", "add", "support", "implement", "enhancement", "request",
            "would be nice", "should have", "need to", "ability to", "option to",
            "new", "improve", "upgrade", "extend"
        ],
        IssueType.DOCUMENTATION: [
            "doc", "docs", "documentation", "readme", "wiki", "guide", "tutorial",
            "explain", "example", " unclear", "confusing", "typo", "grammar"
        ],
        IssueType.PERFORMANCE: [
            "slow", "performance", "lag", "latency", "memory leak", "cpu",
            "optimize", "speed", "bottleneck", "inefficient", "hangs", "freeze"
        ],
        IssueType.SECURITY: [
            "security", "vulnerability", "cve", "exploit", "xss", "sql injection",
            "auth", "authentication", "authorization", "permission", "leak",
            "exposure", "csrf", "sanitize", "escape"
        ]
    }
    
    # Priority indicators
    PRIORITY_SIGNALS = {
        Priority.CRITICAL: [
            "crash", "data loss", "security", "vulnerability", "production down",
            "urgent", "emergency", "critical", "p0", "blocks", "broken completely"
        ],
        Priority.HIGH: [
            "important", "major", "significant", "blocking", "p1", "serious"
        ],
        Priority.LOW: [
            "minor", "cosmetic", "typo", "nitpick", "nice to have", "p3",
            "enhancement", "future", "eventually"
        ]
    }
    
    @omium.trace("issue_classification")
    def classify(self, title: str, body: Optional[str], labels: List[str]) -> Tuple[IssueType, Priority, float, List[str]]:
        """Classify issue and return (type, priority, confidence, keywords)"""
        text = f"{title} {body or ''}".lower()
        words = re.findall(r'\b[a-z]+\b', text)
        
        # Type classification
        type_scores = {t: 0 for t in IssueType}
        for issue_type, keywords in self.TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    type_scores[issue_type] += 1
        
        # Label override (GitHub labels are strong signals)
        label_map = {
            "bug": IssueType.BUG, "enhancement": IssueType.FEATURE,
            "feature": IssueType.FEATURE, "documentation": IssueType.DOCUMENTATION,
            "docs": IssueType.DOCUMENTATION, "performance": IssueType.PERFORMANCE,
            "security": IssueType.SECURITY
        }
        for label in labels:
            label_lower = label.lower()
            if label_lower in label_map:
                type_scores[label_map[label_lower]] += 3  # Strong weight
        
        # Select best type
        best_type = max(type_scores.keys(), key=lambda k: type_scores[k])
        if type_scores[best_type] == 0:
            best_type = IssueType.OTHER
        
        # Priority classification
        priority_scores = {p: 0 for p in Priority}
        for priority, keywords in self.PRIORITY_SIGNALS.items():
            for kw in keywords:
                if kw in text:
                    priority_scores[priority] += 1
        
        # Label priority override
        priority_labels = {"critical": Priority.CRITICAL, "high": Priority.HIGH, 
                          "low": Priority.LOW, "p0": Priority.CRITICAL, 
                          "p1": Priority.HIGH, "p2": Priority.MEDIUM, "p3": Priority.LOW}
        for label in labels:
            if label.lower() in priority_labels:
                priority_scores[priority_labels[label.lower()]] += 3
        
        best_priority = max(priority_scores.keys(), key=lambda k: priority_scores[k])
        if priority_scores[best_priority] == 0:
            best_priority = Priority.MEDIUM
        
        # Confidence based on signal strength
        max_type_score = max(type_scores.values())
        total_signals = sum(type_scores.values())
        confidence = min(0.95, 0.5 + (max_type_score / max(total_signals, 1)) * 0.5)
        
        # Extract keywords (top relevant terms)
        keywords = [w for w in set(words) if len(w) > 3][:10]
        
        return best_type, best_priority, round(confidence, 2), keywords

# Singleton instance
classifier = IssueClassifier()