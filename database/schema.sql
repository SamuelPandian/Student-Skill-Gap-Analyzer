-- ============================================================================
-- NEXUS Database Schema (MySQL 8.0+)
-- Database-Centric Hybrid AI Career-Readiness System
-- ============================================================================

CREATE DATABASE IF NOT EXISTS nexus_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE nexus_db;

-- Disable foreign key checks for table setup
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS MATCH_SKILL_RESULT;
DROP TABLE IF EXISTS MATCH_RESULT;
DROP TABLE IF EXISTS LEARNING_PROGRESS;
DROP TABLE IF EXISTS SKILL_PREREQUISITE;
DROP TABLE IF EXISTS COURSE_SKILL;
DROP TABLE IF EXISTS COURSE;
DROP TABLE IF EXISTS JOB_SKILL;
DROP TABLE IF EXISTS JOB;
DROP TABLE IF EXISTS COMPANY;
DROP TABLE IF EXISTS STUDENT_SKILL;
DROP TABLE IF EXISTS SKILL_ALIAS;
DROP TABLE IF EXISTS SKILL;
DROP TABLE IF EXISTS RESUME;
DROP TABLE IF EXISTS STUDENT;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. STUDENT Table
-- ----------------------------------------------------------------------------
CREATE TABLE STUDENT (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    graduation_year INT NULL,
    cgpa DECIMAL(3, 2) NULL CHECK (cgpa >= 0.00 AND cgpa <= 10.00),
    preferred_location VARCHAR(255) NULL,
    target_role VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_email (email),
    INDEX idx_student_target_role (target_role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. RESUME Table
-- ----------------------------------------------------------------------------
CREATE TABLE RESUME (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_text LONGTEXT NULL,
    parser_version VARCHAR(50) DEFAULT 'v1.0',
    processing_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    INDEX idx_resume_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. SKILL & SKILL_ALIAS Tables (Canonical Skill Vocabulary)
-- ----------------------------------------------------------------------------
CREATE TABLE SKILL (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(150) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    description TEXT NULL,
    difficulty INT DEFAULT 3 CHECK (difficulty BETWEEN 1 AND 5),
    domain VARCHAR(100) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_skill_name (skill_name),
    INDEX idx_skill_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE SKILL_ALIAS (
    alias_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    alias_name VARCHAR(150) NOT NULL UNIQUE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE,
    INDEX idx_alias_name (alias_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 4. STUDENT_SKILL Table (Student Competency State)
-- ----------------------------------------------------------------------------
CREATE TABLE STUDENT_SKILL (
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level DECIMAL(3, 2) NOT NULL DEFAULT 0.00 CHECK (proficiency_level >= 0.00 AND proficiency_level <= 5.00),
    confidence_score DECIMAL(3, 2) DEFAULT 1.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
    source ENUM('RESUME', 'SELF_ASSESSMENT', 'ASSESSMENT', 'PROJECT', 'COURSE', 'ADMIN') DEFAULT 'SELF_ASSESSMENT',
    evidence_text TEXT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, skill_id),
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE,
    INDEX idx_student_skill_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 5. COMPANY & JOB Tables
-- ----------------------------------------------------------------------------
CREATE TABLE COMPANY (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(150) NULL,
    location VARCHAR(255) NULL,
    website VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE JOB (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NULL,
    job_type VARCHAR(50) DEFAULT 'Full-time',
    minimum_cgpa DECIMAL(3, 2) DEFAULT 0.00,
    experience_requirement VARCHAR(100) DEFAULT 'Entry Level',
    posted_date DATE NULL,
    deadline DATE NULL,
    source VARCHAR(100) DEFAULT 'INTERNAL',
    source_job_id VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id) ON DELETE CASCADE,
    INDEX idx_job_title (title),
    INDEX idx_job_company (company_id),
    INDEX idx_job_source (source_job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 6. JOB_SKILL Table (Required Competencies for Role)
-- ----------------------------------------------------------------------------
CREATE TABLE JOB_SKILL (
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    required_proficiency DECIMAL(3, 2) NOT NULL CHECK (required_proficiency >= 1.00 AND required_proficiency <= 5.00),
    importance_weight DECIMAL(5, 4) NOT NULL CHECK (importance_weight >= 0.0000 AND importance_weight <= 1.0000),
    is_mandatory BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES JOB(job_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE,
    INDEX idx_job_skill_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 7. COURSE & COURSE_SKILL Tables
-- ----------------------------------------------------------------------------
CREATE TABLE COURSE (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    provider VARCHAR(150) NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'Intermediate',
    duration_hours INT NOT NULL DEFAULT 10,
    course_url VARCHAR(512) NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE COURSE_SKILL (
    course_id INT NOT NULL,
    skill_id INT NOT NULL,
    target_proficiency DECIMAL(3, 2) NOT NULL DEFAULT 3.00 CHECK (target_proficiency >= 1.00 AND target_proficiency <= 5.00),
    coverage_level DECIMAL(3, 2) DEFAULT 1.00 CHECK (coverage_level >= 0.00 AND coverage_level <= 1.00),
    PRIMARY KEY (course_id, skill_id),
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE,
    INDEX idx_course_skill_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 8. SKILL_PREREQUISITE Table (Prerequisite DAG)
-- ----------------------------------------------------------------------------
CREATE TABLE SKILL_PREREQUISITE (
    skill_id INT NOT NULL,
    prerequisite_skill_id INT NOT NULL,
    relationship_strength DECIMAL(3, 2) DEFAULT 1.00 CHECK (relationship_strength >= 0.00 AND relationship_strength <= 1.00),
    PRIMARY KEY (skill_id, prerequisite_skill_id),
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE,
    CHECK (skill_id <> prerequisite_skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 9. LEARNING_PROGRESS Table
-- ----------------------------------------------------------------------------
CREATE TABLE LEARNING_PROGRESS (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    status ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED') DEFAULT 'NOT_STARTED',
    completion_percentage DECIMAL(5, 2) DEFAULT 0.00 CHECK (completion_percentage >= 0.00 AND completion_percentage <= 100.00),
    assessment_score DECIMAL(5, 2) NULL,
    started_date DATE NULL,
    completed_date DATE NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    time_spent_hours DECIMAL(6, 2) DEFAULT 0.00,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_course (student_id, course_id),
    INDEX idx_progress_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 10. MATCH_RESULT & MATCH_SKILL_RESULT Tables
-- ----------------------------------------------------------------------------
CREATE TABLE MATCH_RESULT (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    weighted_score DECIMAL(5, 2) NOT NULL,
    semantic_score DECIMAL(5, 2) NULL,
    llm_score DECIMAL(5, 2) NULL,
    final_score DECIMAL(5, 2) NOT NULL,
    difference DECIMAL(5, 2) DEFAULT 0.00,
    validation_status ENUM('AGREED', 'RECONCILED', 'REVIEW_REQUIRED') DEFAULT 'AGREED',
    model_version VARCHAR(50) DEFAULT 'v1.0-baseline',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES JOB(job_id) ON DELETE CASCADE,
    INDEX idx_match_student_job (student_id, job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE MATCH_SKILL_RESULT (
    match_id INT NOT NULL,
    skill_id INT NOT NULL,
    required_level DECIMAL(3, 2) NOT NULL,
    student_level DECIMAL(3, 2) NOT NULL,
    skill_weight DECIMAL(5, 4) NOT NULL,
    skill_score DECIMAL(5, 2) NOT NULL,
    gap DECIMAL(3, 2) NOT NULL,
    llm_level DECIMAL(3, 2) NULL,
    llm_confidence DECIMAL(3, 2) NULL,
    evidence TEXT NULL,
    PRIMARY KEY (match_id, skill_id),
    FOREIGN KEY (match_id) REFERENCES MATCH_RESULT(match_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
