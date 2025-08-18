# Overview
A sequenced set of small, focused PRs with explicit task lists and acceptance criteria you can hand to Google's Jules asynchronous agent. Targets Windows first, scales sensibly to larger datasets, and lays groundwork for Linux.

---

## Conventions (apply to every PR)
- **Branch naming:** `feature/<short-name>` or `infra/<short-name>`.
- **Commit style:** Conventional Commits (`feat:`, `fix:`, `perf:`, `chore:`, `test:`, `refactor:`).
- **CI gates (minimum):** ruff, black --check, mypy (strict-ish), pytest -q.
- **Definition of Done (DoD):** Tasks complete, tests green, docs updated, PR description follows template, changelog entry added.
- **PR Template:** Add once in PR #1 at `.github/pull_request_template.md` (sections: Context, Change, Screenshots/GIFs, Tests, Perf Impact, Risks, Rollback).

---

# Execution Order (milestones)
1. **PR1 - Repo hygiene & CI skeleton** (infra)
2. **PR2 - Data pipeline v1 (CSV->Parquet cache + Polars)**
3. **PR3 - Config validation + Column Mapping UI**
4. **PR4 - Performance/LOD (decimator + payload cap + slider)**
5. **PR5 - Voxelization + Isosurface Mode**
6. **PR6 - ROI Selection + Crossfilter**
7. **PR7 - Error Panel + Progress/Cancel UX**
8. **PR8 - Session Save/Load + Export**
9. **PR9 - Test Suite Upgrade (snapshot, property-based, perf markers, E2E)**
10. **PR10 - Windows Packaging & Release CI**
11. **PR11 - Docs + Demo Data**
12. **PR12 - Watch Folder / Live Reload (optional)**
13. **PR13 - Linux Containerization & Devcontainer (optional)**

---

## PR1 - Repo hygiene & CI skeleton
**Branch:** `infra/repo-hygiene-ci`

**Goal:** Standardize packaging, lint/format/type-check, basic CI, PR template.

**Scope:**
- Introduce `pyproject.toml` with runtime + dev deps.
- Add ruff, black, mypy config; pre-commit optional.
- Add GitHub Actions CI for lint, type, tests on 3.10-3.12.
- Add `.gitignore`; purge tracked cache/bytecode.
- Add LICENSE (MIT or your choice) and short repo description.
- Add `.github/pull_request_template.md` and basic issue templates.

**Out of scope:** Functional changes to app logic.

**Tasks:**
- [ ] Create `pyproject.toml` with deps: `dash`, `plotly`, `polars[pyarrow]`, `pydantic`, `kaleido`, `pytest`, `hypothesis`, `dash[testing]`, `ruff`, `black`, `mypy`.
- [ ] Configure ruff (in `pyproject`), set line-length 100 or 120; enable sensible rules.
- [ ] Configure mypy (ignore missing imports only as needed); enable `warn-redundant-casts`, `warn-unused-ignores`.
- [ ] Add `.github/workflows/ci.yml`: matrix 3.10-3.12; steps: setup-python, cache, `pip install .[dev]`, run ruff/black/mypy/pytest.
- [ ] Add `.gitignore` (Python, PyInstaller, build, cache, datasets, `.venv` etc.).
- [ ] Remove committed `__pycache__/` and other artifacts.
- [ ] Add `CHANGELOG.md` with Unreleased section.
- [ ] Add repo description, topics; add LICENSE.

**Acceptance Criteria:**
- CI runs on PR and `main` with green checks.
- Lint/format/type/test pass locally and in CI.
- PR template appears on new PRs.

**Tests:**
- Smoke test: `pytest -q` runs (may be empty initially).

**Docs:**
- `README` top badges for CI; short project description.

**Rollback:**
- Revert branch; CI remains as before.

**Estimate:** 0.5-1 day.

**Dependencies:** None.

**Labels:** `infra`, `ci`, `good-first-issue`.

---

## PR2 - Data pipeline v1 (CSV->Parquet cache + Polars)
**Branch:** `feat/data-pipeline-parquet`

**Goal:** Fast, repeatable data loads with typed schema; future-proof via Parquet and Polars.

**Scope:**
- File ingest service: detect schema, coerce dtypes, write Parquet cache (zstd), column pruning.
- Deterministic cache location `cache/` with file-hash keys.
- Use Polars lazy queries for filters/aggregations.

**Out of scope:** UI changes beyond wiring loader.

**Tasks:**
- [ ] Add `src/meldviz/io.py` with `load_csv_to_parquet(path)->CacheKey`, `load_parquet(cache_key)->pl.LazyFrame`.
- [ ] Implement hashing of file + settings for cache-keying.
- [ ] Dtype coercion rules: numeric->float32/int32 where safe; categorical for short strings.
- [ ] Column pruning: only materialize columns needed by the app.
- [ ] Integrate pipeline into app startup; fall back gracefully if cache missing.

**Acceptance Criteria:**
- First open of CSV writes Parquet; subsequent opens are >2x faster on 10k rows.
- Memory footprint reduced vs pandas baseline.
- Filters operate via Polars lazy frame.

**Tests:**
- Unit: coercion, hashing, cache reuse, column pruning.
- Property-based: random CSV permutations (headers order/types).

**Docs:**
- Add "Data pipeline" section with Parquet cache note.

**Rollback:**
- Flag to bypass Parquet path and use legacy reader.

**Estimate:** 1-2 days.

**Dependencies:** PR1.

**Labels:** `backend`, `performance`.

---

## PR3 - Config validation + Column Mapping UI
**Branch:** `feat/config-validation-column-mapping`

**Goal:** Make diverse CSV headers usable; strict validation with friendly errors.

**Scope:**
- Pydantic models for `config.json` and runtime settings.
- Column-mapping dialog to map arbitrary CSV headers -> canonical fields.
- Persist mappings per filename pattern/vendor.

**Out of scope:** Advanced rule-builder.

**Tasks:**
- [ ] Add `src/meldviz/config.py` (Pydantic models + validation errors).
- [ ] Add `src/meldviz/mapping.py` for header mapping + persistence.
- [ ] UI: modal to map columns; preview detected columns; save mapping.
- [ ] On load, apply mapping; warn on missing/extra columns.

**Acceptance Criteria:**
- Bad configs produce actionable messages; app does not crash.
- A CSV with different header names can be mapped once and re-used automatically.

**Tests:**
- Unit: valid/invalid configs; mapping persistence; partial mappings.
- E2E: upload CSV with odd headers -> map -> charts render.

**Docs:**
- README: "Column Mapping" walkthrough with screenshots.

**Rollback:**
- Env flag disables mapping; falls back to hard-coded headers.

**Estimate:** 1-2 days.

**Dependencies:** PR2.

**Labels:** `ux`, `validation`.

---

## PR4 - Performance/LOD (decimator + payload cap + slider)
**Branch:** `perf/lod-decimator`

**Goal:** Keep interactivity smooth by capping point count and payload size.

**Scope:**
- Server-side decimator: reservoir or stratified by voxel/region/value.
- Payload cap (~6 MB per update) and live point-count readout.
- UI "Performance" slider (Quality <-> Speed) controlling sample %.

**Out of scope:** Voxel/isosurface.

**Tasks:**
- [ ] Implement `src/meldviz/lod.py` with decimation strategies.
- [ ] Hook into filter pipeline; emit sampled dataframe to the client.
- [ ] Add UI slider + label; display current point count and estimated payload.

**Acceptance Criteria:**
- With 100k rows, interactions stay <800 ms median.
- Slider changes sample size and latency as expected.

**Tests:**
- Unit: deterministic sampling with seeded RNG.
- Perf marker: 100k dataset interaction <800 ms.

**Docs:**
- Add "Performance Mode" section explaining tradeoffs.

**Rollback:**
- Feature flag to bypass decimator.

**Estimate:** 1 day.

**Dependencies:** PR2.

**Labels:** `performance`, `ux`.

---

## PR5 - Voxelization + Isosurface Mode
**Branch:** `feat/voxel-isosurface`

**Goal:** Scale to big data via volume/isosurface rendering.

**Scope:**
- `histogramdd`-based voxelizer (counts/mean per cell) with adjustable resolution (64^3 default).
- Plotly `isosurface` or `mesh3d` path (marching cubes) for thresholded views.
- Toggle: Points <-> Voxels.

**Out of scope:** Advanced GPU acceleration.

**Tasks:**
- [ ] Implement `src/meldviz/voxel.py` (voxel grid build + stats).
- [ ] UI toggle and resolution selector; remember user preference.
- [ ] Render isosurface from selected scalar (e.g., temp/force) + threshold.

**Acceptance Criteria:**
- 1M synthetic rows voxelize to 64^3 in <=2.5 s on baseline box.
- Isosurface/points toggle works; threshold slider updates view.

**Tests:**
- Unit: voxel grid correctness on known distributions.
- Snapshot: figure JSON for a canonical isosurface.
- Perf marker: voxelization time budget.

**Docs:**
- Add section with screenshots/GIF.

**Rollback:**
- Fallback to Points mode if voxelization exceeds time budget.

**Estimate:** 2 days.

**Dependencies:** PR4.

**Labels:** `feature`, `performance`, `3d`.

---

## PR6 - ROI Selection + Crossfilter
**Branch:** `feat/roi-crossfilter`

**Goal:** Select a region (box/lasso) and filter all linked charts server-side.

**Scope:**
- 3D ROI tools (box; lasso if practical) producing server-understandable bounds.
- Server applies ROI to Polars pipeline; updates linked 2D/3D charts.
- "Export ROI as CSV" button.

**Out of scope:** Persistent named ROIs (future).

**Tasks:**
- [ ] Add ROI primitives `src/meldviz/roi.py` (AABB, convex hull optional).
- [ ] UI controls + overlay; debounced updates to server.
- [ ] Wire ROI to pipeline; expose export endpoint.

**Acceptance Criteria:**
- ROI reduces dataset and updates in <1 s at 100k.
- Exported CSV matches filtered points.

**Tests:**
- Unit: ROI math; edge cases (empty, out-of-bounds).
- E2E: draw ROI -> charts update -> export file equals expected.

**Docs:**
- Short guide with GIF.

**Rollback:**
- Disable ROI controls via feature flag.

**Estimate:** 1-2 days.

**Dependencies:** PR4, PR5.

**Labels:** `feature`, `ux`.

---

## PR7 - Error Panel + Progress/Cancel UX
**Branch:** `feat/error-panel-progress`

**Goal:** Fail clearly and give users control during heavy ops.

**Scope:**
- Visible error panel for parse/missing-column/empty-set.
- Long-running tasks (voxelize/export) via Dash `long_callback` or worker; show progress & cancel.

**Out of scope:** Full task queue UI.

**Tasks:**
- [ ] Add error surface component; standardize error objects.
- [ ] Wrap heavy ops; add progress bar modal + cancel button.

**Acceptance Criteria:**
- Malformed CSV shows actionable errors (no crash).
- Cancel stops voxelization/export within ~200 ms tick.

**Tests:**
- E2E: upload bad CSV -> error panel; start heavy task -> cancel works.

**Docs:**
- Troubleshooting section.

**Rollback:**
- Feature flag disables long-callback path.

**Estimate:** 1 day.

**Dependencies:** PR2, PR5.

**Labels:** `ux`, `stability`.

---

## PR8 - Session Save/Load + Export
**Branch:** `feat/session-export`

**Goal:** Persist user state and export visuals deterministically.

**Scope:**
- Save/load session (`.meldviz` JSON): layout, filters, column mapping, theme.
- Image export via Kaleido (PNG/SVG) with version string.

**Out of scope:** Cloud sync.

**Tasks:**
- [ ] Implement `src/meldviz/session.py` with schema + versioning.
- [ ] UI: Save/Load session; Export current view.
- [ ] Stamp app version on exported images.

**Acceptance Criteria:**
- Close/reopen with saved session reproduces the view.
- Exports are pixel/JSON-identical across runs for same data.

**Tests:**
- Unit: roundtrip session serialize/deserialize.
- Snapshot: figure JSONs stable.

**Docs:**
- README: Session & Export usage.

**Rollback:**
- Safe ignore of unknown session keys.

**Estimate:** 1 day.

**Dependencies:** PR4/5/6.

**Labels:** `feature`, `state`.

---

## PR9 - Test Suite Upgrade (snapshot, property-based, perf, E2E)
**Branch:** `test/suite-upgrade`

**Goal:** Catch regressions early and enforce performance budgets.

**Scope:**
- JSON snapshot testing for figures.
- Hypothesis generators for messy CSVs.
- E2E with `dash[testing]` scenarios.
- Perf markers for 10k/100k/1M (skipped in CI except 10k/100k).

**Out of scope:** Visual pixel diffs (optional later).

**Tasks:**
- [ ] Add `tests/generators.py` for synthetic data.
- [ ] Add snapshot tests for scatter3d, isosurface, ROI flow.
- [ ] Add E2E: upload -> map -> filter -> toggle -> export.
- [ ] Add perf markers + baseline thresholds.

**Acceptance Criteria:**
- CI runs unit + snapshot + E2E (headless) under 10 minutes.
- Flaky tests quarantined via marker.

**Docs:**
- `CONTRIBUTING.md` test sections.

**Rollback:**
- Disable perf markers via env in CI if needed.

**Estimate:** 1-2 days.

**Dependencies:** PR1-PR8.

**Labels:** `test`, `quality`.

---

## PR10 - Windows Packaging & Release CI
**Branch:** `release/windows-packaging`

**Goal:** Ship a one-click Windows build and publish on tag.

**Scope:**
- PyInstaller spec (one-folder).
- Inno Setup script for installer (optional first pass).
- GitHub Actions: on tag -> build artifact -> GitHub Release upload.
- App data path in `%APPDATA%/MELD_Visualizer`.

**Out of scope:** macOS packaging.

**Tasks:**
- [ ] Add `scripts/meldviz.spec` with hidden-imports (plotly, kaleido, polars).
- [ ] Add `scripts/build_win.bat` and optional `inno_setup.iss`.
- [ ] Add workflow `.github/workflows/release.yml` (tag push).
- [ ] Include sample data + session file in installer (optional).

**Acceptance Criteria:**
- Tagged release produces downloadable installer/zip.
- Fresh Windows VM can run the app offline with demo data.

**Tests:**
- Smoke: run packaged app, open demo session, export image.

**Docs:**
- README: download/install steps; offline note.

**Rollback:**
- Delete release; revert workflow.

**Estimate:** 1 day.

**Dependencies:** PR1, PR2 minimal.

**Labels:** `release`, `windows`.

---

## PR11 - Docs + Demo Data
**Branch:** `docs/demo-data`

**Goal:** Show, do not tell -- demo CSVs, screenshots, short guides.

**Scope:**
- Anonymized small CSV in `/demo/`.
- Screenshots/GIFs of key flows.
- README restructure; quickstart; features tour.
- `CONTRIBUTING.md` + issue templates.

**Out of scope:** Full user manual.

**Tasks:**
- [ ] Add `/demo/sample.csv` and `/demo/sample.meldviz`.
- [ ] Add `docs/` assets; update README with images.
- [ ] Add `CONTRIBUTING.md` + `.github/ISSUE_TEMPLATE/*.yml`.

**Acceptance Criteria:**
- New users can run demo in <=5 minutes.
- Clear contribution guide is present.

**Tests:**
- Link checker action (optional).

**Rollback:**
- Revert docs-only changes.

**Estimate:** 0.5-1 day.

**Dependencies:** PR1, PR2.

**Labels:** `docs`, `dx`.

---

## PR12 - Watch Folder / Live Reload (optional)
**Branch:** `feat/watch-folder`

**Goal:** Auto-refresh when CSV/Parquet grows during a run.

**Scope:**
- Watch a directory/file; re-materialize views periodically.
- Debounce + status indicator.

**Out of scope:** Complex conflict resolution.

**Tasks:**
- [ ] File watcher (watchdog) to detect appends.
- [ ] Periodic refresh of Polars lazy frame; preserve UI state.

**Acceptance Criteria:**
- When file grows, charts update without manual reload.

**Tests:**
- Integration: append to file -> view updates.

**Docs:**
- Note on performance and safety.

**Rollback:**
- Disable watcher via config.

**Estimate:** 1 day.

**Dependencies:** PR2.

**Labels:** `feature`, `realtime`.

---

## PR13 - Linux Containerization & Devcontainer (optional)
**Branch:** `infra/linux-container-devcontainer`

**Goal:** Make Linux runs easy and set stage for future native packaging.

**Scope:**
- `Dockerfile` (slim Python base) + `docker-compose.yml` for local run.
- `.devcontainer/devcontainer.json` for VS Code.

**Out of scope:** Native Linux installer.

**Tasks:**
- [ ] Add Dockerfile; expose port; mount volumes for data/cache.
- [ ] Add compose for one-command run.
- [ ] Add devcontainer with recommended extensions, Python path.

**Acceptance Criteria:**
- `docker compose up` serves the app at `127.0.0.1:8050`.

**Tests:**
- CI optional job to build container.

**Docs:**
- README: "Run with Docker" section.

**Rollback:**
- Remove container files; unaffected host runs.

**Estimate:** 0.5-1 day.

**Dependencies:** PR1.

**Labels:** `infra`, `linux`.

---

# Hand-off Notes for Jules
- Each PR is self-contained with feature flags where useful.
- Prefer small, reviewable commits.
- Link PRs to this plan and check off tasks in the PR description.
- Post benchmark numbers (before/after) for PRs 4-6.
- Attach screenshots/GIFs for PRs touching UI.