"""audit_honesty: что обещает README vs что реально есть."""


import re
from pathlib import Path


# Маркеры "обещаний" в README
PROMISE_PATTERNS = [
    (r"\b(complete|full|production[- ]ready|ready to use|fully implemented)\b", "production-ready"),
    (r"\b(mcp[- ]server|fastapi|django|flask|telegram|bot)\b", "tech claim"),
    (r"\b\d+ tools?\b", "tool count"),
    (r"\b(7-day|7 day|seven day|24 hours?|instant)\b", "speed claim"),
    (r"\b(tests? included|100% tests|tested)\b", "test claim"),
    (r"\b(secure|encrypted|auth|authentication)\b", "security claim"),
]


async def run(repo_path: str) -> dict:
    """Аудит честности README.

    Args:
        repo_path: Путь к репо.

    Returns:
        Словарь с promises и reality check.
    """
    readme_path = Path(repo_path) / "README.md"
    if not readme_path.exists():
        return {"error": "No README.md"}

    readme = readme_path.read_text(errors="ignore").lower()

    promises = []
    for pattern, label in PROMISE_PATTERNS:
        matches = re.findall(pattern, readme)
        if matches:
            promises.append({"type": label, "matches": len(matches)})

    # Reality check
    reality = {}

    # "tests" — есть ли тесты
    reality["tests_actually_present"] = (Path(repo_path) / "tests").is_dir() or (Path(repo_path) / "test").is_dir()
    if reality["tests_actually_present"]:
        test_files = list((Path(repo_path) / "tests").rglob("test_*.py")) if (Path(repo_path) / "tests").is_dir() else []
        reality["test_files_count"] = len(test_files)
    else:
        reality["test_files_count"] = 0

    # "production-ready" — есть ли CI, тесты, requirements, Docker
    reality["ci_present"] = (Path(repo_path) / ".github" / "workflows").is_dir()
    reality["docker_present"] = (Path(repo_path) / "Dockerfile").exists()
    reality["requirements_present"] = (Path(repo_path) / "requirements.txt").exists() or (Path(repo_path) / "package.json").exists()

    # TODOs / half-implementations
    todo_count = 0
    half_done = []
    for code_file in list(Path(repo_path).rglob("*.py"))[:50]:
        try:
            content = code_file.read_text(errors="ignore")
            todo_count += len(re.findall(r"#\s*TODO", content, re.IGNORECASE))
            todo_count += len(re.findall(r"#\s*FIXME", content, re.IGNORECASE))
            if re.search(r"raise NotImplementedError", content):
                half_done.append(str(code_file.relative_to(repo_path)))
        except Exception:
            pass

    reality["todo_fixme_count"] = todo_count
    reality["not_implemented_files"] = half_done[:5]

    # Score честности
    promised_test = any(p["type"] == "test claim" for p in promises)
    actually_has_test = reality["test_files_count"] > 0

    if promised_test and not actually_has_test:
        honesty_issues = ["README обещает тесты, но их нет"]
    else:
        honesty_issues = []

    if reality["todo_fixme_count"] > 5:
        honesty_issues.append(f"Много TODO/FIXME ({reality['todo_fixme_count']}) — код незавершён")

    if half_done:
        honesty_issues.append(f"NotImplementedError в {len(half_done)} файлах")

    return {
        "promises_in_readme": promises,
        "reality_check": reality,
        "honesty_score": 100 - (len(honesty_issues) * 25),
        "honesty_issues": honesty_issues,
    }
