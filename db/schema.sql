-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    experience_level VARCHAR(50) NOT NULL,
    salary_range VARCHAR(100),
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    benefits TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    location VARCHAR(255),
    current_title VARCHAR(255),
    resume_path TEXT,
    raw_text TEXT,
    resume_vector vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create extension for vector operations if it doesn't exist
CREATE EXTENSION IF NOT EXISTS vector;

-- Applications table to track job applications
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Create index on vector column for faster similarity search
CREATE INDEX IF NOT EXISTS resume_vector_idx ON candidates USING ivfflat (resume_vector vector_cosine_ops);

-- Analysis Results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    technical_skills TEXT,
    experience_level TEXT,
    education_level TEXT,
    key_achievements TEXT,
    domain_expertise TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Job Matches table
CREATE TABLE IF NOT EXISTS job_matches (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score INTEGER,
    reasoning TEXT,
    key_matches TEXT,
    skill_gaps TEXT,
    match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Screening Reports table
CREATE TABLE IF NOT EXISTS screening_reports (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    qualification_score INTEGER,
    qualification_analysis TEXT,
    experience_score INTEGER,
    experience_analysis TEXT,
    skill_match_score INTEGER,
    strengths TEXT,
    gaps TEXT,
    cultural_fit_indicators TEXT,
    red_flags TEXT,
    screening_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    candidate_strengths TEXT,
    development_areas TEXT,
    best_fit_roles TEXT,
    immediate_next_steps TEXT,
    long_term_development TEXT,
    suggested_resources TEXT,
    hiring_decision TEXT,
    decision_rationale TEXT,
    compensation_range TEXT,
    growth_path TEXT,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);