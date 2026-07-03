# repo-auditor

> MCP-сервер для аудита GitHub-репозиториев: структура, качество кода, честность README (что обещает vs что есть).

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io)

## 🎯 Что это

MCP-сервер с 5 инструментами для анализа чужих GitHub-репо:

- 📥 **clone_repo** — клонировать репо для анализа
- 📊 **analyze_structure** — статистика (языки, размер, файлы)
- ✅ **audit_quality** — чек-лист качества (тесты, CI, docs, типы)
- 🔍 **audit_honesty** — что обещает README vs что реально есть
- 📋 **generate_report** — финальный отчёт с score и verdict

## 📦 Установка

```bash
git clone https://github.com/shekelstrong/repo-auditor.git
cd repo-auditor
pip install -r requirements.txt
```

## 🛠 MCP Tools

### clone_repo
```python
result = await clone_repo.run("https://github.com/owner/repo", "/tmp/audit")
# → {status: "cloned", repo_path: "/tmp/audit"}
```

### analyze_structure
```python
result = await analyze_structure.run("/tmp/audit")
# → {total_files, total_size_mb, languages: {...}, top_files_by_size}
```

Сканирует структуру, детектит языки по расширениям, находит большие файлы.

### audit_quality
```python
result = await audit_quality.run("/tmp/audit")
# → {score: 0-100, checklist: {tests, ci, readme, ...}, recommendations}
```

10 пунктов чек-листа: tests / ci / readme / license / requirements / gitignore / docker / env_example / security / contributing.

### audit_honesty
```python
result = await audit_honesty.run("/tmp/audit")
# → {promises_in_readme, reality_check, honesty_score, honesty_issues}
```

Детектит обещания ("production-ready", "tests included") и проверяет реальность.

### generate_report
```python
result = await generate_report.run("/tmp/audit")
# → {final_score, structure, quality, honesty, red_flags, verdict: use/caution/avoid}
```

Финальный отчёт с verdict.

## 📁 Структура

```
repo-auditor/
├── README.md
├── LICENSE
├── SKILL.md
├── requirements.txt
├── src_mcp/
│   ├── server.py
│   └── tools/
│       ├── clone_repo.py
│       ├── analyze_structure.py
│       ├── audit_quality.py
│       ├── audit_honesty.py
│       └── generate_report.py
└── .github/workflows/ci.yml
```

## 🎯 Score

- **Quality** (50%): tests + ci + readme + license + types
- **Honesty** (30%): README обещает то что есть
- **Structure** (20%): кол-во файлов, языки

**Verdict:**
- `> 70` = use (можно брать в проект)
- `50-70` = caution (можно, но проверяй)
- `< 50` = avoid (не трогай)

## 📄 License

MIT © Vasiliy Nedopekin (shekelstrong)
