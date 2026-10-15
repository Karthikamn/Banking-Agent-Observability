# Banking Agent Observability Starter — Organizer Prototype

This is a safe, synthetic deterministic Loan Support Agent to help the organizer validate the use case before the event. It is not a real bank system, does not call a live LLM, and contains no real customer data.

## Windows quick start
1. Install Python 3.10+ from https://www.python.org/downloads/
2. Extract this ZIP to `C:\Hackathon\BankingAgent`
3. Open PowerShell in that folder.
4. Run `python --version`
5. Run `python -m venv .venv`
6. Activate: `.venv\Scripts\Activate.ps1`
7. Run `pip install -r requirements.txt`
8. Run each scenario:
   - `python agent.py --scenario healthy`
   - `python agent.py --scenario api_timeout`
   - `python agent.py --scenario api_500`
   - `python agent.py --scenario invalid_response`
   - `python agent.py --scenario quality_regression`
9. Run tests: `pytest -q`

Each scenario writes `data/latest_session.json`. It is overwritten by the next run unless you change `--output`.

## Included
- `agent.py`: mock agent and four mock banking API operations
- `data/sample_historical_sessions.json`: five synthetic historical sessions
- `data/sample_trace_events.csv`: example trace events
- `test_agent.py`: basic scenario tests

## Still to build
OpenTelemetry export/collector, PostgreSQL persistence, FastAPI session/replay endpoints, replay comparison UI, Streamlit/Plotly dashboards and Docker Compose.

## Safety
Use synthetic data only. Replay should use recorded/mock responses, never real banking systems or side-effecting calls. Store sanitized operational artifacts, not hidden chain-of-thought.
