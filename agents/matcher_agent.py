from typing import Dict, Any
from .base_agent import BaseAgent
from db.database import JobDatabase
import json


class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions="""Match candidate profiles with job positions.
            Consider: skills match, experience level, location preferences.
            Provide detailed reasoning and compatibility scores.
            Return matches in JSON format with title, match_score, and location fields.""",
        )
        self.db = JobDatabase()

    async def run(self, messages: list) -> Dict[str, Any]:
        """Match candidate with available positions"""
        print("🎯 Matcher: Finding suitable job matches")

        # Get candidate profile from previous step
        candidate_data = eval(messages[-1]["content"])

        # Get available jobs from database
        available_jobs = self.db.get_all_jobs()

        # Create matching prompt
        matching_prompt = f"""
        Given this candidate profile and list of available jobs, find the best matches.
        Return a JSON array of matches with scores and reasoning.

        Candidate Profile:
        {candidate_data}

        Available Jobs:
        {json.dumps(available_jobs, indent=2)}

        Return format:
        [
            {{
                "job_id": "string",
                "match_score": number (0-100),
                "reasoning": "string explaining the match",
                "key_matches": ["skill1", "skill2"],
                "gaps": ["missing_skill1", "missing_skill2"]
            }}
        ]
        """

        # Get matches from OpenAI
        matches = self._query_openai(matching_prompt)

        return {
            "matches": matches,
            "matching_status": "completed"
        }
