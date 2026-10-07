import enum
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, DateTime, 
    Enum, ForeignKey, CheckConstraint, func, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SkillSource(str, enum.Enum):
    RESUME = "RESUME"
    SELF_ASSESSMENT = "SELF_ASSESSMENT"
    ASSESSMENT = "ASSESSMENT"
    PROJECT = "PROJECT"
    COURSE = "COURSE"
    ADMIN = "ADMIN"

class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ValidationStatus(str, enum.Enum):
    AGREED = "AGREED"
    RECONCILED = "RECONCILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

# ----------------------------------------------------------------------------
# Student & Resume
# ----------------------------------------------------------------------------
class Student(Base):
    __tablename__ = "STUDENT"

    student_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=True)
    cgpa = Column(Numeric(3, 2), nullable=True)
    preferred_location = Column(String(255), nullable=True)
    target_role = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    resumes = relationship("Resume", back_populates="student", cascade="all, delete-orphan")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    learning_progress = relationship("LearningProgress", back_populates="student", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="student", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "RESUME"

    resume_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("STUDENT.student_id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    parsed_text = Column(Text, nullable=True)
    parser_version = Column(String(50), default="v1.0")
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)

    student = relationship("Student", back_populates="resumes")

# ----------------------------------------------------------------------------
# Skill & Aliases
# ----------------------------------------------------------------------------
class Skill(Base):
    __tablename__ = "SKILL"

    skill_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skill_name = Column(String(150), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, default=3)
    domain = Column(String(100), default="General")
    created_at = Column(DateTime, server_default=func.now())

    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    job_skills = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")
    course_skills = relationship("CourseSkill", back_populates="skill", cascade="all, delete-orphan")

class SkillAlias(Base):
    __tablename__ = "SKILL_ALIAS"

    alias_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), nullable=False)
    alias_name = Column(String(150), nullable=False, unique=True, index=True)

    skill = relationship("Skill", back_populates="aliases")

# ----------------------------------------------------------------------------
# Student Skill Competency State
# ----------------------------------------------------------------------------
class StudentSkill(Base):
    __tablename__ = "STUDENT_SKILL"

    student_id = Column(Integer, ForeignKey("STUDENT.student_id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), primary_key=True, index=True)
    proficiency_level = Column(Numeric(3, 2), nullable=False, default=0.00)
    confidence_score = Column(Numeric(3, 2), default=1.00)
    source = Column(Enum(SkillSource), default=SkillSource.SELF_ASSESSMENT)
    evidence_text = Column(Text, nullable=True)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")

# ----------------------------------------------------------------------------
# Company & Job
# ----------------------------------------------------------------------------
class Company(Base):
    __tablename__ = "COMPANY"

    company_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    industry = Column(String(150), nullable=True)
    location = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "JOB"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("COMPANY.company_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    job_type = Column(String(50), default="Full-time")
    minimum_cgpa = Column(Numeric(3, 2), default=0.00)
    experience_requirement = Column(String(100), default="Entry Level")
    posted_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    source = Column(String(100), default="INTERNAL")
    source_job_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="jobs")
    required_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")

class JobSkill(Base):
    __tablename__ = "JOB_SKILL"

    job_id = Column(Integer, ForeignKey("JOB.job_id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), primary_key=True, index=True)
    required_proficiency = Column(Numeric(3, 2), nullable=False)
    importance_weight = Column(Numeric(5, 4), nullable=False)
    is_mandatory = Column(Boolean, default=False)

    job = relationship("Job", back_populates="required_skills")
    skill = relationship("Skill", back_populates="job_skills")

# ----------------------------------------------------------------------------
# Course & Prerequisites
# ----------------------------------------------------------------------------
class Course(Base):
    __tablename__ = "COURSE"

    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(255), nullable=False)
    provider = Column(String(150), nullable=False)
    difficulty = Column(String(50), default="Intermediate")
    duration_hours = Column(Integer, nullable=False, default=10)
    course_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    course_skills = relationship("CourseSkill", back_populates="course", cascade="all, delete-orphan")
    learning_progress = relationship("LearningProgress", back_populates="course", cascade="all, delete-orphan")

class CourseSkill(Base):
    __tablename__ = "COURSE_SKILL"

    course_id = Column(Integer, ForeignKey("COURSE.course_id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), primary_key=True, index=True)
    target_proficiency = Column(Numeric(3, 2), nullable=False, default=3.00)
    coverage_level = Column(Numeric(3, 2), default=1.00)

    course = relationship("Course", back_populates="course_skills")
    skill = relationship("Skill", back_populates="course_skills")

class SkillPrerequisite(Base):
    __tablename__ = "SKILL_PREREQUISITE"

    skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), primary_key=True)
    prerequisite_skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), primary_key=True)
    relationship_strength = Column(Numeric(3, 2), default=1.00)

# ----------------------------------------------------------------------------
# Learning Progress
# ----------------------------------------------------------------------------
class LearningProgress(Base):
    __tablename__ = "LEARNING_PROGRESS"

    progress_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("STUDENT.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("COURSE.course_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    completion_percentage = Column(Numeric(5, 2), default=0.00)
    assessment_score = Column(Numeric(5, 2), nullable=True)
    started_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    time_spent_hours = Column(Numeric(6, 2), default=0.00)

    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_student_course"),)

    student = relationship("Student", back_populates="learning_progress")
    course = relationship("Course", back_populates="learning_progress")

# ----------------------------------------------------------------------------
# Match Results
# ----------------------------------------------------------------------------
class MatchResult(Base):
    __tablename__ = "MATCH_RESULT"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("STUDENT.student_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("JOB.job_id", ondelete="CASCADE"), nullable=False)
    weighted_score = Column(Numeric(5, 2), nullable=False)
    semantic_score = Column(Numeric(5, 2), nullable=True)
    llm_score = Column(Numeric(5, 2), nullable=True)
    final_score = Column(Numeric(5, 2), nullable=False)
    difference = Column(Numeric(5, 2), default=0.00)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.AGREED)
    model_version = Column(String(50), default="v1.0-baseline")
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="match_results")
    job = relationship("Job")
    skill_results = relationship("MatchSkillResult", back_populates="match_result", cascade="all, delete-orphan")

class MatchSkillResult(Base):
    __tablename__ = "MATCH_SKILL_RESULT"

    match_id = Column(Integer, ForeignKey("MATCH_RESULT.match_id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("SKILL.skill_id", ondelete="CASCADE"), primary_key=True)
    required_level = Column(Numeric(3, 2), nullable=False)
    student_level = Column(Numeric(3, 2), nullable=False)
    skill_weight = Column(Numeric(5, 4), nullable=False)
    skill_score = Column(Numeric(5, 2), nullable=False)
    gap = Column(Numeric(3, 2), nullable=False)
    llm_level = Column(Numeric(3, 2), nullable=True)
    llm_confidence = Column(Numeric(3, 2), nullable=True)
    evidence = Column(Text, nullable=True)

    match_result = relationship("MatchResult", back_populates="skill_results")
    skill = relationship("Skill")
