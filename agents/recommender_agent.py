from typing import Dict, Any
from .base_agent import BaseAgent


class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions="""Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results
            Provide clear next steps and specific recommendations.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Generate final recommendations"""
        print("💡 Recommender: Generating final recommendations")

        workflow_context = eval(messages[-1]["content"])
        
        recommendation_prompt = f"""
        Based on the complete candidate evaluation workflow, provide final recommendations and next steps.
        
        Workflow Context:
        {workflow_context}
        
        Return a JSON object with this structure:
        {{
            "summary": {{
                "candidate_strengths": ["string"],
                "development_areas": ["string"],
                "best_fit_roles": ["string"]
            }},
            "recommendations": {{
                "immediate_next_steps": ["string"],
                "long_term_development": ["string"],
                "suggested_resources": ["string"]
            }},
            "hiring_recommendation": {{
                "decision": "Strongly Recommend/Recommend/Consider/Do Not Recommend",
                "rationale": "string",
                "suggested_compensation_range": "string",
                "potential_growth_path": "string"
            }}
        }}
        """
        
        recommendation = self._query_openai(recommendation_prompt)

        return {
            "final_recommendation": recommendation,
            "recommendation_status": "completed"
        }
