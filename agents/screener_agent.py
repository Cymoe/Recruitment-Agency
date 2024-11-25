from typing import Dict, Any
from .base_agent import BaseAgent


class ScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Screener",
            instructions="""Screen candidates based on:
            - Qualification alignment
            - Experience relevance
            - Skill match percentage
            - Cultural fit indicators
            - Red flags or concerns
            Provide comprehensive screening reports.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Screen the candidate"""
        print("👥 Screener: Conducting initial screening")

        workflow_context = eval(messages[-1]["content"])
        
        screening_prompt = f"""
        Based on the candidate's profile and job matches, provide a comprehensive screening report.
        
        Context:
        {workflow_context}
        
        Return a JSON object with this structure:
        {{
            "qualification_alignment": {{
                "score": number (0-100),
                "analysis": "string"
            }},
            "experience_relevance": {{
                "score": number (0-100),
                "analysis": "string"
            }},
            "skill_match": {{
                "score": number (0-100),
                "strengths": ["string"],
                "gaps": ["string"]
            }},
            "cultural_fit": {{
                "indicators": ["string"],
                "concerns": ["string"]
            }},
            "red_flags": ["string"] or [],
            "overall_recommendation": "string"
        }}
        """
        
        screening_results = self._query_openai(screening_prompt)

        return {
            "screening_report": screening_results,
            "screening_status": "completed"
        }
