"""
GitHub Comment Poster: Post AI-generated solution as issue comment
"""

import os
import httpx
import omium
from typing import Dict

class GitHubCommenter:
    """Post comments to GitHub issues via API"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
    
    @omium.trace("post_github_comment")
    async def post_comment(self, repo_full_name: str, issue_number: int,
                          solution: Dict) -> Dict:
        """
        Post solution as comment on GitHub issue
        """
        if not self.token:
            return {
                "status": "error",
                "message": "No GITHUB_TOKEN set",
                "posted": False
            }
        
        # Build markdown comment
        comment_body = self._format_comment(solution)
        
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"token {self.token}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json"
                    },
                    json={"body": comment_body}
                )
                
                if response.status_code == 201:
                    return {
                        "status": "success",
                        "message": "Comment posted successfully",
                        "posted": True,
                        "comment_url": response.json().get("html_url")
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"GitHub API error: {response.status_code} - {response.text}",
                        "posted": False
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "posted": False
            }
    
    def _format_comment(self, solution: Dict) -> str:
        """Format solution as GitHub markdown comment"""
        confidence = solution.get("confidence", 0)
        emoji = "🟢" if confidence > 80 else "🟡" if confidence > 50 else "🔴"
        
        return f"""## {emoji} AI-Powered Issue Analysis

> 🤖 This analysis was generated automatically by our Autonomous Issue Resolver

### 🔍 Root Cause Analysis
{solution.get('analysis', 'No analysis available')}

### 💡 Proposed Solution
{solution.get('solution', 'No solution proposed')}

### 📁 Files to Modify
{', '.join(solution.get('files_to_modify', ['Unknown']))}

### 🎯 Confidence Score: {confidence}%

---
*This is an automated response. Please review before implementing.*
"""

# Singleton
commenter = GitHubCommenter()