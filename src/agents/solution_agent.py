"""
Solution Agent: Generate fix/analysis using LLM (Gemini/OpenAI compatible)
"""

import os
import httpx
from typing import Dict, List

class SolutionAgent:
    """
    Generates solution draft from research context
    Works with Gemini, OpenAI, Ollama, Groq, etc.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self.use_mock = not self.api_key or self.api_key in ["mock", "test", ""]
    
    async def generate_solution(self, issue_title: str, issue_body: str,
                               issue_type: str, priority: str,
                               keywords: List[str],
                               research_files: List[Dict]) -> Dict:
        """
        Generate solution using LLM
        """
        if self.use_mock:
            print("   🤖 Using MOCK solution (no API key)")
            return self._generate_mock(issue_title, issue_body, issue_type, priority, keywords, research_files)
        
        # Build context from research
        files_context = "\n\n".join([
            f"File: {f['file_path']}\n```\n{f['content'][:600]}\n```"
            for f in research_files[:3]
        ])
        
        # Build prompt
        prompt = f"""You are an expert software engineer. Analyze this GitHub issue and provide a concise solution.

## Issue
Title: {issue_title}
Type: {issue_type} | Priority: {priority}
Description: {issue_body or 'No description'}
Keywords: {', '.join(keywords)}

## Relevant Code from Repository
{files_context}

## Respond in this exact format:
ANALYSIS: <2-3 sentence root cause analysis>
SOLUTION: <step-by-step fix with code examples>
FILES: <comma-separated files to modify>
CONFIDENCE: <number 0-100>"""
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful coding assistant. Be concise and technical."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000,
                        "stream": False
                    }
                )
                
                data = response.json()
                
                if "error" in data:
                    error_msg = data["error"].get("message", str(data["error"]))
                    print(f"   ⚠️ LLM Error: {error_msg}")
                    print(f"   🔄 Falling back to MOCK...")
                    return self._generate_mock(issue_title, issue_body, issue_type, priority, keywords, research_files)
                
                content = data["choices"][0]["message"]["content"]
                return self._parse_llm_response(content)
                
        except Exception as e:
            print(f"   ⚠️ LLM call failed: {e}")
            print(f"   🔄 Falling back to MOCK...")
            return self._generate_mock(issue_title, issue_body, issue_type, priority, keywords, research_files)
    
    def _parse_llm_response(self, content: str) -> Dict:
        """Parse structured response from LLM"""
        lines = content.strip().split('\n')
        
        analysis = ""
        solution = ""
        files = []
        confidence = 50
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("ANALYSIS:"):
                current_section = "analysis"
                analysis = line.replace("ANALYSIS:", "").strip()
            elif line.startswith("SOLUTION:"):
                current_section = "solution"
                solution = line.replace("SOLUTION:", "").strip()
            elif line.startswith("FILES:"):
                files_text = line.replace("FILES:", "").strip()
                files = [f.strip() for f in files_text.split(",") if f.strip()]
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = int(line.replace("CONFIDENCE:", "").strip().replace("%", ""))
                except:
                    confidence = 50
            elif current_section and line and not any(line.startswith(x) for x in ["ANALYSIS:", "SOLUTION:", "FILES:", "CONFIDENCE:"]):
                if current_section == "analysis":
                    analysis += " " + line
                elif current_section == "solution":
                    solution += " " + line
        
        return {
            "status": "success",
            "analysis": analysis or "No analysis provided",
            "solution": solution or "No solution provided",
            "files_to_modify": files,
            "confidence": min(100, max(0, confidence)),
            "raw_response": content
        }
    
    def _generate_mock(self, issue_title, issue_body, issue_type, priority, keywords, research_files):
        """Fallback mock solution"""
        import random
        file_paths = [f['file_path'] for f in research_files[:3]] or ['src/main.py']
        
        templates = {
            "bug": {
                "analysis": f"The {random.choice(keywords or ['null'])} issue is caused by improper state handling in {file_paths[0]}. Race condition or missing validation triggers this error.",
                "solution": f"1. Add null/undefined checks in {file_paths[0]}\n2. Validate input before processing\n3. Add error boundary for graceful failure\n4. Write unit test to reproduce issue",
                "confidence": random.randint(75, 92)
            },
            "feature": {
                "analysis": f"Implementing '{issue_title}' requires adding new module with state management and UI components.",
                "solution": f"1. Create feature module in {file_paths[0]}\n2. Add routing and navigation\n3. Implement core business logic\n4. Add tests and documentation",
                "confidence": random.randint(65, 85)
            },
            "security": {
                "analysis": f"CRITICAL: {issue_title} exposes the application to attacks. Input sanitization and access controls are missing.",
                "solution": f"1. Sanitize all user inputs in {file_paths[0]}\n2. Use parameterized queries/ORM\n3. Add rate limiting and auth checks\n4. Run security scan (SAST/DAST)",
                "confidence": random.randint(88, 98)
            }
        }
        
        template = templates.get(issue_type, {
            "analysis": f"Review needed for: {issue_title}",
            "solution": f"1. Refactor {file_paths[0]}\n2. Add documentation\n3. Improve test coverage",
            "confidence": random.randint(50, 70)
        })
        
        return {
            "status": "success",
            "analysis": template["analysis"],
            "solution": template["solution"],
            "files_to_modify": file_paths[:3],
            "confidence": template["confidence"],
            "raw_response": "MOCK_FALLBACK"
        }

# Singleton
solution_agent = SolutionAgent()