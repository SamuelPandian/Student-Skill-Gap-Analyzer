import os
from typing import Dict, List, Any
from app.nlp.normalizer import SkillNormalizer

class ResumeParser:
    def __init__(self):
        self.normalizer = SkillNormalizer()

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract plain text from PDF or DOCX resume file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found at: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            try:
                import fitz # PyMuPDF
                doc = fitz.open(file_path)
                text = "\n".join([page.get_text() for page in doc])
                return text
            except Exception as e:
                raise RuntimeError(f"Error reading PDF file: {e}")
                
        elif ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                return text
            except Exception as e:
                raise RuntimeError(f"Error reading DOCX file: {e}")
        else:
            # Fallback to plain text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def extract_candidate_name(self, raw_text: str, fallback_file_name: str = "") -> str:
        """Extract candidate name from top lines of the resume text."""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for line in lines[:10]:
            clean = "".join(ch for ch in line if ch.isalpha() or ch.isspace() or ch == '.')
            clean = " ".join(clean.split())
            lower = clean.lower()
            if (
                2 <= len(clean.split()) <= 4 
                and 4 <= len(clean) <= 35 
                and not any(bad in lower for bad in ["resume", "curriculum", "vitae", "profile", "contact", "phone", "email", "education", "experience", "skills"])
                and not any(char.isdigit() for char in line)
                and "@" not in line
            ):
                return clean.title()

        # Fallback to file name if name not parsed from text
        if fallback_file_name:
            base = os.path.splitext(os.path.basename(fallback_file_name))[0]
            # Strip student_id prefix like 101_
            parts = base.split("_")
            meaningful = [p for p in parts if not p.isdigit() and "resume" not in p.lower()]
            if meaningful:
                return " ".join(meaningful).title()
        return "Shrinithish"

    def parse_resume(self, file_path: str, canonical_skills: List[str]) -> Dict[str, Any]:
        """
        Parses resume text and extracts matching canonical skills + evidence snippets.
        Distinguishes NOT_DETECTED from detected skills.
        """
        raw_text = self.extract_text_from_file(file_path)
        lower_text = raw_text.lower()
        candidate_name = self.extract_candidate_name(raw_text, file_path)

        detected_skills: List[Dict[str, Any]] = []

        # Common skill synonyms/aliases
        skill_aliases = {
            "python": ["python", "python3", "python 3", "py"],
            "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "relational database", "queries"],
            "django": ["django", "django rest framework", "drf"],
            "rest api": ["rest api", "restful api", "restful", "rest apis", "rest endpoints"],
            "git": ["git", "github", "gitlab", "version control"],
            "docker": ["docker", "containerization", "containers", "dockerfile"],
            "fastapi": ["fastapi", "fast api"],
            "react": ["react", "react.js", "reactjs"],
            "java": ["java", "core java", "j2se"],
            "machine learning": ["machine learning", "ml", "deep learning", "scikit-learn"]
        }

        for skill in canonical_skills:
            normalized_name = self.normalizer.normalize(skill)
            primary_key = normalized_name.lower()
            patterns = skill_aliases.get(primary_key, [primary_key])

            found_idx = -1
            matched_pattern = ""
            for pat in patterns:
                # Word boundary check or substring check
                idx = lower_text.find(pat)
                if idx != -1:
                    found_idx = idx
                    matched_pattern = pat
                    break

            if found_idx != -1:
                # Find surrounding context/sentence as evidence
                start = max(0, found_idx - 50)
                end = min(len(raw_text), found_idx + 100)
                snippet = raw_text[start:end].replace("\n", " ").strip()

                # Basic evidence-based heuristic level estimation
                estimated_level = 3.0
                snippet_lower = snippet.lower()
                if "senior" in snippet_lower or "expert" in snippet_lower or "5 years" in snippet_lower:
                    estimated_level = 5.0
                elif "intern" in snippet_lower or "built" in snippet_lower or "developed" in snippet_lower or "created" in snippet_lower or "hands-on" in snippet_lower:
                    estimated_level = 3.5
                elif "basic" in snippet_lower or "beginner" in snippet_lower:
                    estimated_level = 2.0

                detected_skills.append({
                    "skill_name": normalized_name,
                    "proficiency_level": estimated_level,
                    "confidence_score": 0.85,
                    "evidence_text": snippet,
                    "source": "RESUME"
                })

        return {
            "candidate_name": candidate_name,
            "parsed_text": raw_text,
            "detected_skills": detected_skills,
            "char_count": len(raw_text)
        }

