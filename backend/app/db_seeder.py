from sqlalchemy.orm import Session
from app.models.nexus_models import (
    Student, Skill, SkillAlias, Company, Job, JobSkill, 
    Course, CourseSkill, SkillPrerequisite, StudentSkill, SkillSource
)

def seed_database_if_empty(db: Session):
    """
    Automatically seeds initial benchmark data if database tables are empty.
    Ensures zero manual database setup is required!
    """
    # Check if skills exist
    if db.query(Skill).count() > 0:
        return # Database already seeded

    print("Seeding NEXUS database with benchmark skills, jobs, courses, and student profile...")

    # 1. Seed Skills
    skills_data = [
        (1, 'Python', 'Programming Language', 'General purpose programming language widely used in Web, Data & AI', 2, 'Software Engineering'),
        (2, 'SQL', 'Database', 'Structured Query Language for managing relational databases', 2, 'Data Engineering'),
        (3, 'Django', 'Web Framework', 'High-level Python web framework encouraging rapid development', 3, 'Backend Development'),
        (4, 'REST API', 'Architecture', 'Representational State Transfer API design and HTTP protocols', 3, 'Software Engineering'),
        (5, 'Git', 'Version Control', 'Distributed version control system for tracking source code changes', 1, 'DevOps & Tooling'),
        (6, 'Docker', 'DevOps & Containerization', 'Container platform for packaging application dependencies', 3, 'DevOps'),
        (7, 'React', 'Frontend Framework', 'JavaScript library for building dynamic user interfaces', 3, 'Frontend Development'),
        (8, 'TypeScript', 'Programming Language', 'Typed superset of JavaScript compiling to plain JS', 3, 'Software Engineering'),
        (9, 'FastAPI', 'Web Framework', 'Modern, high-performance web framework for Python REST APIs', 3, 'Backend Development'),
        (10, 'Machine Learning', 'Data Science & AI', 'Predictive modeling, statistical algorithms, and data pattern analysis', 4, 'Data Science')
    ]

    for item in skills_data:
        db.add(Skill(
            skill_id=item[0], skill_name=item[1], category=item[2], 
            description=item[3], difficulty=item[4], domain=item[5]
        ))
    db.commit()

    # 2. Seed Skill Aliases
    aliases = [
        (1, 'Python 3'), (1, 'Python programming'), (1, 'Python scripting'),
        (2, 'Relational Database'), (2, 'SQL Querying'),
        (3, 'Django framework'),
        (4, 'RESTful services'), (4, 'REST API development'), (4, 'RESTful API'),
        (5, 'Git version control'), (5, 'GitHub'),
        (6, 'Docker containers'), (6, 'Containerization'),
        (7, 'React.js'), (7, 'ReactJS'),
        (8, 'TS'), (9, 'Fast API'), (10, 'ML')
    ]
    for skill_id, alias_name in aliases:
        db.add(SkillAlias(skill_id=skill_id, alias_name=alias_name))
    db.commit()

    # 3. Seed Skill Prerequisites DAG
    prereqs = [
        (3, 1, 1.00), # Django requires Python
        (9, 1, 1.00), # FastAPI requires Python
        (4, 3, 0.80), # REST API builds on Django
        (6, 4, 0.70), # Docker benefits from REST API microservices
        (8, 7, 0.60), # TypeScript builds on React
        (10, 1, 0.90) # ML requires Python
    ]
    for skill_id, prereq_id, strength in prereqs:
        db.add(SkillPrerequisite(skill_id=skill_id, prerequisite_skill_id=prereq_id, relationship_strength=strength))
    db.commit()

    # 4. Seed Companies & Jobs
    comp1 = Company(company_id=1, company_name='Nexus AI Labs', industry='AI & Software', location='Remote', website='https://nexus-ai.labs')
    comp2 = Company(company_id=2, company_name='CloudScale Systems', industry='Cloud', location='Seattle, WA', website='https://cloudscale.io')
    db.add(comp1)
    db.add(comp2)
    db.commit()

    job1 = Job(
        job_id=1, company_id=1, title='Backend Developer', 
        description='Build scalable Python web services, RESTful APIs, and database integrations using Django & Docker.',
        location='Remote', job_type='Full-time', minimum_cgpa=7.00, experience_requirement='0-2 years',
        source='INTERNAL', source_job_id='JOB-NEXUS-001'
    )
    db.add(job1)
    db.commit()

    # Job 1 Skill Weights total exactly 1.0000 (30% + 20% + 20% + 15% + 10% + 5%)
    job_skills = [
        (1, 1, 5.00, 0.3000, True),  # Python (30%)
        (1, 2, 4.00, 0.2000, True),  # SQL (20%)
        (1, 3, 4.00, 0.2000, False), # Django (20%)
        (1, 4, 3.00, 0.1500, False), # REST API (15%)
        (1, 5, 3.00, 0.1000, False), # Git (10%)
        (1, 6, 2.00, 0.0500, False)  # Docker (5%)
    ]
    for j_id, s_id, req_lvl, weight, is_mand in job_skills:
        db.add(JobSkill(job_id=j_id, skill_id=s_id, required_proficiency=req_lvl, importance_weight=weight, is_mandatory=is_mand))
    db.commit()

    # 5. Seed Courses & Course Skills
    courses_data = [
        (1, 'Python Core & Advanced Architecture', 'NEXUS Academy', 'Beginner to Intermediate', 20, 'https://nexus.academy/courses/python-core'),
        (2, 'SQL & Relational Database Mastery', 'DataCamp Partner', 'Intermediate', 15, 'https://datacamp.com/sql-mastery'),
        (3, 'Django Web Framework Fundamentals', 'Coursera Enterprise', 'Intermediate', 25, 'https://coursera.org/django-fundamentals'),
        (4, 'Building Scalable REST APIs', 'NEXUS Academy', 'Intermediate', 12, 'https://nexus.academy/courses/rest-apis'),
        (5, 'Git & GitHub Workflow Professional', 'Udemy Tech', 'Beginner', 8, 'https://udemy.com/git-github-professional'),
        (6, 'Docker Essentials for Developers', 'Pluralsight', 'Intermediate', 14, 'https://pluralsight.com/docker-essentials')
    ]
    for c_id, name, prov, diff, dur, url in courses_data:
        db.add(Course(course_id=c_id, course_name=name, provider=prov, difficulty=diff, duration_hours=dur, course_url=url))
    db.commit()

    course_skills = [
        (1, 1, 4.50, 0.95), (2, 2, 4.00, 0.90), (3, 3, 4.00, 0.90),
        (4, 4, 3.50, 0.85), (4, 9, 4.00, 0.80), (5, 5, 4.00, 1.00), (6, 6, 3.50, 0.90)
    ]
    for c_id, s_id, target_lvl, cov in course_skills:
        db.add(CourseSkill(course_id=c_id, skill_id=s_id, target_proficiency=target_lvl, coverage_level=cov))
    db.commit()

    # 6. Seed Student Shrinithish
    student = Student(
        student_id=101, name='Shrinithish', email='shrinithish@nexus.edu',
        password_hash='$2b$12$eWzYqY6qHk5H8.7f8.zOe.s0N7S4bN8F4bN8F4bN8F4bN8F4bN8F',
        graduation_year=2026, cgpa=8.50, preferred_location='Remote', target_role='Backend Developer'
    )
    db.add(student)
    db.commit()

    # Shrinithish's Skills: Python=4/5, SQL=4/5, Git=3/3, Django=2/5, REST API=3/3, Docker=0/5
    student_skills = [
        (101, 1, 4.00, 0.95, SkillSource.RESUME, 'Built python automation scripts and data structures'),
        (101, 2, 4.00, 0.90, SkillSource.ASSESSMENT, 'Passed database query assessment with 90% score'),
        (101, 3, 2.00, 0.70, SkillSource.RESUME, 'Basic Django project'),
        (101, 4, 3.00, 0.85, SkillSource.PROJECT, 'Built REST endpoint service'),
        (101, 5, 3.00, 0.90, SkillSource.RESUME, 'Active GitHub profile'),
        (101, 6, 0.00, 0.00, SkillSource.RESUME, 'No evidence detected')
    ]
    for st_id, s_id, prof, conf, src, ev in student_skills:
        db.add(StudentSkill(student_id=st_id, skill_id=s_id, proficiency_level=prof, confidence_score=conf, source=src, evidence_text=ev))
    db.commit()

    print("Database seeding completed successfully.")
