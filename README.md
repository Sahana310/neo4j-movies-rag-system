# CineGraph — password-free Movies Graph QA

Runs in VS Code without Neo4j Desktop, Neo4j Aura, login, passwords, or API keys. The included `data/movies.json` contains a small **curated subset** of the public Neo4j Movies example graph, with Movie and Person nodes represented as JSON records and ACTED_IN / DIRECTED edges. It is not the complete Neo4j dataset and does not execute Cypher or use a live Neo4j database.

## Windows VS Code / PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 . Ask 'Who acted in The Matrix?', 'Who directed Top Gun?', or 'Tell me about Apollo 13'. No internet is required after dependencies are installed.

## Architecture

User question -> keyword retrieval over local graph-derived JSON -> ranked source records -> deterministic grounded natural-language response -> web chat with sources.

**RAG limitation:** This no-credentials default is retrieval-augmented **template generation**, not LLM generation. For a true LLM-backed RAG implementation, configure a separate LLM service or API key and update the generation layer. A live Neo4j graph database is likewise necessary if your assignment specifically requires Neo4j queries. Do not describe this offline subset as a complete live Neo4j deployment.

Dataset reference: https://github.com/neo4j-graph-examples/movies

## GitHub

Ensure `.gitignore` excludes `.venv/` and `.env`, then commit project files and push using Git.
