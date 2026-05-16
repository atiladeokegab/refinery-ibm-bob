# Refinery

IBM Bob modifies the COBOL. Refinery checks the work.

Built for the IBM Bob Hackathon 2026.

---

## The problem

The average COBOL programmer is over 55. The systems they maintain process $3 trillion a day: payroll, clearing, insurance, pensions. The people who understand them are retiring, and there is nobody coming up behind them fast enough.

IBM Bob can read the code and suggest changes. But the code is not the whole picture. The tolerance thresholds, the edge cases that got hardcoded after an incident in 1987, the reason this field is COMP-3 and not COMP: none of that is in the source file. It lives in one person's head. When that person leaves, it is gone.

Refinery captures it. Every flag, every CRO rejection, every "this is wrong because" gets recorded and fed back into Bob's knowledge base. Bob stops repeating the same mistakes on your estate because it now has your history.

---

## Product flow

```mermaid
flowchart TD
    DEV([Developer]) --> BOB[IBM Bob IDE\nrefactors COBOL]
    BOB -->|change detected| MCP[Refinery MCP Server]
    MCP --> AUDIT[Audit Engine\n8 verification checks]
    AUDIT --> VSCODE[VS Code Extension\ninline verdict]
    AUDIT --> V{Verdict}

    V -->|PASS| PDF[PDF Change Contract\nSHA-256 sealed]
    V -->|FLAGGED| RAG[(Bob Knowledge Base\nrecords failure reason)]

    PDF --> PORTAL[CRO Governance Portal]
    PORTAL --> CRO{CRO decision}

    CRO -->|Approved| DEPLOY([Deployment proceeds])
    CRO -->|Rejected + reason| RAG

    RAG -->|calibrates future changes| BOB

    style RAG fill:#1a1a18,color:#00D46A,stroke:#00D46A
    style V fill:#2a2a28,color:#F0EDE5,stroke:#3a3a38
    style CRO fill:#2a2a28,color:#F0EDE5,stroke:#3a3a38
    style DEPLOY fill:#003d20,color:#00D46A,stroke:#00D46A
```

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

The MCP server exposes Refinery's audit pipeline directly to Bob. Bob calls it after each modification so the verdict is available inside the IDE session without leaving the workflow.

### VS Code extension

The extension surfaces Refinery verdicts inline in the editor. When Bob finishes a change, the risk score and flagged layers appear as diagnostics on the modified file — no context switching to the Streamlit app required.

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
vscode-extension/  VS Code extension — inline verdicts in the editor
```

## Stack

- Python 3.11+, FastAPI, Streamlit
- IBM Bob (Granite) via MCP
- tree-sitter for COBOL parsing
- WeasyPrint for PDF change contracts
- SQLite for governance audit trail

---

*IBM Bob Hackathon, May 2026.*
