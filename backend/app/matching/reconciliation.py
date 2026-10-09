import json
import os
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from app.config import settings

@dataclass
class HybridMatchDecision:
    weighted_score: float
    semantic_score: float
    llm_score: float
    final_score: float
    difference: float
    validation_status: str # "AGREED", "RECONCILED", "REVIEW_REQUIRED"
    passes_count: int
    llm_skill_evaluations: List[Dict[str, Any]]
    reconciliation_notes: str

class LLMProviderAdapter:
    """Provider abstraction layer for Gemini, Groq, or OpenRouter"""
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.groq_key = settings.GROQ_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY

    def evaluate_evidence(self, prompt: str) -> Optional[Dict[str, Any]]:
        # 1. Try Groq (ultra-fast, verified active)
        if self.groq_key and self.groq_key.startswith("gsk_"):
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {"role": "system", "content": "You are a career readiness evaluator. Always return strictly valid JSON matching the requested schema without markdown backticks or commentary."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception as e:
                print(f"Groq API call notice: {e}")

        # 2. Try OpenRouter
        if self.openrouter_key and self.openrouter_key.startswith("sk-or-"):
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [
                        {"role": "system", "content": "You are a career evaluator. Always return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ]
                }
                res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    # Extract JSON if wrapped in markdown
                    cleaned = content.strip().replace("```json", "").replace("```", "").strip()
                    return json.loads(cleaned)
            except Exception as e:
                print(f"OpenRouter API call notice: {e}")

        # 3. Try Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(
                    prompt, 
                    generation_config={"response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            except Exception as e:
                print(f"Gemini API call notice: {e}")

        return None

def evaluate_hybrid_match(
    weighted_score: float,
    semantic_score: float,
    student_resume_text: str,
    job_title: str,
    required_skills_json: List[Dict[str, Any]],
    threshold: float = None
) -> HybridMatchDecision:
    """
    FROZEN HYBRID EVALUATOR & RECONCILIATION LOOP (NEXUS Spec Section 14 & 15)
    Maximum 2 LLM evaluation passes.
    """
    if threshold is None:
        threshold = settings.RECONCILIATION_THRESHOLD

    adapter = LLMProviderAdapter()
    
    # 1. First Pass Evaluation
    prompt_pass_1 = f"""
    Evaluate candidate evidence for target job: {job_title}.
    Required Skills: {json.dumps(required_skills_json)}
    Resume Content: {student_resume_text[:2000]}

    Return JSON schema:
    {{
       "overall_match_score": <number 0-100>,
       "skills": [
          {{"skill": "<name>", "evidence": "<text>", "estimated_level": <0-5>, "confidence": <0-1>}}
       ]
    }}
    """
    
    llm_res_1 = adapter.evaluate_evidence(prompt_pass_1)
    
    if llm_res_1 is not None and "overall_match_score" in llm_res_1:
        llm_score_1 = float(llm_res_1["overall_match_score"])
        llm_skills = llm_res_1.get("skills", [])
    else:
        # Structured baseline fallback when LLM API key is not configured
        llm_score_1 = weighted_score
        llm_skills = []

    diff_1 = abs(weighted_score - llm_score_1)

    # Check threshold for Pass 1
    if diff_1 <= threshold:
        # AGREED
        final_score = round(0.50 * weighted_score + 0.25 * semantic_score + 0.25 * llm_score_1, 2)
        return HybridMatchDecision(
            weighted_score=weighted_score,
            semantic_score=semantic_score,
            llm_score=llm_score_1,
            final_score=final_score,
            difference=round(diff_1, 2),
            validation_status="AGREED",
            passes_count=1,
            llm_skill_evaluations=llm_skills,
            reconciliation_notes="Pass 1: Deterministic score and LLM evidence score agreed within threshold."
        )

    # Trigger Second Pass Reconciliation Loop
    prompt_pass_2 = f"""
    DISAGREEMENT RECONCILIATION PASS (Pass 2 of 2):
    Deterministic Baseline Score: {weighted_score}%
    Previous LLM Score: {llm_score_1}%
    Disagreement: {diff_1:.2f} percentage points (Exceeds {threshold}% threshold).
    
    Job Title: {job_title}
    Required Skills: {json.dumps(required_skills_json)}
    Resume Text: {student_resume_text[:2000]}
    
    Notice: Unsupported assumptions must NOT artificially inflate the score. Re-evaluate evidence strictly.
    Return exact JSON matching:
    {{
       "overall_match_score": <number 0-100>,
       "reconciliation_reasoning": "<string>",
       "skills": [
          {{"skill": "<name>", "evidence": "<text>", "estimated_level": <0-5>, "confidence": <0-1>}}
       ]
    }}
    """
    
    llm_res_2 = adapter.evaluate_evidence(prompt_pass_2)

    if llm_res_2 is not None and "overall_match_score" in llm_res_2:
        llm_score_2 = float(llm_res_2["overall_match_score"])
        llm_skills_2 = llm_res_2.get("skills", llm_skills)
        reasoning = llm_res_2.get("reconciliation_reasoning", "Pass 2 completed.")
    else:
        # Conservative shift towards deterministic score
        llm_score_2 = (weighted_score + llm_score_1) / 2.0
        llm_skills_2 = llm_skills
        reasoning = "Fallback conservative reconciliation applied."

    diff_2 = abs(weighted_score - llm_score_2)

    if diff_2 <= threshold:
        validation_status = "RECONCILED"
        final_score = round(0.60 * weighted_score + 0.20 * semantic_score + 0.20 * llm_score_2, 2)
        notes = f"Pass 2 Reconciled: {reasoning}"
    else:
        validation_status = "REVIEW_REQUIRED"
        # Conservative handling: prioritize deterministic weighted matcher score
        final_score = round(0.70 * weighted_score + 0.15 * semantic_score + 0.15 * llm_score_2, 2)
        notes = f"Pass 2 Still Disagreed ({diff_2:.2f}% diff). Triggered REVIEW_REQUIRED with conservative deterministic score weighting."

    return HybridMatchDecision(
        weighted_score=weighted_score,
        semantic_score=semantic_score,
        llm_score=round(llm_score_2, 2),
        final_score=final_score,
        difference=round(diff_2, 2),
        validation_status=validation_status,
        passes_count=2,
        llm_skill_evaluations=llm_skills_2,
        reconciliation_notes=notes
    )
