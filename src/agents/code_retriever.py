from .repo_indexer import indexer

from typing import List, Dict

class CodeRetriever:

    """Retrieve relevant code based on issue keywords/query"""

    def __init__(self):

        self.indexer = indexer

    def search(self, repo_full_name: str, query: str, top_k: int = 5) -> List[Dict]:

        """
        Search repo for code relevant to query
        Returns: List of relevant file snippets
        """

        collection = self.indexer._get_collection(repo_full_name)

        query_embedding = self.indexer.embedding_model.encode(query).tolist()

        results = collection.query(

            query_embeddings=[query_embedding],

            n_results=top_k,

            include=["documents", "metadatas", "distances"]

        )

        formatted = []

        for i in range(len(results['ids'][0])):

            formatted.append({

                "file_path": results['metadatas'][0][i]['path'],

                "extension": results['metadatas'][0][i]['extension'],

                "content": results['documents'][0][i][:500] + "...",

                "relevance_score": round(1 - results['distances'][0][i], 3)

            })

        return formatted

    def get_context_for_issue(self, repo_full_name: str, issue_title: str,

                              issue_body: str, keywords: List[str]) -> Dict:

        """
        Build full research context for an issue
        Combines multiple search strategies
        """

        query = f"{issue_title}. {issue_body or ''}. Keywords: {', '.join(keywords)}"

        relevant_files = self.search(repo_full_name, query, top_k=8)

        keyword_query = " ".join(keywords[:5])

        keyword_results = self.search(repo_full_name, keyword_query, top_k=3)

        seen_paths = {f['file_path'] for f in relevant_files}

        for result in keyword_results:

            if result['file_path'] not in seen_paths:

                relevant_files.append(result)

        return {

            "query": query,

            "relevant_files": relevant_files,

            "total_files_found": len(relevant_files),

            "repo": repo_full_name

        }

retriever = CodeRetriever()
