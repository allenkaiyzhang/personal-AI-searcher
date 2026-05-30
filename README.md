# personal-AI-searcher

`personal-AI-searcher` is an MVP research-memory search service. It is not a generic `Query -> Result` search API. Its goal is to validate a loop:

`Topic -> Evidence -> Timeline -> Insight -> Updated Research Answer`

The service searches the web, stores evidence, maintains topic timelines, keeps historical judgments, and reuses prior research context in later searches.

## Workflow

1. Match a query to a long-running `Topic`.
2. Load previous `Insight`, `Evidence`, and `TimelineEvent` records when memory is enabled.
3. Plan one to three search queries.
4. Search Bing HTML results.
5. Fetch and extract page content.
6. Convert results into rule-based `Evidence`.
7. Create timeline updates for new evidence.
8. Update insight when enough new evidence arrives.
9. Generate a Markdown research report.

The MVP intentionally does not use an LLM. Reports are rule-based summaries and should not be considered factual conclusions.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Initialize Database

```bash
python -m app.db.init_db
```

The default database URL is `sqlite:///./data/searcher.db`.

## Start Service

```bash
uvicorn app.main:app --reload
```

## One-Command Deployment

Windows PowerShell:

```powershell
.\scripts\deploy.ps1
```

Useful options:

```powershell
.\scripts\deploy.ps1 -Port 8080
.\scripts\deploy.ps1 -SkipTests
.\scripts\deploy.ps1 -NoStart
.\scripts\deploy.ps1 -RecreateVenv
.\scripts\deploy.ps1 -UpgradePip
```

Linux/macOS:

```bash
sh scripts/deploy.sh
```

Useful environment variables:

```bash
PORT=8080 sh scripts/deploy.sh
SKIP_TESTS=1 sh scripts/deploy.sh
NO_START=1 sh scripts/deploy.sh
RECREATE_VENV=1 sh scripts/deploy.sh
UPGRADE_PIP=1 sh scripts/deploy.sh
```

## API Examples

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/topics \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"DRAM Market\",\"aliases\":[\"DRAM\",\"HBM\",\"Micron\"],\"description\":\"Memory market research\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Is DRAM still in an upcycle?\",\"topic_hint\":\"DRAM\",\"max_results\":5,\"use_memory\":true,\"update_memory\":true}"
```

## Roadmap

- V2: PostgreSQL
- V3: LLM Evidence Extraction
- V4: Vector Search
- V5: Personalized Ranking
