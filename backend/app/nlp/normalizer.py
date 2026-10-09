from typing import Dict, List, Optional
import re

DEFAULT_ALIAS_MAP: Dict[str, str] = {
    "python 3": "Python",
    "python programming": "Python",
    "python scripting": "Python",
    "py": "Python",
    "sql querying": "SQL",
    "relational database": "SQL",
    "postgres": "SQL",
    "postgresql": "SQL",
    "mysql": "SQL",
    "django framework": "Django",
    "restful services": "REST API",
    "rest api development": "REST API",
    "restful api": "REST API",
    "rest api": "REST API",
    "git version control": "Git",
    "github": "Git",
    "gitlab": "Git",
    "docker containers": "Docker",
    "containerization": "Docker",
    "react.js": "React",
    "reactjs": "React",
    "ts": "TypeScript",
    "fast api": "FastAPI",
    "ml": "Machine Learning",
    "machine learning ml": "Machine Learning"
}

class SkillNormalizer:
    def __init__(self, custom_alias_map: Optional[Dict[str, str]] = None):
        self.alias_map = custom_alias_map or DEFAULT_ALIAS_MAP

    def normalize(self, raw_skill_string: str) -> str:
        """
        Normalizes variations of skill names into canonical vocabulary name.
        Example: 'Python programming' -> 'Python'
        """
        if not raw_skill_string:
            return ""

        cleaned = raw_skill_string.strip().lower()
        cleaned = re.sub(r'\s+', ' ', cleaned)

        if cleaned in self.alias_map:
            return self.alias_map[cleaned]

        # Capitalize nicely if not in alias dictionary
        return raw_skill_string.strip().title()
