-- ============================================================================
-- NEXUS Seed Data
-- Database-Centric Hybrid AI Career-Readiness System
-- ============================================================================

USE nexus_db;

-- ----------------------------------------------------------------------------
-- 1. Seed Canonical Skills & Aliases
-- ----------------------------------------------------------------------------
INSERT INTO SKILL (skill_id, skill_name, category, description, difficulty, domain) VALUES
(1, 'Python', 'Programming Language', 'General purpose programming language widely used in Web, Data & AI', 2, 'Software Engineering'),
(2, 'SQL', 'Database', 'Structured Query Language for managing relational databases', 2, 'Data Engineering'),
(3, 'Django', 'Web Framework', 'High-level Python web framework encouraging rapid development', 3, 'Backend Development'),
(4, 'REST API', 'Architecture', 'Representational State Transfer API design and HTTP protocols', 3, 'Software Engineering'),
(5, 'Git', 'Version Control', 'Distributed version control system for tracking source code changes', 1, 'DevOps & Tooling'),
(6, 'Docker', 'DevOps & Containerization', 'Container platform for packaging application dependencies', 3, 'DevOps'),
(7, 'React', 'Frontend Framework', 'JavaScript library for building dynamic user interfaces', 3, 'Frontend Development'),
(8, 'TypeScript', 'Programming Language', 'Typed superset of JavaScript compiling to plain JS', 3, 'Software Engineering'),
(9, 'FastAPI', 'Web Framework', 'Modern, high-performance web framework for Python REST APIs', 3, 'Backend Development'),
(10, 'Machine Learning', 'Data Science & AI', 'Predictive modeling, statistical algorithms, and data pattern analysis', 4, 'Data Science');

INSERT INTO SKILL_ALIAS (alias_id, skill_id, alias_name) VALUES
(1, 1, 'Python 3'),
(2, 1, 'Python programming'),
(3, 1, 'Python scripting'),
(4, 2, 'Relational Database'),
(5, 2, 'SQL Querying'),
(6, 3, 'Django framework'),
(7, 4, 'RESTful services'),
(8, 4, 'REST API development'),
(9, 4, 'RESTful API'),
(10, 5, 'Git version control'),
(11, 5, 'GitHub'),
(12, 6, 'Docker containers'),
(13, 6, 'Containerization'),
(14, 7, 'React.js'),
(15, 7, 'ReactJS'),
(16, 8, 'TS'),
(17, 9, 'Fast API'),
(18, 10, 'ML');

-- ----------------------------------------------------------------------------
-- 2. Seed Skill Prerequisites (Acyclic Graph DAG)
-- ----------------------------------------------------------------------------
INSERT INTO SKILL_PREREQUISITE (skill_id, prerequisite_skill_id, relationship_strength) VALUES
(3, 1, 1.00), -- Django requires Python
(9, 1, 1.00), -- FastAPI requires Python
(4, 3, 0.80), -- REST API strongly builds on Django / Web Frameworks
(6, 4, 0.70), -- Docker benefits from understanding REST API microservices
(8, 7, 0.60), -- TypeScript builds on React UI components
(10, 1, 0.90); -- Machine Learning requires Python proficiency

-- ----------------------------------------------------------------------------
-- 3. Seed Companies & Jobs (with 100% Normalized Weights)
-- ----------------------------------------------------------------------------
INSERT INTO COMPANY (company_id, company_name, industry, location, website) VALUES
(1, 'Nexus AI Labs', 'Artificial Intelligence & Software', 'San Francisco, CA / Remote', 'https://nexus-ai.labs'),
(2, 'CloudScale Systems', 'Cloud & Infrastructure', 'Seattle, WA', 'https://cloudscale.io'),
(3, 'DataDynamics Tech', 'Data Engineering', 'Austin, TX', 'https://datadynamics.com');

-- Job 1: Backend Developer (Exact match benchmark job from section 8 & 34 of spec)
INSERT INTO JOB (job_id, company_id, title, description, location, job_type, minimum_cgpa, experience_requirement, posted_date, deadline, source, source_job_id) VALUES
(1, 1, 'Backend Developer', 'Build scalable Python web services, RESTful APIs, and database integrations using Django & Docker.', 'Remote', 'Full-time', 7.00, '0-2 years', '2026-10-01', '2026-11-01', 'INTERNAL', 'JOB-NEXUS-001'),
(2, 2, 'Full Stack Engineer', 'Develop React modern frontends and FastAPI microservices containerized with Docker.', 'Seattle, WA', 'Full-time', 7.50, '1-3 years', '2026-10-02', '2026-11-15', 'INTERNAL', 'JOB-CLOUD-002');

-- Job 1 Skill Weights total exactly 1.0000 (30% + 20% + 20% + 15% + 10% + 5%)
INSERT INTO JOB_SKILL (job_id, skill_id, required_proficiency, importance_weight, is_mandatory) VALUES
(1, 1, 5.00, 0.3000, TRUE),  -- Python (Weight 30%)
(1, 2, 4.00, 0.2000, TRUE),  -- SQL (Weight 20%)
(1, 3, 4.00, 0.2000, FALSE), -- Django (Weight 20%)
(1, 4, 3.00, 0.1500, FALSE), -- REST API (Weight 15%)
(1, 5, 3.00, 0.1000, FALSE), -- Git (Weight 10%)
(1, 6, 2.00, 0.0500, FALSE); -- Docker (Weight 5%)

-- Job 2 Skill Weights total exactly 1.0000 (25% + 25% + 20% + 15% + 15%)
INSERT INTO JOB_SKILL (job_id, skill_id, required_proficiency, importance_weight, is_mandatory) VALUES
(2, 7, 4.00, 0.2500, TRUE),  -- React (25%)
(2, 9, 4.00, 0.2500, TRUE),  -- FastAPI (25%)
(2, 8, 3.00, 0.2000, FALSE), -- TypeScript (20%)
(2, 5, 3.00, 0.1500, FALSE), -- Git (15%)
(2, 6, 3.00, 0.1500, FALSE); -- Docker (15%)

-- ----------------------------------------------------------------------------
-- 4. Seed Courses & Course Skills
-- ----------------------------------------------------------------------------
INSERT INTO COURSE (course_id, course_name, provider, difficulty, duration_hours, course_url, description) VALUES
(1, 'Python Core & Advanced Architecture', 'NEXUS Academy', 'Beginner to Intermediate', 20, 'https://nexus.academy/courses/python-core', 'Master Python 3 syntax, OOP, datatypes, and scripting.'),
(2, 'SQL & Relational Database Mastery', 'DataCamp Partner', 'Intermediate', 15, 'https://datacamp.com/sql-mastery', 'Deep dive into complex queries, joins, indexes, and schema design.'),
(3, 'Django Web Framework Fundamentals', 'Coursera Enterprise', 'Intermediate', 25, 'https://coursera.org/django-fundamentals', 'Build robust server-side Web applications using Python & Django.'),
(4, 'Building Scalable REST APIs', 'NEXUS Academy', 'Intermediate', 12, 'https://nexus.academy/courses/rest-apis', 'Design RESTful APIs, HTTP endpoints, JSON authentication, and FastAPI.'),
(5, 'Git & GitHub Workflow Professional', 'Udemy Tech', 'Beginner', 8, 'https://udemy.com/git-github-professional', 'Master branch management, pull requests, and git rebase workflows.'),
(6, 'Docker Essentials for Developers', 'Pluralsight', 'Intermediate', 14, 'https://pluralsight.com/docker-essentials', 'Containerize applications, docker-compose configuration, and deployment.');

INSERT INTO COURSE_SKILL (course_id, skill_id, target_proficiency, coverage_level) VALUES
(1, 1, 4.50, 0.95), -- Python
(2, 2, 4.00, 0.90), -- SQL
(3, 3, 4.00, 0.90), -- Django
(4, 4, 3.50, 0.85), -- REST API
(4, 9, 4.00, 0.80), -- FastAPI
(5, 5, 4.00, 1.00), -- Git
(6, 6, 3.50, 0.90); -- Docker

-- ----------------------------------------------------------------------------
-- 5. Seed Benchmark Student & Skills (Exact Profile from Section 34 of Spec)
-- ----------------------------------------------------------------------------
-- Password: "Password123!" hashed with bcrypt / argon2 (dummy hash for seed)
INSERT INTO STUDENT (student_id, name, email, password_hash, graduation_year, cgpa, preferred_location, target_role) VALUES
(101, 'Shrinithish', 'shrinithish@nexus.edu', '$2b$12$eWzYqY6qHk5H8.7f8.zOe.s0N7S4bN8F4bN8F4bN8F4bN8F4bN8F', 2026, 8.50, 'Remote', 'Backend Developer');

-- Shrinithish's Skills: Python=4/5, SQL=4/5, Git=3/3, Django=2/5, REST API=3/3, Docker=0/5
INSERT INTO STUDENT_SKILL (student_id, skill_id, proficiency_level, confidence_score, source, evidence_text) VALUES
(101, 1, 4.00, 0.95, 'RESUME', 'Built python automation scripts and data structures'),
(101, 2, 4.00, 0.90, 'ASSESSMENT', 'Passed database query assessment with 90% score'),
(101, 3, 2.00, 0.70, 'RESUME', 'Basic Django toy app project'),
(101, 4, 3.00, 0.85, 'PROJECT', 'Built REST endpoint service for college capstone'),
(101, 5, 3.00, 0.90, 'RESUME', 'Active GitHub profile with multi-branch repositories'),
(101, 6, 0.00, 0.00, 'RESUME', 'No evidence detected');
