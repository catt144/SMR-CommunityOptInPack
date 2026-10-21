# Station rows correction audit — 2026-10-21

Verdict and limits: `docs/agent/reports/STATION_ROWS_RELAY_20261021.md` §18.
Shipping code: `3aa5402`; execution HEAD: `aa7dac14da6c622a07a5c0a45b5580ecbf891e27`.
Executed model: Codex, GPT-6 per session instruction; exact runtime identifier and effort
not exposed. No game run, shipping edit, packing or upload.

Run the scripts with Python from the repository root. Dependencies are the repository's
train harnesses, `lupa`, Git, `rg`, the local archived game source trees and the immutable
first-audit directory `docs/archive/station_rows_audit_20261021/`. Native checks verify
body parity against 1.1.1.406343 (installed build 25579348 in the fingerprint receipt).
Fixture scheduling, requests and UI windows remain doubles.

| Script | Purpose | Output |
|---|---|---|
| `native_math.py` | Native-walk positive A1 cases, reservations/aliases, junctions/cycles and exact rational A2 oracle | `native_math_output.txt` |
| `ui_check.py` | Actual callbacks with window doubles: ownership seams, scroll/broadcast, refresh counts, help, clear | `ui_check_output.txt` |
| `current_boundary.py` | Compare working/non-working current station at `3aa5402`, `83149ea`, `5ba8f3f`; historical copies go to ignored scratch | `current_boundary_output.txt` |
| `contract.py` | Code/shape/name/wrapper/hub controls, pinned pre-audit records, real depot readers | `contract_output.txt` |
| `regressions.py` | Rerun the complete first-audit baseline and verify the expected historical counterexample stop | `regressions_output.txt` |
| `close_check.py` | Verify the completed documentation and untouched shipping/archive paths | `close_check_output.txt` |

`fingerprint_output.txt` records `python tools/doccheck.py --emit-fingerprint` before the
documentation edit; `final_doccheck_output.txt` records `python tools/doccheck.py` after it.
Each output includes its command, HEAD and exit. Outputs are historical receipts, not promises
about another checkout. N/U exercise current working-tree code; C requires it to match
`3aa5402`. C's record scans intentionally use `git show aa7dac1:...`, so they remain replayable
after the audit corrects the current prose. The close check instead verifies the edited records.

`regressions.py` exits zero only if the baseline passes and the old `adversarial.py` fails at
its first, now-false A1 counterexample assertion (Lua chunk line 90). That expected nested exit
1 reaches none of the old later witnesses; the new native/UI scripts assert their corrections
positively. The inherited caught food-stream diagnostic is compared by exact token count.
No earlier archive was edited. The scripts reuse its runtime/fixture source with explicit
boundaries; they do not treat its old failures as current passing behavior.

NOT RUN: engine scheduling/rebuild timing, real saves, drones/cabin, pixels/hit testing,
large-colony latency, player saves, either in-game shipping configuration, packing or upload.
