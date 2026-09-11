# Expedia Lite

A local classroom travel application: Vue frontend, FastAPI API, and Python CSV search. Part 1 only. The supplied fictional data is preserved in backend/data/; no real reservations are made.

## Setup (Windows PowerShell)

Open a terminal in this `Expedia Lite` folder. Python 3.10+ and Node 22.12+ are required (verified here with Python 3.14.7 and Node 24.20.0).

Check first: `python --version`, `node --version`, and `npm.cmd --version`. For an existing environment, check `backend\.venv\Scripts\python.exe -m pip show fastapi uvicorn` and `npm.cmd --prefix frontend ls --depth=0` before installing.

For a fresh checkout:

```powershell
python -m venv backend/.venv
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
```

Verify:

```powershell
backend\.venv\Scripts\python.exe -c "import fastapi, uvicorn; print(fastapi.__version__, uvicorn.__version__)"
npm.cmd --prefix frontend run build
```

## Run

Terminal 1, from this folder:

```powershell
backend\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Terminal 2, from this folder:

```powershell
npm.cmd --prefix frontend run dev
```

Open http://127.0.0.1:5173. Stop each server with Ctrl+C. API documentation: http://127.0.0.1:8000/docs. Vite forwards `/api` requests to FastAPI; use the development server for the complete local app. The build check creates frontend/dist but is not a standalone backend deployment.

## Search and verification

Search `Harbor Lantern Hotel`: expect T001 and T009, each two nights at $150/night ($300/stay). Search `No Such Hotel`: expect a clear empty result. Partial names and capitalization are ignored; blank input lists all 12 stays. Search is by hotel name, not city. Dates are fixed offered stays; sample dates are not filtered against today's date.

See [report.md](report.md) for observed browser checks and screenshots. The student confirmed the VS Code source review and both required browser checks. Repository: [expedia-lite](https://github.com/kuanenlee0925-blip/expedia-lite). The `part1` tag preserves the reviewed Part 1 application checkpoint; the report records its exact hash. Give the instructor access to this private repository before submission.

## Project context

- [Agent instructions](AGENTS.md)
- [Design](docs/design.md)
- [Selected prompts](prompts/selected.md)
- [Current handoff](handoffs/current.md)
- [Original data guide](backend/data/README.md)

Part 2 will seed SQLite once and add simulated booking, cancellation, history, and deletion on a feature branch while preserving the Part 1 checkpoint.
