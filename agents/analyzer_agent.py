from typing import Dict, Any
from .base_agent import BaseAgent


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Education level
            4. Experience level (Junior/Mid-level/Senior)
            5. Key achievements
            6. Domain expertise
            
            Format the output as structured data.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the extracted resume data"""
        print("🔍 Analyzer: Analyzing candidate profile")

        extracted_data = eval(messages[-1]["content"])

        # Get structured analysis from OpenAI
        analysis_prompt = f"""
        Analyze this resume data and return a JSON object with the following structure:
        {{
            "technical_skills": ["skill1", "skill2"],
            "years_of_experience": number,
            "education_level": "string",
            "experience_level": "Junior/Mid-level/Senior",
            "key_achievements": ["achievement1", "achievement2"],
            "domain_expertise": ["domain1", "domain2"]
        }}

        Resume data:
        {extracted_data}
        """

        analysis = self._query_openai(analysis_prompt)

        return {
            "analysis": analysis,
            "analysis_status": "completed"
        }
