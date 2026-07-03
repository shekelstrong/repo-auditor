"""analyze_structure: анализ структуры репо."""


async def run(repo_path: str) -> dict:
    """Анализирует структуру.

    Args:
        repo_path: Путь к репо.

    Returns:
        Словарь со статистикой.
    """
    import os
    from pathlib import Path
    from collections import Counter

    if not os.path.exists(repo_path):
        return {"error": f"Path not found: {repo_path}"}

    files = []
    total_size = 0
    languages = Counter()
    extensions = Counter()

    SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", "target"}

    for root, dirs, fs in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            path = Path(root) / f
            try:
                size = path.stat().st_size
                total_size += size
                ext = path.suffix.lstrip(".").lower() or "no_ext"
                extensions[ext] += 1

                # Детект языка по расширению
                if ext in ("py",):
                    languages["Python"] += 1
                elif ext in ("js", "jsx"):
                    languages["JavaScript"] += 1
                elif ext in ("ts", "tsx"):
                    languages["TypeScript"] += 1
                elif ext in ("go",):
                    languages["Go"] += 1
                elif ext in ("rs",):
                    languages["Rust"] += 1
                elif ext in ("java", "kt", "scala"):
                    languages["JVM"] += 1
                elif ext in ("md", "txt", "rst"):
                    languages["Docs"] += 1
                elif ext in ("json", "yaml", "yml", "toml"):
                    languages["Config"] += 1
            except (OSError, PermissionError):
                continue

    # Top-5 файлов по размеру
    file_list = []
    for root, dirs, fs in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            path = Path(root) / f
            try:
                file_list.append((str(path.relative_to(repo_path)), path.stat().st_size))
            except (OSError, PermissionError):
                continue
    file_list.sort(key=lambda x: -x[1])

    return {
        "total_files": sum(extensions.values()),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "languages": dict(languages.most_common(10)),
        "top_extensions": dict(extensions.most_common(10)),
        "top_files_by_size": [{"path": p, "size": s} for p, s in file_list[:10]],
    }
