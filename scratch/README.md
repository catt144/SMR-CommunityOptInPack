# scratch/

Working space for any session or subagent. Write freely here — no permission
needed. This folder is never committed (see `.gitignore`) and never cited from
a committed document: nothing here is evidence or a record.

If a committed document needs to cite a file, that file belongs in the repo
instead — see the fix pack's `scratch/README.md` for the case that proves it
(a fan-out gate-evidence file written outside its repo entirely, then cited
by report command lines; the citations survived, the file did not, because
nothing outside the repo is durable). Put evidence a report depends on under
`docs/` instead.

The eviction prompt (`docs/agent/prompts/perma/STATE_EVICTION.md`) sweeps
files here older than 14 days. `README.md` itself is never swept.

Durable material that must not be committed — the case above is a *working*
file, not durable evidence — belongs in `../local/` instead, which is never
swept and is entry-gated by `local/README.md`.
