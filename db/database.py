import os
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
import logging

logger = logging.getLogger(__name__)

class JobDatabase:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.is_postgres = bool(self.db_url and self.db_url.startswith('postgres'))
        
        if not self.is_postgres:
            # Local SQLite setup
            current_dir = Path(__file__).parent
            self.db_path = current_dir / "jobs.sqlite"
            self.schema_path = current_dir / "schema.sql"
        else:
            self.schema_path = Path(__file__).parent / "schema.sql"
        
        self._init_db()

    def get_connection(self):
        """Get database connection based on environment"""
        try:
            if self.is_postgres:
                conn = psycopg2.connect(self.db_url)
                conn.cursor_factory = RealDictCursor
                return conn
            else:
                return sqlite3.connect(self.db_path)
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    def _init_db(self):
        """Initialize the database with schema"""
        try:
            if not self.schema_path.exists():
                raise FileNotFoundError(f"Schema file not found at {self.schema_path}")

            if self.is_postgres:
                # For PostgreSQL, first enable the vector extension
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        try:
                            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                            conn.commit()
                        except Exception as e:
                            logger.error(f"Error creating vector extension: {str(e)}")
                            # Continue even if vector extension fails
                            pass

            with open(self.schema_path) as f:
                schema = f.read()

            # Adjust schema for PostgreSQL if needed
            if self.is_postgres:
                schema = schema.replace('AUTOINCREMENT', 'GENERATED ALWAYS AS IDENTITY')
                schema = schema.replace('TEXT', 'VARCHAR')

            with self.get_connection() as conn:
                if self.is_postgres:
                    # Execute each statement separately for PostgreSQL
                    statements = [s.strip() for s in schema.split(';') if s.strip()]
                    with conn.cursor() as cur:
                        for statement in statements:
                            try:
                                cur.execute(statement)
                                conn.commit()
                            except Exception as e:
                                logger.error(f"Error executing statement: {str(e)}\nStatement: {statement}")
                                # Continue with next statement
                                continue
                else:
                    # SQLite can execute multiple statements
                    conn.executescript(schema)
                    conn.commit()

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def _serialize_list(self, data: List) -> str:
        """Serialize list data to JSON string"""
        return json.dumps(data) if data else "[]"

    def _deserialize_list(self, data: str) -> List:
        """Deserialize JSON string to list"""
        try:
            return json.loads(data) if data else []
        except json.JSONDecodeError:
            return []

    # Job-related methods
    def add_job(self, job_data: Dict[str, Any]) -> int:
        """Add a new job to the database"""
        query = """
        INSERT INTO jobs (
            title, company, location, type, experience_level,
            salary_range, description, requirements, benefits
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    job_data["title"],
                    job_data["company"],
                    job_data["location"],
                    job_data["type"],
                    job_data["experience_level"],
                    job_data.get("salary_range"),
                    job_data["description"],
                    self._serialize_list(job_data["requirements"]),
                    self._serialize_list(job_data.get("benefits", [])),
                ),
            )
            return cursor.lastrowid

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs from the database"""
        query = "SELECT * FROM jobs"
        
        with self.get_connection() as conn:
            if self.is_postgres:
                conn.row_factory = RealDictCursor
            else:
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "company": row["company"],
                    "location": row["location"],
                    "type": row["type"],
                    "experience_level": row["experience_level"],
                    "salary_range": row["salary_range"],
                    "description": row["description"],
                    "requirements": self._deserialize_list(row["requirements"]),
                    "benefits": self._deserialize_list(row["benefits"]),
                }
                for row in rows
            ]

    # Candidate-related methods
    def add_candidate(self, candidate_data: Dict[str, Any]) -> int:
        """Add a new candidate to the database"""
        query = """
        INSERT INTO candidates (
            name, email, phone, location, current_title,
            resume_path, raw_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    candidate_data.get("name"),
                    candidate_data.get("email"),
                    candidate_data.get("phone"),
                    candidate_data.get("location"),
                    candidate_data.get("current_title"),
                    candidate_data.get("resume_path"),
                    candidate_data.get("raw_text"),
                ),
            )
            return cursor.lastrowid

    def create_application(self, candidate_id: int) -> int:
        """Create a new application for a candidate"""
        query = "INSERT INTO applications (candidate_id) VALUES (?)"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (candidate_id,))
            return cursor.lastrowid

    def save_analysis_results(self, application_id: int, analysis_data: Dict[str, Any]):
        """Save analysis results for an application"""
        query = """
        INSERT INTO analysis_results (
            application_id, technical_skills, experience_level,
            education_level, key_achievements, domain_expertise
        ) VALUES (?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    application_id,
                    self._serialize_list(analysis_data.get("technical_skills", [])),
                    analysis_data.get("experience_level"),
                    analysis_data.get("education_level"),
                    self._serialize_list(analysis_data.get("key_achievements", [])),
                    self._serialize_list(analysis_data.get("domain_expertise", [])),
                ),
            )

    def save_job_matches(self, application_id: int, matches_data: List[Dict[str, Any]]):
        """Save job matches for an application"""
        query = """
        INSERT INTO job_matches (
            application_id, job_id, match_score, reasoning,
            key_matches, skill_gaps
        ) VALUES (?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for match in matches_data:
                cursor.execute(
                    query,
                    (
                        application_id,
                        match["job_id"],
                        match["match_score"],
                        match["reasoning"],
                        self._serialize_list(match.get("key_matches", [])),
                        self._serialize_list(match.get("gaps", [])),
                    ),
                )

    def save_screening_report(self, application_id: int, screening_data: Dict[str, Any]):
        """Save screening report for an application"""
        query = """
        INSERT INTO screening_reports (
            application_id, qualification_score, qualification_analysis,
            experience_score, experience_analysis, skill_match_score,
            strengths, gaps, cultural_fit_indicators, red_flags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    application_id,
                    screening_data["qualification_alignment"]["score"],
                    screening_data["qualification_alignment"]["analysis"],
                    screening_data["experience_relevance"]["score"],
                    screening_data["experience_relevance"]["analysis"],
                    screening_data["skill_match"]["score"],
                    self._serialize_list(screening_data["skill_match"]["strengths"]),
                    self._serialize_list(screening_data["skill_match"]["gaps"]),
                    self._serialize_list(screening_data["cultural_fit"]["indicators"]),
                    self._serialize_list(screening_data["red_flags"]),
                ),
            )

    def save_recommendation(self, application_id: int, recommendation_data: Dict[str, Any]):
        """Save recommendation for an application"""
        query = """
        INSERT INTO recommendations (
            application_id, candidate_strengths, development_areas,
            best_fit_roles, immediate_next_steps, long_term_development,
            suggested_resources, hiring_decision, decision_rationale,
            compensation_range, growth_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    application_id,
                    self._serialize_list(recommendation_data["summary"]["candidate_strengths"]),
                    self._serialize_list(recommendation_data["summary"]["development_areas"]),
                    self._serialize_list(recommendation_data["summary"]["best_fit_roles"]),
                    self._serialize_list(recommendation_data["recommendations"]["immediate_next_steps"]),
                    self._serialize_list(recommendation_data["recommendations"]["long_term_development"]),
                    self._serialize_list(recommendation_data["recommendations"]["suggested_resources"]),
                    recommendation_data["hiring_recommendation"]["decision"],
                    recommendation_data["hiring_recommendation"]["rationale"],
                    recommendation_data["hiring_recommendation"]["suggested_compensation_range"],
                    recommendation_data["hiring_recommendation"]["potential_growth_path"],
                ),
            )

    def get_application_history(self, candidate_id: int) -> List[Dict[str, Any]]:
        """Get complete application history for a candidate"""
        query = """
        SELECT 
            a.id as application_id,
            a.status,
            a.submission_date,
            ar.*,
            sr.*,
            r.*
        FROM applications a
        LEFT JOIN analysis_results ar ON a.id = ar.application_id
        LEFT JOIN screening_reports sr ON a.id = sr.application_id
        LEFT JOIN recommendations r ON a.id = r.application_id
        WHERE a.candidate_id = ?
        ORDER BY a.submission_date DESC
        """

        with self.get_connection() as conn:
            if self.is_postgres:
                conn.row_factory = RealDictCursor
            else:
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (candidate_id,))
            rows = cursor.fetchall()

            return [dict(row) for row in rows]
