# Refinery — AI Change Contract Enforcer

> Built on IBM Bob · IBM Bob Hackathon 2026

Refinery is an independent verification and validation engine for AI-modified COBOL. When IBM Bob refactors legacy COBOL code, Refinery runs 8 verification layers to prove the change is semantically equivalent — then maps the blast radius across the entire estate before a single line ships.

---

## The workflow

### 1. IBM Bob modifies the COBOL

Bob optimises, refactors, or fixes a COBOL program directly in the IDE. The moment Bob completes a task, Refinery intercepts the change and runs its audit pipeline. If the change is unsafe, Refinery surfaces the verdict immediately — the **FLAGGED — risk score 100/100** banner appears inline so Bob and the developer see it before anything ships.

![IBM Bob IDE session — Refinery flags a risky change in real time](images/Screenshot%202026-05-16%20213031.png)

### 2. Refinery audits the change

8 verification layers run automatically: arithmetic equivalence, data types, control flow, memory layout, call graph, compiled output, error paths, and I/O behaviour. Every flagged change gets a risk score and a signed PDF change contract.

### 3. The feedback loop — Bob learns from every rejection

Every FLAGGED verdict and every CRO rejection is written back into Bob's RAG knowledge base. The next time Bob touches the same program or a similar pattern, it has the full history of what failed and why:

- **What Bob changed** — the exact transformation that was flagged
- **Why Refinery rejected it** — which of the 8 layers caught the drift and what the semantic difference was
- **Why the CRO rejected it** — the stated reason from the sign-off modal (e.g. "data type boundary violated on COMP-3 field", "blast radius exceeds threshold without mitigation plan")

This means Bob gets progressively safer over time on your specific estate — it is not a generic model but one that has been calibrated against your organisation's actual compliance failures.

### 4. CRO Governance Dashboard

Every audit lands in the governance portal. The Chief Risk Officer sees a live feed of all changes, verdicts, blast radius scores, and sign-off status.

![Refinery CRO Governance Portal — Audit Dashboard](images/Screenshot%202026-05-16%20213315.png)

### 5. CRO Sign-off

When blast radius exceeds the threshold, the CRO must approve before the change can ship. The sign-off is immutable — the record locks once submitted. The reason given by the CRO is fed back into Bob's knowledge base so future changes avoid the same failure mode.

![CRO Sign-off modal — blast radius 33, 3 systems affected](images/Screenshot%202026-05-16%20213328.png)

---

## Running locally

### Streamlit app (main demo)

```bash
pip install uv
uv sync
uv run streamlit run streamlit_app/app.py
```

### CRO Governance Portal

```bash
uv run uvicorn portal.main:app --reload --port 8001
```

Open http://localhost:8001 — login with `cro / refinery2026`

### MCP Server (IBM Bob integration)

```bash
uv run python mcp_server.py
```

---

## Project structure

```
audit/          8-layer verification engine
bob/            IBM Bob integration (narrator, RAG, providers)
  bob/rag/      Knowledge base — stores past failures and CRO rejections
estate/         Blast radius analyser — traces cross-system impact
parser/         COBOL AST parser
emulator/       Synthetic COBOL execution runner
streamlit_app/  Main demo UI
portal/         CRO Governance Portal (FastAPI)
mcp_server.py   MCP server for Bob IDE integration
```

## Tech stack

- Python 3.11+, FastAPI, Streamlit
- IBM Bob (Granite) via MCP
- tree-sitter for COBOL AST parsing
- WeasyPrint for PDF change contracts
- SQLite for governance audit trail
- RAG (retrieval-augmented generation) for Bob's compliance memory

---

*Submitted to the IBM Bob Hackathon, May 2026.*
