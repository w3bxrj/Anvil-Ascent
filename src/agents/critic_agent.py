"""
CRITIC AGENT: Validates solution quality — prevents hallucination
SUPER important for production credibility
"""

from typing import Dict, List

class CriticAgent:
    """
    Reviews solution for:
    - Code relevance (retrieved files actually match?)
    - Confidence calibration (is LLM overconfident?)
    - Contradictions (does fix contradict existing code?)
    """
    
    def evaluate(self, solution: Dict, research_files: List[Dict],
                issue_title: str, issue_body: str) -> Dict:
        """
        Returns validated solution with corrections
        """
        scores = {
            "code_relevance": 0.0,
            "confidence_calibration": 0.0,
            "contradiction_check": 0.0,
            "overall": 0.0
        }
        
        # 1. Code Relevance Check
        solution_files = solution.get('files_to_modify', [])
        research_paths = [f['file_path'] for f in research_files]
        
        matched = [f for f in solution_files if any(r in f or f in r for r in research_paths)]
        scores["code_relevance"] = len(matched) / max(len(solution_files), 1) * 100
        
        # 2. Confidence Calibration
        llm_confidence = solution.get('confidence', 50)
        
        # If no files match, confidence should be low
        if scores["code_relevance"] < 30 and llm_confidence > 70:
            scores["confidence_calibration"] = 30  # Overconfident!
            solution['confidence'] = min(llm_confidence, 40)  # Correct it
        else:
            scores["confidence_calibration"] = 80
        
        # 3. Contradiction Check (basic)
        solution_text = solution.get('solution', '').lower()
        for file in research_files:
            content = file.get('content', '').lower()
            
            # If solution suggests adding something that already exists
            if 'add' in solution_text and 'import' in solution_text:
                if 'import' in content:
                    # Might be duplicate — flag for review
                    scores["contradiction_check"] = 60
                    break
        
        # Overall score
        scores["overall"] = (scores["code_relevance"] + 
                           scores["confidence_calibration"] + 
                           scores["contradiction_check"]) / 3
        
        # Decision
        if scores["overall"] > 70:
            verdict = "PASS"
            action = "proceed"
        elif scores["overall"] > 40:
            verdict = "WARNING"
            action = "proceed_with_caution"
        else:
            verdict = "FAIL"
            action = "escalate_to_human"
        
        return {
            "scores": scores,
            "verdict": verdict,
            "action": action,
            "corrected_solution": solution,
            "feedback": f"Code relevance: {scores['code_relevance']:.0f}%. {verdict}."
        }

# Singleton
critic = CriticAgent()