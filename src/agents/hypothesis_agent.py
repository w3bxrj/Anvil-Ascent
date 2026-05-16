from typing import List, Dict

class HypothesisAgent:

    """
    Creates multiple hypotheses, tests against evidence, picks best
    """

    def generate_hypotheses(self, issue_title: str, issue_body: str,

                         keywords: List[str], research_files: List[Dict]) -> Dict:

        """
        Generate 2-3 competing hypotheses, score them
        """

        hypotheses = []

        h1 = {

            "theory": f"Issue caused by missing null check in {keywords[0] if keywords else 'relevant'} flow",

            "evidence": [],

            "confidence": 0,

            "test": "Check if null check exists in retrieved files"

        }

        h2 = {

            "theory": "State not properly initialized before component render",

            "evidence": [],

            "confidence": 0,

            "test": "Check initialization order in lifecycle methods"

        }

        h3 = {

            "theory": "Async operation completes after component unmount",

            "evidence": [],

            "confidence": 0,

            "test": "Check cleanup in useEffect / componentWillUnmount"

        }

        for h in [h1, h2, h3]:

            for file in research_files:

                content = file.get('content', '').lower()

                if 'null' in content and 'null' in h['theory']:

                    h['confidence'] += 20

                    h['evidence'].append(file['file_path'])

                if 'async' in content or 'await' in content or 'useeffect' in content:

                    if 'async' in h['theory'] or 'unmount' in h['theory']:

                        h['confidence'] += 20

                        h['evidence'].append(file['file_path'])

                if 'state' in content or 'usestate' in content:

                    if 'state' in h['theory']:

                        h['confidence'] += 20

                        h['evidence'].append(file['file_path'])

        best = max([h1, h2, h3], key=lambda x: x['confidence'])

        return {

            "best_hypothesis": best,

            "all_hypotheses": [h1, h2, h3],

            "reasoning": f"Selected: {best['theory']} (confidence: {best['confidence']}%)"

        }

hypothesis_agent = HypothesisAgent()
