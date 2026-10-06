# NEXUS --- Complete Build & Implementation Specification

> **NEXUS --- Next-generation Employability, eXpertise & Upskilling
> System**

## 1. Canonical Project Definition

NEXUS is a **database-centric, hybrid AI career-readiness system**. It
models students, competencies, job requirements, learning resources,
prerequisites and learning progress in one normalized relational
database. It combines deterministic weighted skill matching, semantic
similarity, LLM-based evidence analysis, prerequisite-aware learning
paths and predictive analytics for job-match probability and
time-to-readiness.

The central closed loop is:

``` text
Student → Resume/Profile → Current Competency State → Target Job
→ Required Competencies → Skill Gap → Prerequisite-Aware Learning Path
→ Courses/Resources → Time-to-Readiness → Career Readiness + Job Match
→ Student Learns → Progress Recorded → Competency State Updated
→ Recommendations Recalculated
```

The database is the **source of truth**; ML/NLP/LLM components are the
intelligence layer.

------------------------------------------------------------------------

## 2. Frozen Architecture

``` text
                         STUDENT
                            |
              +-------------+-------------+
              |                           |
              v                           v
       Resume Upload                Target Job Selection
              |                           |
              v                           v
      Resume Processing            Job Discovery/Requirements
              |                           |
              +-------------+-------------+
                            v
                  Skill Normalization
                            |
                            v
                 +---------------------+
                 |     NEXUS MYSQL     |
                 |                     |
                 | STUDENT             |
                 | RESUME              |
                 | SKILL               |
                 | STUDENT_SKILL      |
                 | JOB / COMPANY       |
                 | JOB_SKILL           |
                 | COURSE              |
                 | COURSE_SKILL        |
                 | SKILL_PREREQUISITE  |
                 | LEARNING_PROGRESS   |
                 | MATCH_RESULT        |
                 | MATCH_SKILL_RESULT  |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 | INTELLIGENCE LAYER  |
                 |                     |
                 | Weighted Matching   |
                 | Skill Gap Engine    |
                 | Dependency Engine   |
                 | Semantic Matching   |
                 | LLM Evaluation      |
                 | ML Prediction       |
                 +----------+----------+
                            |
                            v
                 Personalized Career Engine
                            |
                            v
                    Student Dashboard
                            |
                            v
                     Student Learns
                            |
                            v
                     Progress Update
                            |
                            +------> Recalculate
```

### Architectural rule

Use **one MySQL database**, not separate job and course databases. Jobs
and courses connect through skills:

``` text
JOB → JOB_SKILL → SKILL ← COURSE_SKILL ← COURSE
```

Do not primarily model `JOB → COURSE`, because a course can support many
roles and a role requires many skills.

------------------------------------------------------------------------

# 3. User Roles

### Student

-   Register/login
-   Upload resume
-   Review/correct extracted skills
-   Set or validate proficiency
-   Select target roles
-   View jobs and requirements
-   View skill gaps
-   View learning path
-   Track course progress
-   Complete assessments
-   View readiness and match scores
-   Explore alternative career paths

### Admin

-   Manage jobs and companies
-   Manage skills and aliases
-   Manage job requirements
-   Manage courses and learning resources
-   Maintain prerequisite relationships
-   Validate imported data

### External data sources

Use only legitimately available/authorized sources: public datasets,
authorized APIs, partner feeds, or admin input. Do not build the project
around unauthorized LinkedIn/Naukri scraping.

------------------------------------------------------------------------

# 4. Resume/NLP Pipeline

``` text
PDF/DOCX Resume
      ↓
Text Extraction
      ↓
NLP/LLM Entity Extraction
      ↓
Skill + Education + Project + Experience Extraction
      ↓
Skill Normalization
      ↓
Student Competency Profile
```

Extract evidence, not blindly assumed proficiency. Example:

`Developed a Flask application` → evidence for Python/Flask/web
development, but not automatic 5/5 proficiency.

Possible sources for proficiency: - Resume evidence - Self assessment -
Technical assessment - Project evidence - Course/assessment completion

Distinguish **NOT_DETECTED** from **CONFIRMED_ZERO** where possible. A
resume not mentioning Docker does not prove zero Docker knowledge.

------------------------------------------------------------------------

# 5. Skill Normalization / Ontology

Different strings should map to one canonical skill:

``` text
Python programming / Python development / Python scripting → Python
RESTful API / REST services / REST API development → REST API
```

Canonical `SKILL` records should contain at least:

``` text
skill_id
skill_name
category
description
```

Optional:

``` text
aliases
difficulty
domain
```

This becomes the system's competency vocabulary.

------------------------------------------------------------------------

# 6. Relational Database Design

## STUDENT

``` text
student_id PK
name
email
password_hash
graduation_year
cgpa
preferred_location
target_role
created_at
```

Never store plaintext passwords.

## RESUME

``` text
resume_id PK
student_id FK
file_name
file_path/storage_reference
uploaded_at
parsed_text
parser_version
processing_status
```

## SKILL

``` text
skill_id PK
skill_name
category
description
```

## STUDENT_SKILL

``` text
student_id FK
skill_id FK
proficiency_level
confidence_score
source
last_updated
```

Recommended composite key: `(student_id, skill_id)`.

Possible sources: `RESUME`, `SELF_ASSESSMENT`, `ASSESSMENT`, `PROJECT`,
`COURSE`, `ADMIN`.

## COMPANY

``` text
company_id PK
company_name
industry
location
website
```

## JOB

``` text
job_id PK
company_id FK
title
description
location
job_type
minimum_cgpa
experience_requirement
posted_date
deadline
source
source_job_id
created_at
```

`source_job_id` helps deduplicate external jobs.

## JOB_SKILL

``` text
job_id FK
skill_id FK
required_proficiency
importance_weight
is_mandatory
```

Weights for one job should total 1.0 or 100%.

## COURSE

``` text
course_id PK
course_name
provider
difficulty
duration_hours
course_url
description
```

## COURSE_SKILL

``` text
course_id FK
skill_id FK
target_proficiency
coverage_level
```

## SKILL_PREREQUISITE

``` text
skill_id FK
prerequisite_skill_id FK
relationship_strength
```

Prefer an acyclic prerequisite graph for learning-path generation.
Detect cycles.

## LEARNING_PROGRESS

``` text
progress_id PK
student_id FK
course_id FK
status
completion_percentage
assessment_score
started_date
completed_date
last_updated
time_spent_hours
```

Statuses: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`.

------------------------------------------------------------------------

# 7. Job → Skill → Course Logic

This is the critical relationship:

``` text
JOB
 ↓
JOB_SKILL
 ↓
SKILL
 ↓
COURSE_SKILL
 ↓
COURSE
```

Example:

``` text
Backend Developer
  ├─ Python 4/5
  ├─ SQL 4/5
  ├─ Django 3/5
  └─ Docker 2/5
```

A student with Python 4/5, SQL 4/5, Django 0/5, Docker 0/5 gets Django
and Docker as gaps. NEXUS finds courses through `COURSE_SKILL` rather
than a hard-coded job-course relationship.

------------------------------------------------------------------------

# 8. Weighted Skill Matching --- FROZEN BASELINE ALGORITHM

For each required skill:

``` text
SkillScore_i = min(StudentLevel_i / RequiredLevel_i, 1)
```

Weighted contribution:

``` text
Contribution_i = SkillScore_i × Weight_i
```

Overall:

``` text
WeightedSkillScore = Σ(SkillScore_i × Weight_i)
```

Example:

  Skill         Required   Student     Weight   Contribution
  ----------- ---------- --------- ---------- --------------
  Python               5         4        30%             24
  SQL                  4         4        20%             20
  Django               4         2        20%             10
  REST API             3         3        15%             15
  Git                  3         3        10%             10
  Docker               2         0         5%              0
  **Total**                          **100%**        **79%**

Overqualification is capped at 100% for that skill. A student with 7/5
receives a skill score of 1.0, not 1.4.

Skill gap:

``` text
Gap_i = max(RequiredLevel_i - StudentLevel_i, 0)
```

------------------------------------------------------------------------

# 9. Why Weighted Matching Is the Baseline

Simple set overlap was considered but is insufficient. A missing
high-importance Python skill should not be treated as equivalent to a
missing low-importance Docker skill.

Weighted matching is: - deterministic - reproducible - explainable -
database-friendly - easy to unit test - a transparent baseline against
which AI methods can be compared

------------------------------------------------------------------------

# 10. Semantic Matching

Use embeddings to capture semantic relationships:

``` text
"RESTful services"
        ≈
"REST API development"
```

Pipeline:

``` text
Resume/skill text
      ↓
Embedding model
      ↓
Vector
      ↓
Cosine similarity
```

Cosine similarity:

``` text
cos(A,B) = (A · B) / (||A|| ||B||)
```

Potential implementation: Sentence Transformers or another embedding
model.

------------------------------------------------------------------------

# 11. LLM Evaluator

The LLM should be a **semantic evidence evaluator**, not the only
scoring authority.

Potential providers for prototyping include Gemini, Groq, or OpenRouter,
depending on current free-tier availability/limits. API providers are
interchangeable through an adapter layer.

Never expose API keys in frontend code. Use:

``` text
React → FastAPI backend → AI provider
```

not:

``` text
React → AI provider
```

Use environment variables for secrets.

------------------------------------------------------------------------

# 12. Structured LLM Output

Do not ask an LLM only:

> What is the candidate's match percentage?

Ask for evidence-level structured output:

``` json
{
  "skills": [
    {
      "skill": "Python",
      "evidence": "Developed a Flask application",
      "estimated_level": 4,
      "confidence": 0.91
    },
    {
      "skill": "Django",
      "evidence": "No direct evidence found",
      "estimated_level": 0,
      "confidence": 0.96
    }
  ]
}
```

Backend validates the JSON before using it. Do not let an LLM directly
execute SQL or arbitrarily write database records.

------------------------------------------------------------------------

# 13. Hybrid Matching Architecture

NEXUS uses three signals:

### A. Weighted Skill Matcher

Structured competency comparison.

### B. Semantic Similarity

Embedding/cosine comparison of resume/job/skill text.

### C. LLM Evidence Evaluation

Contextual interpretation of evidence.

Conceptually:

``` text
Student + Job
     ├── Weighted Matcher → 79%
     ├── Semantic Matcher → 82%
     └── LLM Evaluator    → 84%
                ↓
            Comparator
```

An initial fusion can be configured as:

``` text
FinalScore = w1*Weighted + w2*Semantic + w3*LLM
```

Do not claim that arbitrary weights such as 0.5/0.2/0.3 are
scientifically optimal. Use them only as initial configuration and
tune/validate them with data.

------------------------------------------------------------------------

# 14. LLM vs Weighted Matcher Reconciliation --- FROZEN FEATURE

Example:

``` text
Weighted = 62%
LLM = 87%
Difference = |62 - 87| = 25 percentage points
```

Define a configurable mismatch threshold, e.g. 10 percentage points for
the prototype:

``` text
if difference <= threshold:
    ACCEPT
else:
    FEEDBACK / RECONCILIATION
```

The threshold should eventually be validated experimentally.

------------------------------------------------------------------------

# 15. Feedback / Reconciliation Loop

Do NOT implement an infinite loop.

Frozen prototype:

``` text
Initial evaluation
       ↓
Compare
       ↓
Mismatch?
   ├─ No → Accept
   └─ Yes
       ↓
Feedback prompt with exact disagreement
       ↓
Second LLM evaluation
       ↓
Compare again
   ├─ Agree → Accept
   └─ Still disagree → REVIEW_REQUIRED / conservative handling
```

Maximum two LLM evaluation passes for the prototype.

Second-pass prompt should tell the model: - the deterministic score -
its previous score - exact skill-level disagreement - evidence - that
unsupported assumptions must not increase the score - required
structured output

Do not merely say "think again."

------------------------------------------------------------------------

# 16. Match Result Storage

## MATCH_RESULT

``` text
match_id PK
student_id FK
job_id FK
weighted_score
semantic_score
llm_score
final_score
difference
validation_status
model_version
created_at
```

Possible statuses:

``` text
AGREED
RECONCILED
REVIEW_REQUIRED
```

## MATCH_SKILL_RESULT

``` text
match_id FK
skill_id FK
required_level
student_level
skill_weight
skill_score
gap
llm_level
llm_confidence
evidence
```

This supports explainability and auditing.

------------------------------------------------------------------------

# 17. Prerequisite-Aware Learning Path

Example:

``` text
Python
  ↓
OOP
  ↓
Django
  ↓
REST API
  ↓
Docker
```

If Python and OOP are already satisfied:

``` text
✓ Python
✓ OOP
▶ Django
○ REST API
○ Docker
```

The system should not simply recommend every missing course at once. It
should order learning according to prerequisites, skill importance and
student state.

------------------------------------------------------------------------

# 18. Course Ranking

Candidate courses can be ranked using:

``` text
skill coverage
proficiency coverage
course duration
difficulty fit
prerequisite compatibility
student progress
resource quality
provider
```

A course should not be recommended merely because its title contains a
required skill.

------------------------------------------------------------------------

# 19. Time-to-Readiness Prediction

Inputs may include:

``` text
current proficiency
required proficiency
skill gap
skill difficulty
number of missing skills
prerequisite depth
course duration
study hours/week
historical learning velocity
assessment scores
course completion rate
```

Output should preferably be a range:

``` text
Estimated readiness: 6–9 weeks
```

Avoid false precision such as exactly 52 days unless the data supports
it.

Possible initial regression models: - Linear Regression - Random Forest
Regressor - Gradient Boosting Regressor

Start simple. Do not use deep learning unless data volume justifies it.

------------------------------------------------------------------------

# 20. Job Match Prediction ML

Potential models: - Logistic Regression - Decision Tree - Random
Forest - Gradient Boosting

Potential features:

``` text
weighted_skill_score
mandatory_skill_coverage
semantic_similarity
experience_match
education_match
project_match
certification_match
```

Output:

``` text
match probability
```

Important: do not call a number a calibrated probability until the model
is evaluated/calibrated using suitable labeled data.

------------------------------------------------------------------------

# 21. Career Readiness

Possible readiness inputs:

``` text
required skill coverage
proficiency match
mandatory skill completion
learning progress
project evidence
experience evidence
assessment performance
```

Dashboard example:

``` text
Backend Developer
Career Readiness: 72%

Python    4/5
SQL       4/4
Git       3/3
Django    2/4
REST API  2/3
Docker    0/2
```

------------------------------------------------------------------------

# 22. Continuous Feedback Loop

``` text
Student completes course
        ↓
Learning progress stored
        ↓
Assessment/proficiency updated
        ↓
STUDENT_SKILL updated
        ↓
Skill gaps recalculated
        ↓
Weighted match recalculated
        ↓
Readiness recalculated
        ↓
Learning path recalculated
```

Example:

``` text
Django 0/5 → 3/5
Match 62% → 74%
```

The application should calculate the actual result from stored values
rather than hard-code demo numbers.

------------------------------------------------------------------------

# 23. Alternative Careers

Optional but valuable:

``` text
Data Analyst       86%
Backend Developer  78%
Data Engineer      74%
ML Engineer        61%
```

Explain why the highest role is currently strongest, based on existing
competency coverage.

------------------------------------------------------------------------

# 24. External Job Data / ETL

``` text
Authorized APIs / Public datasets / Admin input
                ↓
             Extract
                ↓
            Transform
                ↓
             Validate
                ↓
       Skill normalization
                ↓
              Load
                ↓
             MySQL
```

Store `source` and `source_job_id` for traceability and deduplication.

Do not make the hackathon dependent on unauthorized scraping.

------------------------------------------------------------------------

# 25. Recommended Technology Stack

### Frontend

``` text
React
TypeScript
Tailwind CSS
```

### Backend

``` text
Python
FastAPI
```

### Database

``` text
MySQL
```

### Data/ML

``` text
Python
pandas
NumPy
scikit-learn
```

### Semantic similarity

``` text
Sentence Transformers or equivalent embedding model
```

### LLM

``` text
Provider abstraction:
Gemini / Groq / OpenRouter
```

### Resume processing

``` text
PyMuPDF
python-docx
LLM/NLP extraction
```

------------------------------------------------------------------------

# 26. Backend Project Structure

``` text
nexus/
├── frontend/
├── backend/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── api/
│       │   ├── auth.py
│       │   ├── students.py
│       │   ├── resumes.py
│       │   ├── jobs.py
│       │   ├── courses.py
│       │   ├── matching.py
│       │   └── recommendations.py
│       ├── models/
│       ├── schemas/
│       ├── repositories/
│       ├── services/
│       ├── nlp/
│       │   ├── resume_parser.py
│       │   ├── skill_extractor.py
│       │   └── normalizer.py
│       ├── matching/
│       │   ├── weighted_matcher.py
│       │   ├── semantic_matcher.py
│       │   ├── comparator.py
│       │   └── reconciliation.py
│       ├── ml/
│       │   ├── job_match_model.py
│       │   ├── readiness_model.py
│       │   └── training/
│       ├── llm/
│       │   ├── provider.py
│       │   ├── gemini.py
│       │   ├── groq.py
│       │   └── prompts/
│       └── graph/
│           └── prerequisites.py
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   └── migrations/
├── ml/
│   ├── datasets/
│   ├── notebooks/
│   ├── models/
│   └── evaluation/
├── docs/
└── .env.example
```

------------------------------------------------------------------------

# 27. API Endpoints

``` text
POST /auth/register
POST /auth/login

POST /students/{id}/resume
GET  /students/{id}/skills
PUT  /students/{id}/skills

GET  /jobs
GET  /jobs/{job_id}
GET  /jobs/{job_id}/skills

GET  /courses
GET  /courses/{course_id}

POST /matching/{student_id}/{job_id}
GET  /matching/{match_id}

GET  /students/{id}/skill-gaps
GET  /students/{id}/learning-path
GET  /students/{id}/readiness
GET  /students/{id}/recommendations

POST /progress
PUT  /progress/{progress_id}
```

------------------------------------------------------------------------

# 28. Match API Flow

``` text
POST /matching/{student_id}/{job_id}
        ↓
Fetch student
        ↓
Fetch student skills
        ↓
Fetch job + requirements
        ↓
Weighted matcher
        ↓
Semantic matcher
        ↓
LLM evaluator
        ↓
Comparator
        ↓
If mismatch → reconciliation
        ↓
Skill gaps
        ↓
Learning path
        ↓
Readiness estimate
        ↓
Persist result
        ↓
Return structured response
```

------------------------------------------------------------------------

# 29. Example Match Response

``` json
{
  "student_id": 101,
  "job_id": 500,
  "weighted_score": 79,
  "semantic_score": 82,
  "llm_score": 84,
  "final_score": 81,
  "validation_status": "AGREED",
  "skill_gaps": [
    {
      "skill": "Django",
      "current_level": 2,
      "required_level": 4,
      "gap": 2
    },
    {
      "skill": "Docker",
      "current_level": 0,
      "required_level": 2,
      "gap": 2
    }
  ],
  "estimated_readiness": {
    "minimum_weeks": 6,
    "maximum_weeks": 9
  }
}
```

------------------------------------------------------------------------

# 30. Dashboard

``` text
========================================
          NEXUS CAREER DASHBOARD
========================================

Target: Backend Developer

Career Readiness: 72%
Job Match: 81%
Estimated Readiness: 6–9 weeks

----------------------------------------
SKILL GAP
Python       4 / 5
SQL          4 / 4
Git          3 / 3
Django       2 / 4
REST API     2 / 3
Docker       0 / 2

----------------------------------------
LEARNING PATH
✓ Python Advanced
✓ Git & GitHub
▶ Django Fundamentals
○ REST API Development
○ Docker Fundamentals

----------------------------------------
NEXT PRIORITY
Django

Reason:
High job weight + proficiency gap +
prerequisites satisfied
```

------------------------------------------------------------------------

# 31. Security

Minimum: - Password hashing - `.env` secrets - No API keys in frontend -
File size/type validation - Input validation - Parameterized SQL/ORM -
Authentication/authorization - Private resume handling - Avoid
unnecessary sensitive logging

Example `.env`:

``` text
DATABASE_URL=...
GEMINI_API_KEY=...
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
JWT_SECRET=...
```

Never commit actual secrets.

------------------------------------------------------------------------

# 32. DBMS Quality Requirements

Aim for 3NF for core relational tables.

Avoid:

``` text
JOB.skills = "Python, SQL, Docker"
```

Use:

``` text
JOB
JOB_SKILL
SKILL
```

Avoid:

``` text
COURSE.skills = "Python, SQL"
```

Use:

``` text
COURSE
COURSE_SKILL
SKILL
```

Use foreign keys and referential integrity.

Use transactions for multi-table operations such as:

``` text
Course completion
→ progress update
→ skill update
```

Add indexes based on actual query patterns, especially:

``` text
STUDENT.email
JOB.title
JOB.company_id
JOB.source_job_id
SKILL.skill_name
STUDENT_SKILL.skill_id
JOB_SKILL.skill_id
COURSE_SKILL.skill_id
LEARNING_PROGRESS.student_id
MATCH_RESULT.student_id
MATCH_RESULT.job_id
```

------------------------------------------------------------------------

# 33. Edge Cases

### Overqualification

Cap skill score at 1.0.

### Missing skill

Use a deterministic score of zero if required, but retain evidence state
as `NOT_DETECTED` where appropriate.

### Invalid weights

Reject jobs whose skill weights do not sum to 1/100%.

### Duplicate skills

Normalize before storage.

### Synonyms

Map aliases to canonical skills.

### Course mismatch

Do not recommend a course unless it covers the target skill.

### Prerequisite cycle

Detect and reject/flag cycles.

### API failure

Core DB + deterministic matching should still function.

------------------------------------------------------------------------

# 34. Testing Weighted Matching

Use this deterministic test:

``` text
Python  required 5, student 4, weight 30
SQL     required 4, student 4, weight 20
Django  required 4, student 2, weight 20
REST    required 3, student 3, weight 15
Git     required 3, student 3, weight 10
Docker  required 2, student 0, weight 5
```

Expected:

``` text
Python = 24
SQL = 20
Django = 10
REST = 15
Git = 10
Docker = 0
Total = 79%
```

Unit tests should include: 1. perfect match 2. zero match 3. partial
match 4. missing skill 5. overqualified student 6. mandatory missing
skill 7. invalid weight sum 8. duplicate normalized skill

------------------------------------------------------------------------

# 35. Anti-Gravity Implementation Strategy

Do NOT ask a coding agent to build the whole project in one prompt.
Build in controlled milestones.

## Phase 1 --- Repository

Create frontend/backend/database/ml/docs and get a minimal app running.

## Phase 2 --- Database

Implement schema, foreign keys, constraints, indexes and seed data.

## Phase 3 --- Student Profile

Authentication, profile, resume upload, skill profile.

## Phase 4 --- Jobs

Companies, jobs, requirements, filtering.

## Phase 5 --- Courses

Courses, course-skill mapping, prerequisites.

## Phase 6 --- Deterministic Matching

Weighted matching, skill gaps, explanations. Test before adding AI.

## Phase 7 --- NLP/LLM

Resume extraction, normalization, structured JSON.

## Phase 8 --- Semantic Matching

Embeddings + cosine similarity.

## Phase 9 --- Hybrid Evaluator

Weighted score + semantic score + LLM score + comparator +
reconciliation.

## Phase 10 --- Learning Path

Prerequisite traversal, ranking, course ordering.

## Phase 11 --- ML

Job match model and time-to-readiness model. Only after usable data
exists.

## Phase 12 --- Feedback Loop

Progress → competency update → recalculation.

## Phase 13 --- Dashboard

Integrate all outputs.

## Phase 14 --- Testing

DB, API, matching, NLP, ML, mismatch handling, security, UI.

------------------------------------------------------------------------

# 36. Anti-Gravity Prompt Rules

When asking the coding agent to modify code:

1.  Inspect the repository first.
2.  Identify existing architecture before editing.
3.  State exactly which module may be changed.
4.  State what must not change.
5.  Implement one feature at a time.
6.  Run tests after implementation.
7.  Report changed files.
8.  Never silently redesign the database.
9.  Keep migrations versioned.
10. Keep ML models replaceable.
11. Keep LLM providers replaceable.
12. Keep deterministic matching independent from the LLM.

Example prompt:

``` text
Inspect the existing NEXUS repository before modifying anything.

Task: implement weighted skill matching.

Requirements:
- Read JOB_SKILL records from MySQL.
- Read STUDENT_SKILL records from MySQL.
- SkillScore = min(student_level / required_level, 1).
- Multiply by importance weight.
- Validate that job weights sum to 1 or 100%.
- Calculate total weighted match.
- Calculate skill gaps.
- Preserve NOT_DETECTED vs confirmed zero where possible.
- Return explainable skill-level results.

Do not:
- add an LLM
- change the database schema
- change frontend code
- invent missing skills
- hard-code job data

Add tests for perfect, zero, partial, missing, overqualified and mandatory-missing cases.
Run tests and report changed files.
```

------------------------------------------------------------------------

# 37. MVP vs Advanced

## MVP --- must work

``` text
Student
Resume
Skill
Student Skill
Job
Job Skill
Course
Course Skill
Prerequisite
Progress
MySQL
Weighted Matching
Skill Gap
Learning Path
```

## Advanced

``` text
LLM Resume Parsing
Semantic Similarity
LLM Evaluation
Mismatch Reconciliation
Job Match ML
Time-to-Readiness ML
Alternative Careers
External Job Data
Explainability
```

Do not let advanced AI prevent the DBMS core from working.

------------------------------------------------------------------------

# 38. Final Build Order

``` text
1. Database schema
2. Seed jobs/skills/courses
3. Student profile
4. Resume upload
5. Skill extraction
6. Skill normalization
7. Weighted matcher
8. Skill-gap engine
9. Course mapping
10. Prerequisite graph
11. Learning path
12. Progress tracking
13. Semantic similarity
14. LLM evaluator
15. Comparator/reconciliation
16. Job-match ML
17. Time-to-readiness ML
18. Adaptive feedback loop
19. Dashboard
20. Testing + presentation
```

------------------------------------------------------------------------

# 39. Rejected Design Decisions --- Preserve These Decisions

## THIRAN name --- rejected

`THIRAN` was considered because Tamil `திறன்` means skill/capability. It
was rejected because the name emphasized skills more than the complete
connected career intelligence architecture and the acronym felt somewhat
forced.

## VALAR name --- rejected

`VALAR` was considered because Tamil `வளர்` means grow/develop. It fit
adaptive learning but emphasized growth rather than the full
student--skill--job--course nexus. NEXUS was selected.

## VAZHI / MARGA / DISHA / PRAGATI --- rejected

These communicated path, direction or progress, but each represented
only one aspect of the system. NEXUS better communicates
interconnection.

## Two separate databases --- rejected

A separate job database and course database would add unnecessary
separation and weaken relational modeling. One normalized MySQL database
is more appropriate.

## Direct JOB → COURSE mapping --- rejected

A course can support multiple jobs, and a job requires multiple skills.
The correct conceptual chain is
`JOB → JOB_SKILL → SKILL ← COURSE_SKILL ← COURSE`.

## LLM-only matching --- rejected

It is harder to reproduce, explain, validate and calibrate. It also
weakens the deterministic DBMS component. NEXUS therefore uses
deterministic weighted matching as the baseline and LLMs as a
semantic/evidence layer.

## Keyword-only matching --- rejected

Exact keywords miss semantic equivalence. Embedding-based similarity is
added for semantic matching.

## Infinite LLM thinking loop --- rejected

An unlimited loop is expensive, hard to debug and may not converge.
Prototype uses a maximum of two LLM evaluation passes followed by
`REVIEW_REQUIRED` or conservative handling if disagreement remains.

## Missing skill = confirmed zero --- rejected

A resume omission does not prove zero knowledge. Store evidence state
separately where possible.

## Arbitrarily complex ML --- rejected

Deep learning is not justified by default. Start with interpretable
classical models and only increase complexity if data and evaluation
justify it.

## Entire system dependent on external APIs --- rejected

Core DBMS + deterministic matching must continue to function if an AI
API is unavailable.

------------------------------------------------------------------------

# 40. Final Research/Technical Positioning

NEXUS should be presented as a:

> **Database-centric, hybrid AI framework for adaptive career
> readiness.**

The technical integration is:

``` text
Relational Data Modeling
        +
Competency/Skill Ontology
        +
Prerequisite Dependency Graph
        +
Weighted Skill Matching
        +
Semantic Similarity
        +
LLM Evidence Analysis
        +
Predictive ML
        +
Adaptive Feedback
```

The novelty is NOT simply "using AI". The stronger proposition is the
integration of structured competency modeling, prerequisite-aware
learning-path generation, deterministic weighted matching, semantic
evaluation, predictive readiness forecasting and disagreement-driven
reconciliation inside a single adaptive career-readiness system.

------------------------------------------------------------------------

# 41. One-Sentence Project Definition

> **NEXUS transforms resume-derived student competency data and
> target-job requirements into proficiency-aware skill-gap analysis,
> prerequisite-aware learning paths, personalized time-to-readiness
> forecasts, explainable job matching and continuously adaptive
> career-readiness recommendations.**

------------------------------------------------------------------------

# 42. Final Frozen Logic

``` text
DATABASE
  ↓
MySQL normalized relational schema

NLP
  ↓
Resume → evidence/skills

MATCHING
  ↓
Weighted skill matching

SEMANTIC
  ↓
Embedding + cosine similarity

LLM
  ↓
Structured evidence evaluation

VALIDATION
  ↓
Weighted vs LLM comparison

MISMATCH
  ↓
One reconciliation pass

SKILL GAP
  ↓
Required - Current

LEARNING
  ↓
Skill → Course mapping

PREREQUISITES
  ↓
Dependency-aware ordering

PREDICTION
  ↓
Job-match probability + time-to-readiness

FEEDBACK
  ↓
Learning progress → competency update

OUTPUT
  ↓
Personalized career roadmap
```

This is the **frozen baseline architecture**. Future changes should be
implementation improvements or experimentally validated refinements, not
silent changes to the core concept.
