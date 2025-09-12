# Using the MELD G/M Reference (JSON)

Identical schema to the YAML version; JSON is smallest-to-parse in many tools.

## How to load (Claude Code)
- Read JSON into `ref` with keys: `legend`, `g`, `m`, `rules`.
- Rows are compact arrays.

### Field map (compact keys)
- `c` = code (e.g., "G01", "M04")
- `s` = short description
- `m` = modal?  (`"1"` yes, `"0"` no, `"B"` = block-only effect)  *(G only)*
- `d` = default active at reset? (1/0) *(G only)*
- `t` = type: `"hs"` handshake, `"fb"` fast-bit *(M only)*
- `w` = when to execute: `"pre"` or `"post"` *(M only)*
- `p` = parameter list, strings like `"S(rpm)"`, `"X(sec)"` etc.
- `n` = notes


### Retrieval policy (tell the model)
1) Treat these files as the **sole source of truth** for G/M semantics on MELD L3/K2.
2) If a code/param is missing, say so; don't invent values.
3) When answering, **echo the code and key params** (e.g., `M04 S{rpm}`) and highlight hazards:
   - Add `G04 X0.5` before `M30`; newline after `M30`.
   - `F` must be > 0 before any move.
   - Prefer `G71`/`G700`; avoid mixed `G70/G710`; if units change with no motion, add `G04 X0.5`.
4) Prefer concise steps; show a minimal example when helpful.


### Micro examples
**Q:** How do I start the spindle and wait for speed?
**A:** Use `M04 S{rpm}` (handshake; waits to ≥95% setpoint). Example: `M04 S350`.

**Q:** What forces a precise stop at a corner?
**A:** `G60` modal accurate stop (reset by `G00`) or block-level `G09`.

**Q:** Safe program end?
**A:** Put `G04 X0.5` on the line before `M30`, ensure a newline after `M30`.


### Minimal prompt stub
```
System: You have a compact JSON MELD reference with keys legend/g/m/rules.
When asked about a code, scan the respective array by row[0].
Never hallucinate codes not present. Apply safety from rules.*
```
