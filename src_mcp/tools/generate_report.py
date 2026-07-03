"""generate_report: финальный отчёт."""


from src_mcp.tools.analyze_structure import run as analyze_run
from src_mcp.tools.audit_quality import run as quality_run
from src_mcp.tools.audit_honesty import run as honesty_run


async def run(repo_path: str) -> dict:
    """Генерирует отчёт.

    Args:
        repo_path: Путь к репо.

    Returns:
        Словарь с отчётом.
    """
    structure = await analyze_run(repo_path)
    quality = await quality_run(repo_path)
    honesty = await honesty_run(repo_path)

    # Red flags
    red_flags = []
    if quality["score"] < 50:
        red_flags.append(f"Качество кода низкое ({quality['score']}/100)")
    if honesty.get("honesty_score", 100) < 70:
        red_flags.append("README врёт: обещает что нет на самом деле")
    if not structure.get("languages"):
        red_flags.append("Нет кода в репо")
    elif sum(structure["languages"].values()) < 3:
        red_flags.append(f"Мало файлов ({sum(structure['languages'].values())})")
    if structure.get("total_size_mb", 0) > 500:
        red_flags.append("Огромный размер (>500MB) — может быть закоммичен node_modules или venv")

    # Final score
    final_score = round(
        quality["score"] * 0.5 +
        honesty.get("honesty_score", 100) * 0.3 +
        min(structure.get("total_files", 0) / 50 * 100, 100) * 0.2
    )

    return {
        "repo_path": repo_path,
        "final_score": final_score,
        "structure": {
            "total_files": structure.get("total_files"),
            "languages": structure.get("languages"),
            "size_mb": structure.get("total_size_mb"),
        },
        "quality": {
            "score": quality["score"],
            "checklist": quality["checklist"],
            "recommendations": quality["recommendations"],
        },
        "honesty": {
            "score": honesty.get("honesty_score"),
            "issues": honesty.get("honesty_issues"),
            "promises": honesty.get("promises_in_readme"),
        },
        "red_flags": red_flags,
        "verdict": "use" if final_score > 70 and not red_flags else "caution" if final_score > 50 else "avoid",
    }
