# Station rows build audit, 2026-10-21

Verdict and limits: `docs/agent/reports/STATION_ROWS_RELAY_20261021.md` §16.
Audited HEAD: `922a22cbb1fa38bf9d53417c31ad12e573118e8c`; shipping code at `83149ea`.
Executed model: Codex, GPT-6 per session instruction; exact runtime identifier and effort
not exposed. No game run or shipping edit.

From the repository root, with Python/lupa and this rig's archived source tree available:

```text
python docs/archive/station_rows_audit_20261021/adversarial.py
python docs/archive/station_rows_audit_20261021/baseline.py
python docs/archive/station_rows_audit_20261021/contract.py
python docs/archive/station_rows_audit_20261021/close_check.py
```

The corresponding `_output.txt` files contain the executed command, HEAD and process exit.
The fingerprint receipt additionally records `python tools/doccheck.py --emit-fingerprint`.
`adversarial.py` asserts the observed counterexamples: zero exit confirms reproduction,
not acceptance of the shipping build. The rational allocation search has a fixed seed.

`contract.py` includes assertions about the pre-audit wording in the outbox and D16.
Those claims were corrected by the audit commit. Reproduce that complete original receipt
on the audited HEAD; its record-presence checks intentionally fail against corrected text.
Its baseline UI comparison copies historical Lua to `scratch/station_audit_versions/` and
loads it in the harness; it never changes shipping files. The other scripts read the
checked-out shipping tree, so their command/HEAD and code hashes identify what they check.
`close_check.py` checks the completed audit records and enumerates the persisted-name scan.

All runtime objects other than the explicitly loaded archived native bodies are doubles.
Engine scheduling, save serialization, actual rebuilds, real cabin/drone service, pixels,
player saves and release actions were NOT RUN. Earlier prototype/review archives are unchanged.
