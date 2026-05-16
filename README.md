# Refinery

IBM Bob modifies the COBOL. Refinery checks the work.

Built for the IBM Bob Hackathon 2026.

---

## How it works

### Bob modifies the COBOL

Bob optimises or refactors a COBOL program in the IDE. Refinery intercepts the change and runs its audit pipeline. If something is wrong, the verdict appears immediately — FLAGGED with a risk score — before anything gets committed.

![IBM Bob IDE — Refinery flags a risky change in real time](images/Screenshot%202026-05-16%20213031.png)

### The audit

Eight checks run: arithmetic equivalence, data types, control flow, memory layout, call graph, compiled output, error paths, and I/O behaviour. Each check either passes or flags. A flagged change gets a PDF change contract with a SHA-256 hash for chain of custody.

### The feedback loop

Every flagged verdict and every CRO rejection goes back into Bob's RAG knowledge base. Next time Bob touches the same program or a similar pattern, it has the history of what failed and why:

- What the change was and which check caught it
- What the semantic difference was
- Why the CRO rejected it (e.g. "data type boundary violated on COMP-3 field")

Bob does not stay generic. It gets progressively more accurate on your specific estate because it is learning from your actual compliance failures, not someone else's.

### Governance dashboard

Every audit lands in the governance portal. The CRO sees verdicts, risk scores, blast radius scores, and sign-off status.

![Refinery CRO Governance Portal — Audit Dashboard](images/Screenshot%202026-05-16%20213315.png)

### CRO sign-off

When blast radius exceeds the threshold, the CRO must approve before the change ships. The record locks once submitted. The reason given goes back into Bob's knowledge base so the same mistake does not get made twice.

![CRO Sign-off modal — blast radius 33, 3 systems affected](images/Screenshot%202026-05-16%20213328.png)

---

## Running it

### Streamlit app (main demo)

```bash
pip install uv
uv sync
uv run streamlit run streamlit_app/app.py
```

### CRO portal

```bash
uv run uvicorn portal.main:app --reload --port 8001
```

http://localhost:8001 — login: `cro / refinery2026`

### MCP server (Bob IDE integration)

```bash
uv run python mcp_server.py
```

---

## Structure

```
audit/          verification engine (8 checks)
bob/            IBM Bob integration and RAG knowledge base
estate/         blast radius — traces cross-system impact
parser/         COBOL AST parser
emulator/       synthetic COBOL runner
streamlit_app/  demo UI
portal/         CRO governance portal (FastAPI)
mcp_server.py   MCP server for Bob IDE
```

## Stack

- Python 3.11+, FastAPI, Streamlit
- IBM Bob (Granite) via MCP
- tree-sitter for COBOL parsing
- WeasyPrint for PDF change contracts
- SQLite for governance audit trail

---

*IBM Bob Hackathon, May 2026.*
