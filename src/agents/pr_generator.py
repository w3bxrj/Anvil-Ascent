from typing import Dict, List

class PRGenerator:

    """
    Generates unified diff patches for suggested fixes
    """

    def generate_patch(self, file_path: str, original_content: str,

                      solution: Dict) -> str:

        """
        Create git-style diff for the fix
        """

        lines = original_content.split('\n')

        patch_lines = []

        in_function = False

        function_name = self._extract_function_name(solution.get('solution', ''))

        for i, line in enumerate(lines):

            if function_name and function_name in line:

                in_function = True

            if in_function and ('return' in line or 'pass' in line):

                patch_lines.append(f"-{line}")

                patch_lines.append(f"+    # TODO: Add validation per AI suggestion")

                patch_lines.append(f"+{line}")

                in_function = False

            else:

                patch_lines.append(f" {line}")

        return f"""```diff
--- a/

      {file_path}
+++ b/

      {file_path}
@@ -1,

      {len(lines)} +1,{len(lines)+2} @@

{chr(10).join(patch_lines)}
```

   """

    def _extract_function_name(self, solution_text: str) -> str:

        """Extract function name from solution"""

        import re

        matches = re.findall(r'(?:function|def|method)\s+(\w+)', solution_text, re.IGNORECASE)

        return matches[0] if matches else ""

    def format_pr_description(self, issue_number: int, issue_title: str,

                             solution: Dict, critic_result: Dict) -> str:

        """Format PR description with AI context"""

        return f"""## 🤖 AI-Generated Fix for #{issue_number}

**Original Issue:** 

                    {issue_title}

### 🔍 Analysis

{solution.get('analysis', 'N/A')}

### 💡 Proposed Solution

{solution.get('solution', 'N/A')}

### ✅ Validation
- Critic Score: 

                {critic_result['scores']['overall']:.0f}/100
- Verdict: 

           {critic_result['verdict']}

### 🎯 Confidence: 

                  {solution.get('confidence', 0)}%

---
*This PR was drafted by Autonomous Issue Resolver. Human review required before merge.*

"""

pr_generator = PRGenerator()
