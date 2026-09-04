# E2E Test Infra: AI Teacher Platform

## Test Philosophy
- Multi-tier verification covering backend routes, schema contracts, frontend flow transitions, UI theme integrity, and adaptive loop data persistence.
- Opaque-box + integration testing.

## Verification Tiers
1. **Tier 1: Backend Unit & API Tests**
   - Pytest test suite (`pytest backend/tests`)
   - Endpoint test client validating all 14 API endpoints with realistic payloads.
2. **Tier 2: Frontend Compilation & TypeCheck**
   - `npm run build` in `frontend/` ensuring zero TypeScript/JSX errors.
3. **Tier 3: UI Theme & Static Integrity**
   - Regex scan for banned color tokens (`#2b1a07`, `#ff6f1e`, `#ce500a`, `#fdfbf9`).
   - Audit interactive elements for `<button>` semantics and hover states.
4. **Tier 4: Adaptive Feedback Loop Integration**
   - Ingestion -> Plan -> Quiz -> Submission -> Profile Update -> Recommendations -> Next Plan generation.

## Test Runner Commands
- Backend: `/home/dev/Desktop/projects/AI-InnovationHackathon/.venv/bin/python -m pytest backend/tests`
- Frontend Build: `cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build`
- Hex Audit: `grep -rn -E '#2b1a07|#ff6f1e|#ce500a|#fdfbf9' frontend/src/`
