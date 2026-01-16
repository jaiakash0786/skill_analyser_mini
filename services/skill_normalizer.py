import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TAXONOMY_PATH = os.path.join(BASE_DIR, "rag", "skills", "skill_taxonomy.json")


def load_taxonomy():
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    alias_to_canonical = {}
    for canonical, aliases in taxonomy.items():
        for alias in aliases:
            alias_to_canonical[alias.lower()] = canonical

    return taxonomy, alias_to_canonical


TAXONOMY, ALIAS_LOOKUP = load_taxonomy()


def normalize_skills(raw_skills):
    normalized = set()

    for skill in raw_skills:
        s = skill.lower().strip()

        # Direct alias match
        if s in ALIAS_LOOKUP:
            normalized.add(ALIAS_LOOKUP[s])
            continue

        # Partial / semantic match
        for alias, canonical in ALIAS_LOOKUP.items():
            if alias in s:
                normalized.add(canonical)

    # Skill expansion logic
    if "full_stack" in normalized:
        normalized.update(
            ["frontend_development", "backend_development"]
        )

    return sorted(normalized)
