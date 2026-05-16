import json

import os

from typing import List, Dict

from datetime import datetime

class MemoryAgent:

    """
    Stores and retrieves issue history for pattern recognition
    """

    def __init__(self, memory_file: str = "./data/memory.json"):

        self.memory_file = memory_file

        self.memory = self._load()

    def _load(self) -> Dict:

        if os.path.exists(self.memory_file):

            with open(self.memory_file, 'r') as f:

                return json.load(f)

        return {"issues": [], "patterns": {}}

    def save(self):

        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

        with open(self.memory_file, 'w') as f:

            json.dump(self.memory, f, indent=2)

    def remember_issue(self, issue_number: int, title: str,

                      issue_type: str, solution: Dict, repo: str):

        """Store issue for future reference"""

        entry = {

            "number": issue_number,

            "title": title,

            "type": issue_type,

            "solution_summary": solution.get('analysis', '')[:200],

            "files_modified": solution.get('files_to_modify', []),

            "repo": repo,

            "timestamp": datetime.now().isoformat()

        }

        self.memory["issues"].append(entry)

        self._update_patterns(issue_type, title)

        self.save()

    def _update_patterns(self, issue_type: str, title: str):

        """Detect recurring patterns"""

        if issue_type not in self.memory["patterns"]:

            self.memory["patterns"][issue_type] = []

        keywords = [w.lower() for w in title.split() if len(w) > 4]

        self.memory["patterns"][issue_type].extend(keywords)

    def find_similar_past_issues(self, title: str, issue_type: str,

                                  repo: str, top_k: int = 3) -> List[Dict]:

        """Find historically similar issues"""

        keywords = set(title.lower().split())

        matches = []

        for issue in self.memory["issues"]:

            if issue["repo"] != repo:

                continue

            issue_keywords = set(issue["title"].lower().split())

            overlap = len(keywords & issue_keywords)

            if overlap > 0:

                matches.append({

                    "issue": issue,

                    "similarity_score": overlap / len(keywords)

                })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)

        return matches[:top_k]

    def get_pattern_insight(self, issue_type: str) -> str:

        """Get insight from past patterns"""

        patterns = self.memory["patterns"].get(issue_type, [])

        if not patterns:

            return ""

        from collections import Counter

        common = Counter(patterns).most_common(3)

        return f"Common in past {issue_type}s: {', '.join([p[0] for p in common])}"

memory = MemoryAgent()
