import os

import chromadb

from chromadb.config import Settings

from sentence_transformers import SentenceTransformer

from git import Repo

from pathlib import Path

import tempfile

from typing import List, Dict, Optional

CODE_EXTENSIONS = {

    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',

    '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',

    '.kt', '.scala', '.r', '.m', '.mm', '.sql', '.sh', '.yaml',

    '.yml', '.json', '.xml', '.md', '.txt', '.html', '.css',

    '.scss', '.sass', '.less', '.vue', '.svelte'

}

class RepoIndexer:

    """Index a GitHub repository into ChromaDB for semantic search"""

    def __init__(self, persist_dir: str = "./data/chroma_db"):

        self.persist_dir = persist_dir

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_dir)

        self.collections = {}

    def _get_collection(self, repo_full_name: str):

        """Get or create collection for repo"""

        if repo_full_name not in self.collections:

            safe_name = repo_full_name.replace("/", "_")

            self.collections[repo_full_name] = self.client.get_or_create_collection(

                name=safe_name,

                metadata={"repo": repo_full_name}

            )

        return self.collections[repo_full_name]

    def index_local_repo(self, local_path: str, repo_full_name: str) -> Dict:

        """
        Index a local repository folder (for hackathon demo / testing)
        Returns: {"status": "success", "files_indexed": N}
        """

        print(f"🔧 Indexing local repo: {local_path}")

        if not os.path.exists(local_path):

            return {"status": "error", "message": f"Path not found: {local_path}"}

        files = self._extract_code_files(local_path)

        print(f"📁 Found {len(files)} code files")

        if not files:

            return {"status": "error", "message": "No code files found in path"}

        collection = self._get_collection(repo_full_name)

        try:

            existing = collection.get()

            if existing['ids']:

                collection.delete(ids=existing['ids'])

        except Exception:

            pass

        batch_size = 100

        for i in range(0, len(files), batch_size):

            batch = files[i:i + batch_size]

            self._index_batch(collection, batch, repo_full_name)

        return {

            "status": "success",

            "files_indexed": len(files),

            "repo": repo_full_name,

            "source": "local"

        }

    def clone_and_index(self, repo_url: str, repo_full_name: str) -> Dict:

        """
        Clone repo from GitHub, extract files, create embeddings
        Returns: {"status": "success", "files_indexed": N}
        """

        print(f"🔧 Cloning {repo_full_name} from {repo_url}...")

        tmpdir = tempfile.mkdtemp()

        try:

            Repo.clone_from(repo_url, tmpdir, depth=1)

        except Exception as e:

            return {"status": "error", "message": str(e)}

        files = self._extract_code_files(tmpdir)

        print(f"📁 Found {len(files)} code files")

        if not files:

            return {"status": "error", "message": "No code files found in cloned repo"}

        collection = self._get_collection(repo_full_name)

        try:

            existing = collection.get()

            if existing['ids']:

                collection.delete(ids=existing['ids'])

        except Exception:

            pass

        batch_size = 100

        for i in range(0, len(files), batch_size):

            batch = files[i:i + batch_size]

            self._index_batch(collection, batch, repo_full_name)

        return {

            "status": "success",

            "files_indexed": len(files),

            "repo": repo_full_name,

            "source": "github"

        }

    def _extract_code_files(self, repo_path: str | Path) -> List[Dict]:

        """Extract all code files with content"""

        files = []

        repo_path = Path(repo_path)

        for file_path in repo_path.rglob("*"):

            if any(part.startswith('.') or part in [

                'node_modules', 'venv', '__pycache__', 'dist', 'build',

                '.git', 'data', 'chromadb'

            ] for part in file_path.parts):

                continue

            if file_path.is_file() and file_path.suffix in CODE_EXTENSIONS:

                try:

                    content = file_path.read_text(encoding='utf-8', errors='ignore')

                    if len(content) < 10 or '\x00' in content:

                        continue

                    rel_path = str(file_path.relative_to(repo_path))

                    files.append({

                        "path": rel_path,

                        "content": content,

                        "extension": file_path.suffix,

                        "size": len(content)

                    })

                except Exception:

                    continue

        return files

    def _index_batch(self, collection, files: List[Dict], repo_name: str):

        """Index a batch of files into ChromaDB"""

        ids = []

        documents = []

        metadatas = []

        embeddings = []

        for i, file in enumerate(files):

            file_id = f"{repo_name}_{file['path']}_{i}"

            content = file['content'][:3000]

            embedding = self.embedding_model.encode(content).tolist()

            ids.append(file_id)

            documents.append(content)

            metadatas.append({

                "path": file['path'],

                "extension": file['extension'],

                "size": file['size'],

                "repo": repo_name

            })

            embeddings.append(embedding)

        collection.add(

            ids=ids,

            documents=documents,

            metadatas=metadatas,

            embeddings=embeddings

        )

    def is_indexed(self, repo_full_name: str) -> bool:

        """Check if repo is already indexed"""

        try:

            safe_name = repo_full_name.replace("/", "_")

            collection = self.client.get_collection(safe_name)

            count = collection.count()

            return count > 0

        except Exception:

            return False

indexer = RepoIndexer()
