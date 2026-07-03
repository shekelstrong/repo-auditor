"""clone_repo: клонирование репо для анализа."""


async def run(repo_url: str, output_dir: str = "/tmp/repo-audit") -> dict:
    """Клонирует репо.

    Args:
        repo_url: URL GitHub.
        output_dir: Куда клонировать.

    Returns:
        Словарь с путём.
    """
    import subprocess
    import os
    import shutil
    from pathlib import Path

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    Path(output_dir).parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", repo_url, output_dir],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return {"error": f"Clone failed: {result.stderr[:200]}"}
        return {
            "status": "cloned",
            "repo_path": output_dir,
            "repo_url": repo_url,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Clone timeout (60s)"}
    except Exception as e:
        return {"error": str(e)}
