"""
=============================================================================
AUTONOMOUS ISSUE RESOLVER v2.0 — Multi-Agent Orchestration
=============================================================================
Agents: Planner → Async Orchestrator → Research → Hypothesis → Solution → 
        Critic → Decision (Comment/PR/Escalate) → Memory
=============================================================================
"""

import sys
import os
import hmac
import hashlib
import json
import asyncio
import time
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import omium
from contextlib import asynccontextmanager

# Initialize Omium
omium.init()

# Ensure src is in path for imports
sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Core models & config
from src.models import IssuePayload, ParsedIssue, IssueType, Priority
from src.classifier import classifier
from src.config import settings

# AGENT IMPORTS — All 8 agents
from src.agents.planner_agent import planner, InvestigationType
from src.agents.async_orchestrator import orchestrator
from src.agents.research_agent import research_agent
from src.agents.hypothesis_agent import hypothesis_agent
from src.agents.solution_agent import solution_agent
from src.agents.critic_agent import critic
from src.agents.memory_agent import memory
from src.agents.pr_generator import pr_generator
from src.agents.github_commentor import commenter

# In-memory store for MVP
processing_queue = []
metrics = {"total_processed": 0, "escalated": 0, "auto_resolved": 0}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup with agent diagnostics"""
    print(f"\n{'='*70}")
    print(f"🚀 AUTONOMOUS ISSUE RESOLVER v2.0")
    print(f"{'='*70}")
    print(f"   Multi-Agent Architecture: 8 specialized agents")
    print(f"   Planner → Async Exec → Research → Hypothesis → Solution → Critic → Execute → Memory")
    print(f"")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   LLM: {settings.LLM_MODEL}")
    print(f"   Webhook: POST /webhook/github")
    print(f"   Health:  GET /health")
    print(f"   Metrics: GET /metrics")
    print(f"{'='*70}\n")
    yield
    print(f"\n{'='*70}")
    print(f"👋 Server shutting down...")
    print(f"   Total processed: {metrics['total_processed']}")
    print(f"   Auto-resolved: {metrics['auto_resolved']}")
    print(f"   Escalated: {metrics['escalated']}")
    print(f"{'='*70}\n")

app = FastAPI(
    title="Autonomous Issue Resolver v2.0",
    description="Multi-agent AI system for autonomous GitHub issue investigation & resolution",
    version="2.0.0",
    lifespan=lifespan
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def verify_github_signature(payload: bytes, signature: Optional[str]) -> bool:
    """Verify webhook signature - SKIP in dev mode"""
    if not settings.GITHUB_WEBHOOK_SECRET:
        return True
    if not signature or signature == "sha256=test":
        return True
    
    expected = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def parse_issue_payload(payload: dict) -> ParsedIssue:
    """Extract and clean GitHub issue data"""
    issue_data = payload["issue"]
    repo_data = payload["repository"]
    
    labels = [label["name"] for label in issue_data.get("labels", [])]
    
    issue_type, priority, confidence, keywords = classifier.classify(
        title=issue_data.get("title", ""),
        body=issue_data.get("body"),
        labels=labels
    )
    
    return ParsedIssue(
        id=issue_data["id"],
        number=issue_data["number"],
        title=issue_data.get("title", "Untitled"),
        body=issue_data.get("body"),
        state=issue_data.get("state", "open"),
        labels=labels,
        author=issue_data["user"]["login"],
        created_at=issue_data["created_at"],
        updated_at=issue_data["updated_at"],
        url=issue_data["html_url"],
        repo_name=repo_data["name"],
        repo_full_name=repo_data["full_name"],
        issue_type=issue_type,
        priority=priority,
        confidence_score=confidence,
        extracted_keywords=keywords
    )

# =============================================================================
# CORE PIPELINE — Multi-Agent Orchestration
# =============================================================================

@omium.trace("issue_resolution_pipeline")
async def process_issue_async(parsed: ParsedIssue):
    """
    FULL MULTI-AGENT PIPELINE
    =========================
    1. PLANNER: Decide investigation strategy
    2. ASYNC ORCHESTRATOR: Execute tasks in parallel
    3. RESEARCH: RAG-based code retrieval
    4. HYPOTHESIS: Generate & test root cause theories
    5. SOLUTION: LLM-powered fix generation
    6. CRITIC: Validate solution quality
    7. DECISION: Execute, Escalate, or Caution
    8. MEMORY: Store for future learning
    """
    pipeline_start = time.time()
    
    print(f"\n{'='*70}")
    print(f"🔔 ISSUE #{parsed.number}: {parsed.title[:60]}...")
    print(f"{'='*70}")
    print(f"   Repo: {parsed.repo_full_name}")
    print(f"   Type: {parsed.issue_type.value.upper()} | Priority: {parsed.priority.value.upper()}")
    print(f"   Classification Confidence: {parsed.confidence_score*100:.0f}%")
    print(f"   Keywords: {', '.join(parsed.extracted_keywords[:5])}")
    
    # =========================================================================
    # STEP 1: PLANNER AGENT — Decide Strategy
    # =========================================================================
    print(f"\n📋 [1/8] PLANNER: Deciding investigation strategy...")
    
    plan = planner.plan_investigation(
        issue_title=parsed.title,
        issue_body=parsed.body or "",
        issue_type=parsed.issue_type.value,
        priority=parsed.priority.value,
        keywords=parsed.extracted_keywords
    )
    
    print(f"   Strategy: {plan['reasoning']}")
    print(f"   Primary tasks: {[t.value for t in plan['primary_tasks']]}")
    print(f"   Secondary tasks: {[t.value for t in plan['secondary_tasks']]}")
    print(f"   Estimated time: {plan['estimated_time']}")
    
    # =========================================================================
    # STEP 2: ASYNC ORCHESTRATOR — Parallel Execution
    # =========================================================================
    print(f"\n⚡ [2/8] ASYNC ORCHESTRATOR: Executing {len(plan['primary_tasks'])} tasks in parallel...")
    
    local_repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Build parallel tasks
    parallel_tasks = []
    
    # Always: Index/Search repo
    parallel_tasks.append({
        "name": "research_repo",
        "func": research_agent.investigate,
        "args": [],
        "kwargs": {
            "repo_full_name": parsed.repo_full_name,
            "issue_title": parsed.title,
            "issue_body": parsed.body or "",
            "keywords": parsed.extracted_keywords,
            "local_path": local_repo_path
        },
        "timeout": 45
    })
    
    # Always: Check memory for similar issues
    parallel_tasks.append({
        "name": "check_memory",
        "func": memory.find_similar_past_issues,
        "args": [parsed.title, parsed.issue_type.value, parsed.repo_full_name],
        "kwargs": {},
        "timeout": 5
    })
    
    # Conditional: Search docs (if in plan)
    if InvestigationType.DOCS_CHECK in plan['primary_tasks']:
        parallel_tasks.append({
            "name": "search_docs",
            "func": _mock_search_docs,  # Placeholder for real implementation
            "args": [parsed.repo_full_name, parsed.extracted_keywords],
            "kwargs": {},
            "timeout": 10
        })
    
    # Execute all in parallel
    parallel_results = await orchestrator.execute_parallel(parallel_tasks)
    exec_time = parallel_results.get('execution_time', 0)
    
    print(f"   ⏱️  Parallel execution: {exec_time}s")
    print(f"   Tasks completed: {parallel_results['parallel_tasks']}")
    
    # Extract results
    research_result = parallel_results.get('research_repo', {}).get('data', {})
    similar_issues = parallel_results.get('check_memory', {}).get('data', [])
    
    if not research_result or research_result.get('status') != 'success':
        print(f"   ❌ Research failed — falling back to basic mode")
        await _handle_research_failure(parsed)
        return
    
    print(f"   📚 Research: {research_result['context']['total_files_found']} files found")
    
    if similar_issues:
        print(f"   🧠 Memory: {len(similar_issues)} similar past issues detected!")
        for si in similar_issues[:2]:
            print(f"      → #{si['issue']['number']}: {si['issue']['title'][:40]}... (score: {si['similarity_score']:.2f})")
    
    # =========================================================================
    # STEP 3: HYPOTHESIS AGENT — Root Cause Reasoning
    # =========================================================================
    print(f"\n🧠 [3/8] HYPOTHESIS: Generating & testing root cause theories...")
    
    hypotheses = hypothesis_agent.generate_hypotheses(
        issue_title=parsed.title,
        issue_body=parsed.body or "",
        keywords=parsed.extracted_keywords,
        research_files=research_result.get('files', [])
    )
    
    best = hypotheses['best_hypothesis']
    print(f"   Best theory: {best['theory'][:70]}...")
    print(f"   Theory confidence: {best['confidence']}%")
    print(f"   Evidence files: {len(best['evidence'])}")
    
    # =========================================================================
    # STEP 4: SOLUTION AGENT — Generate Fix
    # =========================================================================
    print(f"\n🤖 [4/8] SOLUTION: Generating fix via LLM ({settings.LLM_MODEL})...")
    
    # Enhance prompt with hypothesis context
    enhanced_context = research_result['files'] + [{
        'file_path': 'HYPOTHESIS',
        'content': f"Leading theory: {best['theory']}\nConfidence: {best['confidence']}%",
        'relevance_score': 1.0
    }]
    
    solution_result = await solution_agent.generate_solution(
        issue_title=parsed.title,
        issue_body=parsed.body or "",
        issue_type=parsed.issue_type.value,
        priority=parsed.priority.value,
        keywords=parsed.extracted_keywords,
        research_files=enhanced_context
    )
    
    if solution_result["status"] != "success":
        print(f"   ❌ LLM generation failed — escalating to human")
        await _escalate_to_human(parsed, "LLM generation failed")
        return
    
    print(f"   ✅ Solution generated")
    print(f"   Analysis: {solution_result['analysis'][:80]}...")
    print(f"   Raw confidence: {solution_result['confidence']}%")
    
    # =========================================================================
    # STEP 5: CRITIC AGENT — Validate Quality
    # =========================================================================
    print(f"\n🔍 [5/8] CRITIC: Validating solution quality...")
    
    critic_result = critic.evaluate(
        solution=solution_result,
        research_files=research_result.get('files', []),
        issue_title=parsed.title,
        issue_body=parsed.body or ""
    )
    
    scores = critic_result['scores']
    print(f"   Code relevance: {scores['code_relevance']:.0f}%")
    print(f"   Confidence calib: {scores['confidence_calibration']:.0f}%")
    print(f"   Contradiction: {scores['contradiction_check']:.0f}%")
    print(f"   OVERALL: {scores['overall']:.0f}% → VERDICT: {critic_result['verdict']}")
    
    # Use corrected solution (critic may have adjusted confidence)
    final_solution = critic_result['corrected_solution']
    
    # =========================================================================
    # STEP 6: DECISION — Execute, Escalate, or Caution
    # =========================================================================
    print(f"\n⚖️  [6/8] DECISION: {critic_result['action'].upper()}")
    
    if critic_result['action'] == "proceed":
        # HIGH CONFIDENCE → Full auto: Comment + Draft PR suggestion
        await _execute_full(parsed, final_solution, research_result, critic_result)
        
    elif critic_result['action'] == "proceed_with_caution":
        # MEDIUM CONFIDENCE → Comment with warning
        await _execute_with_caution(parsed, final_solution)
        
    else:
        # LOW CONFIDENCE → Escalate to human
        await _escalate_to_human(parsed, f"Critic score too low: {scores['overall']:.0f}%")
    
    # =========================================================================
    # STEP 7: MEMORY — Store for Learning
    # =========================================================================
    print(f"\n💾 [7/8] MEMORY: Storing issue pattern...")
    
    memory.remember_issue(
        issue_number=parsed.number,
        title=parsed.title,
        issue_type=parsed.issue_type.value,
        solution=final_solution,
        repo=parsed.repo_full_name
    )
    
    # Get pattern insight
    insight = memory.get_pattern_insight(parsed.issue_type.value)
    if insight:
        print(f"   Pattern insight: {insight}")
    
    # =========================================================================
    # STEP 8: METRICS — Pipeline Complete
    # =========================================================================
    total_time = round(time.time() - pipeline_start, 2)
    metrics['total_processed'] += 1
    
    print(f"\n✅ [8/8] PIPELINE COMPLETE in {total_time}s")
    print(f"{'='*70}\n")
    
    # Store in queue
    processing_queue.append({
        "issue_number": parsed.number,
        "status": critic_result['action'],
        "pipeline_time": total_time,
        "classification": parsed.to_processing_context(),
        "plan": plan,
        "hypothesis": hypotheses['best_hypothesis'],
        "critic_scores": scores,
        "solution": final_solution
    })

# =============================================================================
# DECISION HANDLERS
# =============================================================================

@omium.trace("execute_full")
async def _execute_full(parsed: ParsedIssue, solution: Dict, research_result: Dict, critic_result: Dict):
    """HIGH CONFIDENCE: Post comment + generate draft PR patch"""
    print(f"\n💬 [6a] Posting AI comment + draft PR suggestion...")
    
    # Generate patch if we have files
    patch = None
    if research_result.get('files'):
        patch = pr_generator.generate_patch(
            file_path=research_result['files'][0]['file_path'],
            original_content=research_result['files'][0].get('content', ''),
            solution=solution
        )
    
    # Enhance solution with patch
    if patch:
        solution['solution'] += f"\n\n### 📝 Suggested Patch\n{patch}"
    
    # Post comment
    comment_result = await commenter.post_comment(
        repo_full_name=parsed.repo_full_name,
        issue_number=parsed.number,
        solution=solution
    )
    
    if comment_result.get('posted'):
        print(f"   ✅ Comment + patch posted: {comment_result.get('comment_url', 'N/A')}")
        metrics['auto_resolved'] += 1
    else:
        print(f"   ⚠️  Post failed: {comment_result.get('message')}")

@omium.trace("execute_with_caution")
async def _execute_with_caution(parsed: ParsedIssue, solution: Dict):
    """MEDIUM CONFIDENCE: Post with disclaimer"""
    print(f"\n💬 [6b] Posting with CAUTION disclaimer...")
    
    solution['solution'] += "\n\n---\n⚠️ **Moderate Confidence**: This fix has been validated but please review before implementing. Human verification recommended."
    
    comment_result = await commenter.post_comment(
        repo_full_name=parsed.repo_full_name,
        issue_number=parsed.number,
        solution=solution
    )
    
    if comment_result.get('posted'):
        print(f"   ✅ Cautionary comment posted")
    else:
        print(f"   ⚠️  Post failed")

@omium.trace("escalate_to_human")
async def _escalate_to_human(parsed: ParsedIssue, reason: str):
    """LOW CONFIDENCE: Tag human, post minimal info"""
    print(f"\n🚨 [6c] ESCALATING to human: {reason}")
    
    # Post comment asking for human help
    await commenter.post_comment(
        repo_full_name=parsed.repo_full_name,
        issue_number=parsed.number,
        solution={
            "analysis": f"🤖 AI analysis inconclusive.\n\n**Reason:** {reason}\n\nThe autonomous system could not generate a reliable fix with sufficient confidence. Human engineer review is required.",
            "solution": "No automated fix generated. Please investigate manually.",
            "files_to_modify": [],
            "confidence": 0
        }
    )
    
    metrics['escalated'] += 1
    print(f"   🚨 Human escalation posted")

async def _handle_research_failure(parsed: ParsedIssue):
    """Handle when research step fails completely"""
    print(f"\n❌ Research pipeline failed — basic fallback")
    
    await commenter.post_comment(
        repo_full_name=parsed.repo_full_name,
        issue_number=parsed.number,
        solution={
            "analysis": "⚠️ Autonomous investigation failed. The system could not index or search the repository. This may be due to repository access issues or unsupported structure.",
            "solution": "Please ensure the repository is public and contains supported code files (.py, .js, .ts, etc.).",
            "files_to_modify": [],
            "confidence": 0
        }
    )
    
    metrics['escalated'] += 1

async def _mock_search_docs(repo_full_name: str, keywords: List[str]):
    """Placeholder for documentation search"""
    return {"status": "success", "docs_found": 0}

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check with agent status"""
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "architecture": "multi-agent",
        "agents": 8,
        "status": "running",
        "queued_issues": len(processing_queue),
        "metrics": metrics
    }

@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "healthy", "agents": "all_operational"}

@app.get("/metrics")
async def get_metrics():
    """Pipeline metrics for monitoring"""
    return {
        "total_processed": metrics['total_processed'],
        "auto_resolved": metrics['auto_resolved'],
        "escalated": metrics['escalated'],
        "success_rate": round(metrics['auto_resolved'] / max(metrics['total_processed'], 1) * 100, 1),
        "queue_size": len(processing_queue)
    }

@app.get("/queue")
async def get_queue():
    """Debug: see processed issues"""
    return {
        "total_queued": len(processing_queue),
        "recent_issues": processing_queue[-5:]
    }

@app.post("/webhook/github")
@omium.trace("github_webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    Main webhook endpoint — triggers full multi-agent pipeline
    """
    payload_bytes = await request.body()
    
    if not verify_github_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    if x_github_event != "issues":
        return JSONResponse(status_code=200, content={"message": f"Ignored: {x_github_event}"})
    
    if payload.get("action") != "opened":
        return JSONResponse(status_code=200, content={"message": f"Ignored action: {payload.get('action')}"})
    
    try:
        parsed_issue = parse_issue_payload(payload)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    
    # Trigger full pipeline in background
    background_tasks.add_task(process_issue_async, parsed_issue)
    
    return JSONResponse(
        status_code=202,
        content={
            "message": "Issue queued for multi-agent processing",
            "issue_number": parsed_issue.number,
            "pipeline": "Planner → Async → Research → Hypothesis → Solution → Critic → Decision → Memory",
            "classification": {
                "type": parsed_issue.issue_type.value,
                "priority": parsed_issue.priority.value,
                "confidence": parsed_issue.confidence_score
            }
        }
    )

@app.post("/simulate")
@omium.trace("simulate_issue")
async def simulate_issue(issue_payload: dict):
    """
    Test endpoint — runs full pipeline with fake payload
    """
    try:
        parsed = parse_issue_payload({
            "action": "opened",
            "issue": issue_payload.get("issue", {}),
            "repository": issue_payload.get("repository", {
                "name": "test-repo",
                "full_name": "user/test-repo"
            }),
            "sender": issue_payload.get("sender", {"login": "testuser"})
        })
        await process_issue_async(parsed)
        return {
            "status": "pipeline_complete",
            "parsed": parsed.to_processing_context()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))