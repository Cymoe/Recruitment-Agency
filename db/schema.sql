-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    type TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    salary_range TEXT,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    benefits TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    location TEXT,
    current_title TEXT,
    resume_path TEXT,
    raw_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Applications table to track job applications
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- Analysis Results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    technical_skills TEXT,
    experience_level TEXT,
    education_level TEXT,
    key_achievements TEXT,
    domain_expertise TEXT,
    analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Job Matches table
CREATE TABLE IF NOT EXISTS job_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score INTEGER,
    reasoning TEXT,
    key_matches TEXT,
    skill_gaps TEXT,
    match_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Screening Reports table
CREATE TABLE IF NOT EXISTS screening_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    screening_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    recommendation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);