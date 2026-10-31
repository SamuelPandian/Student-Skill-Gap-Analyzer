# NEXUS — Next-generation Employability, eXpertise & Upskilling System
> **A Database-Centric, Hybrid AI Career-Readiness & Skill-Gap Analysis Platform**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg?logo=react)](https://reactjs.org/)
[![Database](https://img.shields.io/badge/Database-MySQL_%2F_SQLite_(3NF)-00758F.svg?logo=mysql)](https://mysql.com)
[![AI Evaluator](https://img.shields.io/badge/AI_Engine-Groq_%2F_Llama--3-F55036.svg)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

NEXUS transforms resume-derived candidate competencies and target job requirements into:
1. **Proficiency-aware skill-gap analysis** with strict 100% normalized requirement weighting.
2. **Prerequisite-aware learning roadmaps** using Directed Acyclic Graph (DAG) topological sorting.
3. **Hybrid AI evaluation** combining a deterministic database baseline, vector embedding similarity, and live LLM evidence reasoning.
4. **Anti-hallucination 2-pass reconciliation loops** that catch discrepancies above 10%.
5. **Continuous adaptive feedback**: Completing learning courses recalculates readiness and match metrics in real-time.

```text
Student Resume → NLP Extraction → Relational DB (Competency State)
   ↓
Target Job Requirements (Weights = 100%)
   ↓
Hybrid Matcher (Weighted DB Baseline + Vector Similarity + LLM Evaluator)
   ↓
2-Pass Reconciliation Loop (Catches AI Discrepancies)
   ↓
Prerequisite DAG Traversal (Topological Learning Roadmap)
   ↓
Student Completes Courses → Competency Recalculated Automatically
```

---

## 🏛️ Architecture & System Design

NEXUS treats the **relational database as the single source of truth**, with ML, NLP, and LLM models acting as the intelligence layer.

### The Critical Relational Rule
A job needs skills, and a course teaches skills:
$$\text{JOB} \rightarrow \text{JOB\_SKILL} \rightarrow \text{SKILL} \leftarrow \text{COURSE\_SKILL} \leftarrow \text{COURSE}$$

---

## 🚀 Features

- **14 Normalized 3NF Tables**: Complete relational modeling with zero unnormalized CSV-in-column anti-patterns.
- **Deterministic Weighted Baseline Matcher**: 
  $$\text{SkillScore}_i = \min\left(\frac{\text{StudentLevel}_i}{\text{RequiredLevel}_i}, 1.0\right)$$
  $$\text{Contribution}_i = \text{SkillScore}_i \times \text{Weight}_i \times 100$$
- **Prerequisite DAG Engine**: Cycle-detection and Kahn's topological sort via NetworkX.
- **NLP Resume Parser**: Extracts text from `.pdf` and `.docx` documents and estimates evidence levels.
- **Predictive ML Analytics**: Range-based Time-to-Readiness estimation (e.g. `6–9 weeks` or `10–16 weeks`).
- **Interactive Glassmorphic Dashboard**: Real-time KPI cards, interactive skill matrices, and simulation triggers.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, NetworkX, PyMuPDF, python-docx, Sentence-Transformers.
- **AI / LLM Layer**: Groq (`openai/gpt-oss-120b`), Google Gemini, OpenRouter.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Database**: SQLite (local auto-fallback) / MySQL 8.0+.

---

## 💻 Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Web Dashboard: `http://localhost:3000`

### 3. Database Inspection
```bash
cd backend
python show_database.py
```

---

## 👥 Project Team

- **Contributors**:
  - [Shrinithish Boobalan](https://github.com/nithish4431j-droid)
  - [Samuel Pandian](https://github.com/SamuelPandian)
  - [Ashmit Mehta](https://github.com/ashmitmehta1234-sudo)
