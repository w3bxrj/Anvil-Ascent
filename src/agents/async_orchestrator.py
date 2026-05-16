"""
ASYNC ORCHESTRATOR: Runs tasks in parallel — not sequential
Massive performance + architecture upgrade
"""

import asyncio
from typing import List, Dict, Callable
import time

class AsyncOrchestrator:
    """
    Executes investigation tasks concurrently
    """
    
    async def execute_parallel(self, tasks: List[Dict]) -> Dict:
        """
        tasks = [
            {"name": "index_repo", "func": indexer.index_local_repo, "args": [...]},
            {"name": "classify", "func": classifier.classify, "args": [...]},
            {"name": "search_similar", "func": search_similar_issues, "args": [...]}
        ]
        """
        start_time = time.time()
        
        # Create all coroutines
        coroutines = []
        for task in tasks:
            coro = self._run_task(task)
            coroutines.append(coro)
        
        # Run ALL in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Process results
        output = {}
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                output[task["name"]] = {"status": "error", "error": str(result)}
            else:
                output[task["name"]] = {"status": "success", "data": result}
        
        output["execution_time"] = round(time.time() - start_time, 2)
        output["parallel_tasks"] = len(tasks)
        
        return output
    
    async def _run_task(self, task: Dict):
        """Run single task with timeout"""
        func = task["func"]
        args = task.get("args", [])
        kwargs = task.get("kwargs", {})
        timeout = task.get("timeout", 30)
        
        return await asyncio.wait_for(
            func(*args, **kwargs) if asyncio.iscoroutinefunction(func) 
            else asyncio.to_thread(func, *args, **kwargs),
            timeout=timeout
        )

# Singleton
orchestrator = AsyncOrchestrator()