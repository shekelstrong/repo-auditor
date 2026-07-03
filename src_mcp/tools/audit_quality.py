"""audit_quality: чек-лист качества кода."""


CHECKLIST = {
    "tests": ("tests/", "Есть директория с тестами"),
    "ci": (".github/workflows/", "CI/CD настроен"),
    "type_hints_py": (None, "Python type hints"),  # special check
    "readme": ("README.md", "README > 500 символов"),
    "license": ("LICENSE", "LICENSE файл"),
    "requirements": ("requirements.txt", "requirements.txt / package.json"),
    "gitignore": (".gitignore", ".gitignore"),
    "docker": ("Dockerfile", "Dockerfile или compose"),
    "env_example": (".env.example", ".env.example"),
    "security": ("SECURITY.md", "SECURITY.md (опц.)"),
    "contributing": ("CONTRIBUTING.md", "CONTRIBUTING.md (опц.)"),
}


async def run(repo_path: str) -> dict:
    """Аудит качества.

    Args:
        repo_path: Путь к репо.

    Returns:
        Словарь с чек-листом и score.
    """
    import os
    from pathlib import Path

    if not os.path.exists(repo_path):
        return {"error": f"Path not found: {repo_path}"}

    base = Path(repo_path)
    results = {}

    for name, (rel_path, description) in CHECKLIST.items():
        if rel_path is None:
            continue
        path = base / rel_path
        if name == "readme":
            results[name] = {
                "present": path.exists(),
                "size_ok": path.stat().st_size > 500 if path.exists() else False,
                "description": description,
            }
        else:
            results[name] = {
                "present": path.exists(),
                "description": description,
            }

    # Python type hints
    py_files = list(base.rglob("*.py"))
    type_hints_count = 0
    for py in py_files[:20]:  # первые 20
        try:
            content = py.read_text(errors="ignore")
            if "def " in content and (" -> " in content or ": " in content.split("def ")[1].split(":")[0]):
                type_hints_count += 1
        except Exception:
            pass
    results["type_hints_py"] = {
        "files_checked": min(20, len(py_files)),
        "files_with_hints": type_hints_count,
        "pct": round(type_hints_count / max(min(20, len(py_files)), 1) * 100, 1),
    }

    # Score
    items_with_pass = []
    for k, v in results.items():
        if k == "readme":
            items_with_pass.append(v["present"] and v["size_ok"])
        elif k == "type_hints_py":
            items_with_pass.append(v["pct"] > 50)
        else:
            items_with_pass.append(v.get("present", False))

    score = round(sum(items_with_pass) / len(items_with_pass) * 100)

    return {
        "score": score,
        "checklist": results,
        "recommendations": _build_recommendations(results),
    }


def _build_recommendations(results: dict) -> list:
    recs = []
    for k, v in results.items():
        if k == "readme" and not (v.get("present") and v.get("size_ok")):
            recs.append("📝 README должен быть > 500 символов с инструкциями")
        elif k == "tests" and not v.get("present"):
            recs.append("🧪 Добавь tests/ — без тестов код 'хрупкий'")
        elif k == "ci" and not v.get("present"):
            recs.append("🔄 Настрой CI через GitHub Actions — автоматические тесты на каждый PR")
        elif k == "license" and not v.get("present"):
            recs.append("📜 Добавь LICENSE — без него другие не могут использовать код")
        elif k == "type_hints_py" and v.get("pct", 0) < 50:
            recs.append("🔤 Type hints в Python — 50%+ функций должны иметь")
    return recs
