from src.agents.repo_indexer import indexer

from src.agents.code_retriever import retriever

from typing import Dict, List, Optional

import os

class ResearchAgent:

    """
    Autonomous research agent:
    1. Checks if repo is indexed
    2. Indexes if needed (local or GitHub)
    3. Retrieves relevant code context
    4. Returns structured research report
    """

    def __init__(self):

        self.indexer = indexer

        self.retriever = retriever

    async def investigate(self, repo_full_name: str, issue_title: str,

                        issue_body: str, keywords: List[str],

                        local_path: Optional[str] = None) -> Dict:

        """
        Full investigation pipeline
        """

        print(f"\n🔍 Starting research for {repo_full_name}...")

        if not self.indexer.is_indexed(repo_full_name):

            print(f"📦 Repo not indexed. Indexing...")

            if local_path and os.path.exists(local_path):

                result = self.indexer.index_local_repo(local_path, repo_full_name)

            else:

                repo_url = f"https://github.com/{repo_full_name}.git"

                result = self.indexer.clone_and_index(repo_url, repo_full_name)

            if result["status"] != "success":

                return {

                    "status": "error",

                    "message": f"Failed to index repo: {result.get('message', 'Unknown')}",

                    "context": None

                }

            source = result.get('source', 'unknown')

            print(f"✅ Indexed {result['files_indexed']} files from {source}")

        else:

            print(f"✅ Repo already indexed")

        print(f"🔎 Searching for relevant code...")

        context = self.retriever.get_context_for_issue(

            repo_full_name, issue_title, issue_body, keywords

        )

        print(f"📋 Found {context['total_files_found']} relevant files")

        for f in context['relevant_files'][:3]:

            print(f"   • {f['file_path']} (score: {f['relevance_score']})")

        return {

            "status": "success",

            "context": context,

            "files": context['relevant_files']

        }

research_agent = ResearchAgent()
