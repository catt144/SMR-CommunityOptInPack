# Build an opt-in module that shows each service building's interests

**Authored 2026-09-28** by a fix-pack seat, at this repo's `378bd39`. One-off: `git rm` this file
and its row in `docs/agent/prompts/README.md` in the commit that lands its result.

```sh
git log --oneline -5 && git status --short && python tools/doccheck.py | tail -1
```

Reasoning need: high. It touches UI paths nobody here has traced (no engine fact covers the
build-menu rollover or the building infopanel), and the hook choice decides whether this stays a
wrap or becomes a template replacement.

## Authority — settled

⚖️ **Owner, 2026-09-28:** *"can you actually author a brief in the opt in mod, to create a new
interest tags opt in. That would add this info in the construction panel when you hover of the
building and add a ui panel that has a interest / tags section for the build UI when its already
out?"*

This is the owner ruling that `CLAUDE.md`'s header asks for before a module's behaviour exists;
copy it verbatim into the module's design record. It asks for two surfaces and nothing more:

1. **Build-menu hover:** the rollover shown when hovering a service building in the construction
   menu (today: description, "Service <category>", capacity, "Effect at 100% Performance", …)
   also lists the building's interests.
2. **Placed building:** selecting a built service building shows an interests / tags section in
   its infopanel (today its "Visitors" section shows "Servicing", "Overall Performance" and
   "Service effect").

The module follows FIX_POLICY §5: an `Opt_*` module, off by default, one Mod Options toggle. With
the toggle off, the UI must be vanilla.

## Why the owner wants it

Relaunched shows a service building's *category* ("Stores", "Parks") and hides its *interests*.
The interests still drive play on 1.1.1: colonists look up a building for their daily interest by
interest label, and the Gamer and Extrovert traits pay +10 Sanity on entering any working building
whose interests include Gaming or Social. Players cannot see that an Electronics Store counts for
Gamers. The fix-pack seat checked this against 1.1.1 source on 2026-09-28; the citations below are
leads, so re-derive each line number with `grep -n` before relying on it.

## Evidence (source: `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\<build>\Src\Lua`)

**The data, 1.1.1.405907:**
- `interest1`…`interest11` are template properties on `ServiceBase` (`ServiceBase.lua:26-36`).
  `ServiceBase:IsOneOfInterests` checks all eleven (`:216-229`).
- `Service:SetCustomLabels` files the building under one label per interest (`Buildings/Service.lua:170-230`).
  `Dome:GetService` finds services by `dome.labels[need]` (`Buildings/Dome.lua:3622-3640`).
- The Gamer and Extrovert bonuses are in `Colonist:VisitService` (`Units/Colonist.lua:2671-2678`).
- **`ServiceBase:GetServiceList()` still ships and nothing displays it** (`ServiceBase.lua:166-212`).
  It returns a `TList` of localized interest names and skips needs a law auto-satisfies
  (`g_AutoSatisfiedNeeds`). `MedicalBuilding` overrides it (`Buildings/MedicalCenter.lua:21`) and
  `IsOneOfInterests` (`:29-33`) to add Relaxation while rejuvenation runs. Grep
  `ServiceList` across 1.1.1 `Lua` and `Data`: no other callers.
- Localized display names: the `Interests` table (`Interests.lua:17-58`, `GetInterestDisplayName`).
- Checked 2026-09-28: no code writes the interest fields at runtime except
  `ResourceStockpile.lua:302` (`needFood`).

**The UI, 1.1.1.405907:**
- `Service:GetServiceDescription(texts, label_separator, dont_modify)` (`Buildings/Service.lua:123-165`)
  builds the "Service <category>" / capacity / "Effect at 100% Performance" block. It reads
  `GetModifierObject(self)` when `self` is not a valid object, so it also serves class or template
  calls. Its callers are `Service:GetIPDescription` (`:167`) and `FoodServiceBuilding:GetIPDescription`
  (`Buildings/FoodServiceBuilding.lua:924-928`). The build-menu hover shows the same lines, but
  **nobody has traced which function feeds it.**
- The "Visitors" infopanel section is the generated XDef class `sectionVisitors`
  (`XDef/sectionVisitors.generated.lua`, 51 lines; `Init` at `:20`, "Servicing" `:23`,
  "Service effect" `:40`). Its container is `XDef/ipBuilding.generated.lua`.

**The precedent, 1.0.7.396349 — the game used to show this:**
- `Service:GetIPDescription` appended `T{376972917568, "Services: <em><list></em>", list = GetServiceList()}`
  (`Buildings/Service.lua:58-62`, again at `:190-194` for `ServiceWorkplace`).
- `sectionVisitors` ended with `InfopanelText` `T(114391732659, "Needs serviced: <ServiceList>")` (`:44`).
- Neither string id is in the 1.1.1 or 1.1.0 Src tree (grep, 2026-09-28). Whether the game's shipped
  language tables still carry them is unchecked.

## End state

- A new `Opt_*` module on `main`, registered like its siblings (`items.lua` toggle, `metadata.lua`
  `default_options` and code list), with the header §5 requires.
- A design record in `docs/agent/bugs/` with the next free D id (check filenames and the archive),
  carrying the owner ruling above.
- A desk check that shows both surfaces render the interests with the toggle on and the vanilla
  text with it off, for at least the Electronics Store, Casino Complex, a medical building and a
  food service.
- The in-game look proposed where this repo's `CLAUDE.md` routes playtest runs. Proposing a sitting
  needs the owner's approval; don't hold one yourself.

## Judgement handed to you

Which hook for each surface; whether to reuse `GetServiceList` (it respects the medical override);
whether needs such as Food and Medical appear; the label wording and localization (restored ids or
new ones); ordering and layout; which service classes are covered. Record your calls in the commit
message and the design record. Use the todo tool before any write: one item per commit-and-verify
unit, one in progress.

## Scope

- **In:** the module, its registration, its design record, its desk check, and a
  `FUTURE_IDEAS.md` line if you judge one worth adding.
- **Out:** any change to how interests behave; the fix pack; non-service buildings. Also out:
  showing which traits benefit (Gamer → Gaming, Extrovert → Social). Report it as a follow-up idea;
  don't build it.

## Stops — report instead of building

1. The build-menu hover does not pass through a Lua function you can wrap (it is engine-side, or
   reachable only by replacing a whole vanilla XTemplate). Report the options with their risk under
   FIX_POLICY §0 and §1.
2. The infopanel section can only be added by replacing `sectionVisitors` or `ipBuilding` whole,
   not by inserting into it. Same report.
3. A peer has uncommitted work on `items.lua`, `metadata.lua` or the same module name.

## Claim limits

"Renders in the desk check" is supported. "Shows in game" is not, until the owner has looked.

## References

`CLAUDE.md` (the two bans, the ruling duty) · `docs/agent/FIX_POLICY.md` §0, §1, §2, §3a, §5 and §8
(both-configuration run with the fix pack present and absent) · `docs/agent/WORKFLOW.md` ·
skills `doc-editing`, `smr-bug-library`. If run unattended, a different owner-selected model audits
the result before it enters the record.
