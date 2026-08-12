# The Prompt-Chain Method — a playbook from the run that proved it (2026-08-03)

**Written by the chain-12 QA session at the owner's request, at peak knowledge:
this session verified the full 18-prompt chain end to end (inbox audit, flip
sampling against primary logs, consistency pass, adversarial adjudications),
so the claims below about *why* it worked are evidenced, not theorized.**
The chain ran 2026-08-01 → 2026-08-03 and closed problems the project had
classed as intractable — F86 save-safety (discovery to verified repair of both
proven leak sites), the 66-premise blind audit, six approved fixes built and
play-verified, three owner-routed adjudications — with **zero dropped items
across 18 self-consuming prompts** and every sampled claim verifying against
primary evidence.

This document is the reusable method. The authoring mechanics it builds on are
`agent/WORKFLOW.md` "Authoring a prompt" (elements 1–7) — read those first;
this adds the chain-level structure and the lessons.

---

## 1 · What the method is, in one paragraph

Decompose a large effort into **many focused prompts sized to finish
comfortably in one session's context**, numbered in a folder that acts as a
**self-consuming queue**: each prompt ends by appending its handoff notes to
the NEXT prompt's inbox (or to whichever later prompt owns a discovered item),
committing, and **deleting its own file in the same commit**. The folder's
emptiness is the objective done-condition. The final prompt is always an
**adversarial backward QA** with fresh context that trusts nothing forward.

## 2 · Why it worked — mechanisms, each with its evidence from this run

1. **Self-consumption forces completion semantics.** A prompt cannot linger
   half-done: it finishes, or it self-splits at a clean commit boundary
   (rule 3) into a continuation that is a first-class chain member. Five
   splits happened (4→4b, 5→5b, 6b, 8→8b/8c, 8b→8b2); all were clean; the
   QA found no split that lost state. *Contrast: every long-lived "standing"
   document in this project drifted; no consumed prompt did.*
2. **Written inbox/outbox makes handoffs verifiable — and they verified.**
   Nothing owed ever lived in a session's memory. The QA audited all 17
   close-out commits: every outbox landed in the successor + the terminal QA
   prompt + the manifest, in one commit. Zero orphaned notes in 18 prompts.
3. **Mandatory re-derivation beat inheritance, repeatedly, in both
   directions.** The chain's biggest wins came from prompts ordered to
   re-derive premises rather than trust specs: a route recorded *impossible*
   existed (C23 → F97 shipped at a fraction of its approved cost); a route
   recorded *"verified feasible"* did not exist (F46, correctly declined);
   three approved-spec claims fell on re-derivation (D10) and two builds
   shipped because their premises held byte-verbatim (D12). **Rule to carry:
   the builder re-verifies the ROUTE even when told not to re-derive the
   design — every route failure this week sat above individually-correct
   citations.**
4. **Predictions written before runs.** PT-58/60/61/62 all recorded numbered
   predictions before any leg ran, which made results falsifiable, made
   misses diagnosable (PT-60's 79/79 vs predicted 73/79 exposed an
   account-state fact, not a defect), and made the QA's log-verification
   possible at all.
5. **Owner decisions routed, never absorbed — with provisional approval as
   the unlock.** "Build it, but it's not locked — the QA reviews it" (F97)
   and "let the QA look before we make hard decisions" (D12) let building
   proceed at full speed *without* laundering judgment calls into faits
   accomplis. All three routed adjudications were decidable downstream
   because the routing preserved the evidence and the open question.
6. **The adversarial terminal QA is where the method pays compound
   interest.** Fresh context + a different model + "every 'done' is a claim"
   found what forward motion structurally cannot: stale banners above their
   own resolutions, a silently excluded observation in a scored table, a
   heading tag contradicting its own entry, and a permanent evidence loss
   (log rotation) — while *confirming* the work itself everywhere it sampled.
7. **Blind controls are worth their cost.** The sealed BLIND_AUDIT (a fresh
   session grading all 66 fix premises with docs off-limits, examined only by
   the terminal QA) independently validated the pack's evidence base AND
   surfaced findings the informed record had missed (the F55 intent tell).
   The seal held because it was written into every prompt as a named rule
   with a required handoff attestation.
8. **Mistake capture as corpus, not shame (chain rule 4b).** Every drift
   instance — even ten-second fixes — was appended to the QA's evidence list.
   Result: a 40-instance corpus that produced a structural diagnosis
   (`DOC_STRUCTURE_REVIEW.md`) instead of another round of patching. *A
   silently-corrected instance is destroyed evidence* proved to be one of the
   most valuable rules in the chain.
9. **Scope fences and stop conditions were honored under pressure.** Prompt 8
   stopped rather than force a conversion whose route had dissolved; prompt
   11 refused to self-close a P1 where the reporter was also the adjudicator.
   Fences work when they are written in the prompt, not assumed.
10. **The model division of labor is not a convention — it is what makes the
    method affordable AND accurate, and the owner rates it load-bearing.**
    (Owner, 2026-08-03, on the record: the chain was co-designed by the owner
    with a top-tier session, and **the per-prompt model assignment was
    specifically the Fable authoring session's own decision** — the owner
    could guess at it but not be sure, and rates the resulting division
    load-bearing: *"that model division of labor is the only way this
    works"*.) The economics, both
    directions: run everything on the volume tier and accuracy drops exactly
    where error compounds; run everything — or even half — on the scarce top
    tier and usage limits stretch a ~24-hour chain across one to two weeks.
    **This chain placed the top tier on 3 of 18 prompts (~17%)**: the spec
    (prompt 3 — where a wrong decision poisons every downstream build), the
    highest-risk build (prompt 4, Tier 1 — save-safety code with the worst
    failure mode), and the terminal QA (prompt 12 — the adversary everything
    else is checked by). The volume tier ran the sweeps, the spec-guided
    builds, the legs, and the records — work where the spec-plus-re-derivation
    discipline bounds the cost of any single error. Routing lives in the
    FILENAME only; prompt bodies stay model-neutral so the owner can re-route
    per task. **The placement rule to reuse: the scarce tier goes where errors
    COMPOUND (design, adjudication, the final audit) and where independence
    matters (fresh-context QA); the volume tier goes where errors are CAUGHT
    downstream by a leg, a probe, or the QA.**

## 3 · Failure modes observed, with the countermeasure each earned

| failure | instance | countermeasure (adopt at authoring time) |
|---|---|---|
| Routing without preconditions | two items hopped 3 prompts each (a suite-run debt; C40's enacted-law need) | every routed item carries **TAKEABLE WHEN <condition>**; situation-gated items go to the checklist as riders, not to prompts |
| The manifest no prompt owns | the README chain table went stale about the chain (row 8b2) | the manifest gets an explicit owner: each prompt's close-out updates its OWN row as part of the deletion commit checklist |
| Briefs staler than entries | prompt 7's brief contradicted the C33 entry it described | briefs cite entries; sessions act on the ENTRY, and the brief says so |
| Specs authoritative on design, unreliable on detail | 7 of the prompt-7-era specs had a defective supporting detail; all 7 shapes survived | "do not re-derive the design" never means "do not verify the route"; tag spec details with provenance (MEASURED / SOURCE / INFERRED) |
| A prompt that needs the keyboard | prompt 11's jobs 2–4 needed the owner; the file could not self-consume as designed | mark attended prompts as such up front; split attended and unattended halves at authoring time |
| Context-edge risk | none bitten — because rule 3 existed | keep the self-split rule verbatim; never push a job to the edge of a window |
| Evidence rotation | the founding logs aged off disk (~20-file cap) before the QA could re-read them | any leg whose numbers a status flip will cite gets its log archived in the same commit |
| ⛔ A seal the standing rules defeat (f11-f99 chain, 2026-08-03) | the sealed prompt 1 was force-fed sealed material BEFORE it opened its own prompt: `CLAUDE.md` makes STATE.md a mandatory whole-file read (its F11/F99 paragraphs were sealed), and chain rule 1's `git log --oneline -10` prints the sealed commits' subject lines. The attestation was honest and the damage was contained (everything AGREEING with the anchor was discounted; only anchor-contradicting findings were counted) — but the seal was structurally unholdable | seal at the SOURCE, not the reader: before the chain starts, EXTRACT the sealed STATE.md paragraphs into a sealed side-file and leave a one-line pointer in STATE.md; prescribe a subject-hiding staleness check in the sealed prompt (`git log --format=%h -10` + `git pull`); and keep the attestation requirement — a broken seal honestly mapped (what leaked, what it anchors) preserved most of this second opinion's value |

| ⛔ Parked instruments pass every static gate and still fail live (unattended-1, 2026-08-04 — the first Opus-executes/Fable-audits instance) | 3 of 7 parked probes were parse-swept GREEN **and** Src-verified, and still produced wrong answers on their first run (an undefined helper every payload called; a completion counter that could not fail; a discarded `pcall` that turned 34 raises into a false vegetation sentence). The executor caught and rewrote all three MID-RUN via its own pre-launch cross-check and falsifier discipline, archiving every voided log beside the good one. **What the terminal audit floor then caught, honestly: no verdict** — every leg verdict survived re-derivation against the logs; the audit's yield was hygiene (a self-contradictory entry heading the mid-run correction had missed, an 11-vs-9 log miscount, a leftover staged save from the PREVIOUS chain, one ledger conflation). | Two halves. **Authoring:** static gates are necessary, never sufficient — briefs mandate the used-vs-defined resolution cross-check, a named liveness witness for every completion counter, printed `pcall` results, and no per-chain fact in a per-process flag (all now binding in `WORKFLOW.md` Co-runs). **Method:** the audit tier's value on a run whose executor self-corrects visibly is *certification plus residue*, not rescue — keep the tier (the executor said in its own handoff it was the wrong person to certify its own rewrites, and it was right), and keep the void-log-beside-good-log practice, which is what makes a post-hoc audit possible at all. |

| ⛔ A run's preconditions include state a PREVIOUS chain mutated, and the unblock is owner-only (unattended-2, 2026-08-11 — the first Opus-builds/Fable-audits chain that SHIPPED code) | The night's first launch read `pack=0/0 active`: corun-batch-2's leg T had disabled the pack in the Mod Manager a day earlier and no close-out owned the re-enable. The payload had no run-condition gate, so six steps banked readings about code that never executed; the unblock was one human click, unscriptable (`AccountStorage`/`SaveAccountStorage`/`ModsReloadItems` all ModEnvBlacklist keys, no console at the main menu), owner asleep. The executor spent the dead time on a **declared HARNESS REHEARSAL** — the mode flipped by the arm script and read back off disk, a `MODE` banner in the log, every verdict-bearing line stamped `VOID` — which proved the three-load/two-round-trip flow and both fresh harness fixes (EF-050's verbatim savename, the new gate). The owner's re-run then verified all four items in a single shot; the terminal audit sustained every verdict. | **Authoring:** a chain whose run depends on externally-mutable state (mod enabled, cloud sync, account settings) gates on that state AT RUN TOP, and the gate STOPS the run (WORKFLOW batch-2 rule 7 as amended 2026-08-11); any leg that mutates such state HANDS THE RESTORE BACK to the owner explicitly in its close-out. **Method:** when a run blocks on an owner-only unblock, don't park — prove the instrument with a declared-VOID rehearsal (mode armed by script and read off disk, bannered in the log, verdict lines stamped so the log can never be quoted as a measurement) so the unblocked re-run is single-shot instead of a second night of harness archaeology. |

| ⛔ An attended sitting is a priority queue the owner may reorder live, and the brief's minutes model does not survive contact (corun-batch-1, 2026-08-05 — the first BATCHED attended sitting) | The sitting ran 2 of its 5 legs and ~2 h of owner time against a ~24-minute promise — but most of the overrun was the owner deliberately chasing their own leads (the F99 hunt, the dev-cheat exploration), which produced the sitting's best finds (`F101`, both F99 samples) and which the owner then ruled an **override, not scored against the estimate**. The rig's own genuine miss was separable and small in kind but large in effect: one moment budgeted at 3 min took ~25 because its prep-measured fixture had evaporated (nothing re-confirmed it at sitting time, and no instrument could find a replacement subject). Structurally, the rig has no input path into a running game, so every console line was the owner's hands — a cost class the measure-moments model cannot see. | Three halves. **Authoring:** an attended brief is a PRIORITY QUEUE, not a schedule — order legs so a truncated sitting still banks the decider first, and treat owner deviation as a feature to absorb (witness discipline applies to whatever runs, planned or not), never a variance to explain away; once the owner overrides onto a lead, state the plan's position once and then stop — no per-message back-on-track reminders, and the session keeps the sent/checked/outstanding ledger so the owner does not have to (owner rule 2026-08-05, verbatim in WORKFLOW Co-runs). **Estimating:** re-confirm every fixture AT SITTING TIME, name a subject-finder instrument per moment, and budget console-driving explicitly until the rig has an input path (all binding in `WORKFLOW.md` Co-runs). **Scoring:** separate owner-directed deviation from rig misses before scoring anything — and only the owner may rule their own time out of scope. |

| ⛔ Evidence the terminal audit cannot re-read: owner verbatims that live only in the session transcript (corun-pt15, 2026-08-11 — the first chain designed to reach a `tested` grant) | The sitting gathered four owner verbatims at measure moments and pushed exactly ONE through the harness's log-note primitive (F85's); the other three — including the verdict backing F07's `tested` grant — exist only in the session transcript. The sitting flagged this honestly and deferred the grant ruling to the audit rather than assuming, which is the right half of the pattern; the audit sustained the grant (owner eyes attended the measure moment, the quote is verbatim on the entry, everything forced is named in the grant) but had to rule on evidence it could not re-read, and a future re-audit never can. | Two halves. **Authoring:** the sitting prompt MANDATES relaying every owner verbatim through the log-note primitive the moment it is spoken (now binding in `WORKFLOW.md` Co-runs, corun-pt15 rule 3) — chat stays where the owner speaks and transcript quotes stay quotable, but a log-resident quote is re-readable forever. **Method:** when a sitting knows a grant's provenance is mixed, deferring the ruling to the terminal audit WITH the exposure stated (the notes' "the audit should rule on it rather than assume") is the correct move — keep it; an upstream prompt that grades its own strongest claim is the failure shape. |

| ⛔ A pre-flighted console line can still carry an untested ASSUMPTION about game state — and the operator judges by the screen (corun-pt60, 2026-08-12 — the batch-coverage co-run) | Prep pre-flighted every console line for syntax, but the brief's order assumed a console at the main menu. At the sitting the kit's own boot line said the console only comes up "once in a colony"; the operator inferred "no console at the main menu" and spent an extra owner load (~2 min) to reach one. The archived log then proved the inference wrong in one direction: the menu command EXECUTED and reached the log (`CP60.Menu()` at `Lua 0:02:57`) — only the on-screen ECHO was missing, because `ConsolePrint` had no UI. Two separable failures: pre-flight validated syntax but not the state assumption, and the operator treated a silent screen as a failed command. ⭐ The wasted load was banked anyway as an accidental negative control (a post-batch save loading with zero save-state heals). | **Authoring:** a brief that drives a console names WHERE each line runs (menu vs colony) and states the echo contract — at the main menu, input EXECUTES but does not display, so the operator must judge by the LOG (flush first), never by the screen. **Method:** pre-flight covers state assumptions, not just syntax — every "run X then Y" order names the game state it presumes. **Salvage:** when an operator mis-step burns owner time, look for what the detour measured for free before writing it off — this one bought a control the leg design had not thought to stage. |

## 4 · The chain template (assemble from these parts)

0. **Author the chain WITH the owner — and size decides who assigns the
   models (owner rule, 2026-08-03):**
   - **5 prompts or fewer:** the owner decides the model placement themselves
     if comfortable doing so.
   - **6 prompts or more:** any agent scoping the effort should RECOMMEND
     that the chain setup — the decomposition AND the per-prompt model
     placement — be done by a top-tier (Fable) session, unless the owner
     overrides.
   This codifies how the proven chain was actually made (owner + Fable
   collaboration, 2026-08-01; the placement was Fable's call, which the
   owner could sanity-check but not derive). The assignment is a judgment
   about *where errors compound versus where they get caught* — a read on
   the work's internal risk structure that grows superlinearly with chain
   length: at 5 prompts the owner can hold the risk map; at 18 nobody but
   the authoring session can. The division of labor in §2.10 is a design
   input, not an afterthought. Budget
   the scarce tier at roughly 15–20% of prompts, placed at the compounding
   points; if the plan needs more than ~half the chain on the top tier, the
   decomposition is wrong (the specs are not carrying enough of the load).
   **Owner rule for UNATTENDED work (2026-08-04), the floor on chain size:**
   even a single truly unattended item is a minimum chain of two — the
   volume tier executes, the top tier audits adversarially against the
   archived logs. Batches of unattended items are a full chain, volume tier
   throughout (top tier mid-chain only where a step is genuinely
   complicated), always closed by a terminal top-tier audit. Precedent for
   the shape: the corun-rig close — execution upstream, adversarial audit
   terminal, every "done" treated as a claim.
1. **A folder** (`docs/agent/prompts/<effort>/`), a **README manifest** (table:
   number · file · model · owner-needed? · what it drains; strike rows on
   consumption), and **binding chain rules** in the README: inbox/outbox,
   route-don't-drop (unsure → STOP AND ASK), self-split, defect filing,
   drift-evidence capture, WORKFLOW elements 1–7, commit convention, any
   sealed documents.
2. **Prompt bodies**, each with: staleness check first (`git log` + `git
   pull`); the job; a **scope fence** (in/out); **stop conditions**; **"what
   may not be claimed"** (the honesty rail — the single best guard against
   success-theater); live todo requirement; self-deletion instruction; a
   `## Notes from upstream` section others append into.
3. **Decision points**: anything that is genuinely the owner's is packaged
   with a recommendation and ROUTED (to a decisions surface the owner
   actually reads — see `DOC_STRUCTURE_REVIEW.md` R10), optionally with
   provisional go-ahead ("build, not locked, QA reviews").
4. **Ordering**: strict only where work products interfere (the 8b-before-8c
   rule existed because two fixes shared a subsystem and one unrun leg);
   otherwise declare independence explicitly so prompts can run in any order.
5. **The terminal prompt, always**: an adversarial backward QA, fresh
   context, ideally the strongest model — inbox audit, owed-work sweep,
   consistency pass, verification *sampling against primary evidence*, and
   the folder-empty gate. Budget it generously; this run's QA produced new
   primary evidence (the OG bytecode answer) because it had room to chase.
6. **Chain-to-chain handoff and mid-chain escalation (owner rule,
   2026-08-04).** The owner starts every chain by hand, so the terminal
   prompt's owner report ends with the kickoff line for the next queued
   chain (or says none is queued). And when a supposedly unattended item
   escalates to needing eyes or hands, the discovering prompt OFFERS the
   owner an inserted attended co-run prompt right before the terminal
   audit — accept, and the chain ends with a prepped sitting; decline, and
   the item goes to the checklist as a TAKEABLE IN a co-run rider. The
   audit stays the last prompt in both cases.
7. **Optional but proven**: a blind-control document produced by a fresh
   context with the record off-limits, sealed from every prompt except the
   terminal QA. Use when the effort's conclusions would benefit from an
   unanchored second derivation (audits especially). ⛔ **Author the seal
   against the standing rules** (§3, last row): extract sealed STATE.md
   material to a side-file first and use a subject-hiding `git log` form,
   or the mandatory reads will break the seal before the prompt is opened.

## 5 · Worked outlines for the three named uses

**A — Large project effort** (the form this chain already is): phase-0
measurements → spec (re-derived, decisions closed) → build (split by unit) →
leg prompts (attended, predictions first) → records close-out → backward QA.

**B — Audit chain**: sweep prompts over the target corpus (sized ~10 items
each, verdicts with evidence grades) → decision-package prompts (one §4-style
package per contested item, owner-routed) → a blind control run in parallel
under seal → build/remediation batch → verification legs → terminal QA that
examines the blind control against the informed record and adjudicates
divergences on evidence.

**C — Prelaunch chain (the project's actual next large effort — sketch, not
authored):**
0. Gate: playtest campaign items that block release are done (PT-62 remainder
   etc.); doc-structure adoptions decided (R-list) so the chain builds on the
   final layout.
1. **D13 derivation** — the cleaner's target list derived from scratch (its
   entry already forbids inheriting any recorded count); the chain-12 QA's
   installer table and marker feed (`CHAIN_QA_REPORT.md` §1.4–1.5) are its
   starting evidence, not its answer.
2. **D13 build + leg** (uninstall procedure + save-rescue artifact; attended
   verification with predictions).
3. **MOD_DESCRIPTION rebuild** from entries (R11's release gate), including
   the owner's relabel-package decisions (QA report §3) — every claim
   verified against BUGS, none inherited from the frozen draft. **The player
   FAQ compiles in this same step**: `grep -rn "\[FAQ\]" docs/ Code/` collects
   the tagged sources (15 tags / 10 files as of 2026-08-03, three inside the
   frozen draft itself — the grep must include `archive/`), per WORKFLOW's
   `[FAQ]` convention; each tag's claim gets the same verify-against-entries
   treatment as the description, and tags whose behaviour has since changed
   are dropped, not inherited.
4. **Release-gate sweep** — per-site §3a disposition table complete, fpk
   extraction diff, probe sweep, version/latch checks, the public README.
5. **Doc overhaul execution** (the R15/R12/R13 scripted migration, if not
   already done) + public-facing generation.
6. **Terminal backward QA** — full backward check with a launch-blocking
   stop condition; nothing ships if the folder is not empty.

**D — Kill-gated build chain (PROVEN 2026-08-04, the corun-rig chain: 4
prompts, rig built and paying inside one day):** for building on unproven
capability when the owner fears a hasty plan needing days of rework.
Structure: an **inventory prompt** bins every primitive by provenance
(PROVEN / VERIFIED-IN-SRC / UNKNOWN) under a chain rule that nothing may be
planned on a primitive outside the bins → a **walking-skeleton prompt**
executes the smallest end-to-end proof, with per-step predictions and 3×
abort thresholds written down first, and is **allowed to kill the chain** (a
clean abort that records why is the gate *working*; the terminal prompt
carries a pre-written reduced form — post-mortem into this document, route
the respec/abandon decision, empty the folder — so a kill has somewhere to
land before the outcome is known) → the **payload prompt** builds only on
what the skeleton proved, authoring re-runs from each run's own gaps inside
one sitting → the **terminal QA** audits verdict-by-verdict against the
archived logs, re-derives the economics from actuals, and integrates.
Lessons this run banked, beyond the shapes above:
- **PASS WITH CORRECTIONS is a verdict class.** The skeleton corrected the
  spec §-by-§ (strike-and-supersede, 11 corrections across two runs) instead
  of either failing the gate or silently absorbing the drift.
- **Prediction-vs-actual tables with abort thresholds** turn "the effort
  model was pessimistic" into a measured finding (5–8 min predicted, 80 s
  actual) instead of a vibe — and give a kill objective trip-wires.
- **A declined grant with the alternative timed is a control, not an
  anecdote.** Prompt 3 declined a one-time rule override and measured what it
  would have bought (0.4 s); the terminal audit then adjudicated the rule
  from a number, not an argument. Hand a mid-chain grant back as a
  measurement when you can.
- **The owner can inject decisions mid-chain through the outbox mechanism**
  without breaking self-consumption — three landed here (the probe-gate
  decision plus its recheck order, the override grant, the run-3 insistence
  on sampling the corner), and the last one caught the chain's worst error.
- **Consumed files must name their git grave.** The spec was the only place
  the rig was described; integration dissolves it into standing docs and the
  close-out cites `git show <sha>:<path>` for the full text, so deletion
  costs nothing.

## 6 · The two sentences to keep if everything else is lost

**Structure work so that finishing is the only way a prompt can disappear,
and route every discovery to a written owner instead of a memory.** And:
**end every chain with a fresh-context adversary whose job is to disbelieve
the chain — the run that produced this document was that adversary, and the
method survived it.**

*Cross-references: `CHAIN_QA_REPORT.md` (the verification this playbook rests
on), `DOC_STRUCTURE_REVIEW.md` (the drift taxonomy and the doc-side
mechanisms), `agent/WORKFLOW.md` (per-prompt authoring elements).*
