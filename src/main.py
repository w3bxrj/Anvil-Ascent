"""
Autonomous Issue Resolver - Main FastAPI App
Step 1: Webhook Receiver + Issue Parser + Classifier
Step 2: Research Agent (Repo Indexing + RAG)
"""

import sys
import os
import hmac
import hashlib
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Ensure src is in path for imports
sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models import IssuePayload, ParsedIssue, IssueType, Priority
from src.classifier import classifier
from src.config import settings
from src.agents.research_agent import research_agent
from src.agents.solution_agent import solution_agent
from src.agents.github_commentor import commenter

# In-memory store for MVP (replace with Redis in production)
processing_queue = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    print(f"🚀 {settings.APP_NAME} v0.1.0 starting...")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   Webhook: POST /webhook/github")
    print(f"   Health:  GET /health")
    yield
    print("👋 Server shutting down...")

app = FastAPI(
    title="Autonomous Issue Resolver",
    description="AI-powered GitHub issue investigation & resolution",
    version="0.1.0",
    lifespan=lifespan
)

def verify_github_signature(payload: bytes, signature: Optional[str]) -> bool:
    """Verify webhook signature - SKIP in dev mode"""
    if not settings.GITHUB_WEBHOOK_SECRET:
        return True  # Dev mode: no secret needed
    
    if not signature or signature == "sha256=test":
        return True  # Test mode bypass
    
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
    
    # Classify
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

async def process_issue_async(parsed: ParsedIssue):
    """
    Full pipeline: Parse → Research → Solution → Comment
    """
    print(f"\n{'='*60}")
    print(f"🔔 NEW ISSUE #{parsed.number} in {parsed.repo_full_name}")
    print(f"{'='*60}")
    print(f"📌 Title: {parsed.title}")
    print(f"🏷️  Type: {parsed.issue_type.value.upper()} | Priority: {parsed.priority.value.upper()}")
    print(f"🎯 Confidence: {parsed.confidence_score * 100}%")
    print(f"🔑 Keywords: {', '.join(parsed.extracted_keywords)}")
    print(f"🔗 URL: {parsed.url}")
    print(f"{'='*60}\n")
    
    # === STEP 2: RESEARCH ===
    local_repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    research_result = await research_agent.investigate(
        repo_full_name=parsed.repo_full_name,
        issue_title=parsed.title,
        issue_body=parsed.body or "",
        keywords=parsed.extracted_keywords,
        local_path=local_repo_path
    )
    
    if research_result["status"] != "success":
        print(f"❌ Research failed: {research_result.get('message')}")
        processing_queue.append({
            "issue_number": parsed.number,
            "status": "research_failed",
            "classification": parsed.to_processing_context()
        })
        return
    
    print(f"\n📊 RESEARCH: {research_result['context']['total_files_found']} files found")
    
    # === STEP 3: SOLUTION AGENT ===
    print(f"\n🤖 Generating solution via LLM...")
    
    solution_result = await solution_agent.generate_solution(
        issue_title=parsed.title,
        issue_body=parsed.body or "",
        issue_type=parsed.issue_type.value,
        priority=parsed.priority.value,
        keywords=parsed.extracted_keywords,
        research_files=research_result["files"]
    )
    
    if solution_result["status"] != "success":
        print(f"❌ Solution generation failed: {solution_result.get('message')}")
    else:
        print(f"\n✅ SOLUTION GENERATED:")
        print(f"   Analysis: {solution_result['analysis'][:100]}...")
        print(f"   Confidence: {solution_result['confidence']}%")
    
    # === STEP 4: POST COMMENT ===
    if solution_result["status"] == "success" and solution_result["confidence"] > 40:
        print(f"\n💬 Posting comment to GitHub...")
        
        comment_result = await commenter.post_comment(
            repo_full_name=parsed.repo_full_name,
            issue_number=parsed.number,
            solution=solution_result
        )
        
        if comment_result["posted"]:
            print(f"✅ Comment posted: {comment_result.get('comment_url', 'N/A')}")
        else:
            print(f"⚠️  Comment failed: {comment_result.get('message')}")
    else:
        print(f"⚠️  Skipping comment (low confidence or error)")
    
    # Store final result
    processing_queue.append({
        "issue_number": parsed.number,
        "status": "completed",
        "classification": parsed.to_processing_context(),
        "research": research_result,
        "solution": solution_result
    })
@app.get("/")
async def root():
    """Health check"""
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "queued_issues": len(processing_queue)
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}

@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    Main webhook endpoint for GitHub events
    """
    # Read raw payload for signature verification
    payload_bytes = await request.body()
    
    # Verify signature
    if not verify_github_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Only process 'issues' events
    if x_github_event != "issues":
        return JSONResponse(
            status_code=200,
            content={"message": f"Ignored event type: {x_github_event}"}
        )
    
    # Only process 'opened' action
    action = payload.get("action")
    if action != "opened":
        return JSONResponse(
            status_code=200,
            content={"message": f"Ignored action: {action}"}
        )
    
    # Parse and classify
    try:
        parsed_issue = parse_issue_payload(payload)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    
    # Queue for async processing (non-blocking response)
    background_tasks.add_task(process_issue_async, parsed_issue)
    
    return JSONResponse(
        status_code=202,
        content={
            "message": "Issue queued for processing",
            "issue_number": parsed_issue.number,
            "classification": {
                "type": parsed_issue.issue_type.value,
                "priority": parsed_issue.priority.value,
                "confidence": parsed_issue.confidence_score
            }
        }
    )

@app.get("/queue")
async def get_queue():
    """Debug endpoint to see queued issues"""
    return {
        "total_queued": len(processing_queue),
        "issues": processing_queue[-10:]  # Last 10
    }

@app.post("/simulate")
async def simulate_issue(issue_payload: dict):
    """
    Test endpoint — send a fake GitHub payload to test parsing
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
            "parsed": parsed.to_processing_context(),
            "classification": {
                "type": parsed.issue_type.value,
                "priority": parsed.priority.value,
                "confidence": parsed.confidence_score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))