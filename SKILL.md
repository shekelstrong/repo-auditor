---
name: repo-auditor
description: Аудит GitHub-репозиториев. Клонирование, структура, качество кода (тесты/CI/docs), честность README (обещания vs реальность), финальный отчёт с verdict (use/caution/avoid).
---

# Repo Auditor

MCP-сервер для оценки чужих GitHub-репо перед использованием.

## Когда использовать

- Нашёл интересное репо, хочешь проверить качество
- Хочешь понять, не врёт ли README ("production-ready" = реально?)
- HR проверяет портфолио кандидата
- Делаешь security audit зависимости

## 5 tools

```
URL → clone_repo (клонировать)
    ↓
analyze_structure (языки, размер)
    ↓
audit_quality (тесты, CI, docs)
    ↓
audit_honesty (обещания vs реальность)
    ↓
generate_report (финальный отчёт + verdict)
```

## Алгоритм

### 1. clone_repo
git clone --depth=1 (быстро, только последний коммит).

### 2. analyze_structure
- total_files / total_size_mb
- languages (Python, TS, Go, Rust...)
- top_files_by_size (подозрительные большие)
- Skip: .git, node_modules, __pycache__, .venv

### 3. audit_quality
10 пунктов чек-листа:
- tests/, ci, readme, license, requirements, gitignore, docker, env_example, security, contributing

+ Python type hints (% функций с аннотациями).

### 4. audit_honesty
Детект promises в README:
- "production-ready", "complete", "fully implemented"
- "X tools", "MCP server", "telegram bot"
- "tests included", "100% tested"
- "secure", "encrypted"
- "7-day", "24 hours", "instant"

Reality check:
- tests_actually_present
- ci_present
- docker_present
- requirements_present
- TODO/FIXME count
- NotImplementedError files

### 5. generate_report
Final score = quality * 0.5 + honesty * 0.3 + structure * 0.2.

Verdict:
- > 70 = **use** (можно брать)
- 50-70 = **caution** (проверяй)
- < 50 = **avoid** (не трогай)

## Pitfalls

| Ошибка | Последствие | Как избежать |
|---|---|---|
| Судить по звёздам | 50K звёзд = deprecated код | Смотри на last commit, open issues, contributors |
| Верить "production-ready" | Код с NotImplementedError | audit_honesty |
| 500MB репо | Случайно закоммитили node_modules | Смотри на top_files_by_size |
| Нет тестов = "просто" | Ломается на каждом PR | audit_quality tests |
| README 10 страниц | Документация > код | Проверяй ratio |
| Travis CI в 2016 | Заброшен | Смотри на дату последнего CI запуска |

## Red Flags

- README обещает → реально нет
- Много TODO/FIXME
- Размер > 100MB
- CI не запускался 6+ месяцев
- Последний коммит 2+ года назад
- 1 contributor
- Нет тестов при "production-ready"

## Источники

4 скилла: repo-honesty-audit, github-repo-skill-mining, github-repo-audit, repomix-explorer.
