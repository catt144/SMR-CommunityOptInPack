# Reading the live Pages deployment

Use this reference when a task needs to know what the public GitHub Pages site actually
says about this mod. A committed site tree and a deployed site are different states:
`publish-site.yml` in `B:\Dev\SMR\SMR-CommunityMods` is `workflow_dispatch`-only, so a
repository commit is not public until the owner runs the workflow. The fix pack's copy
of this protocol is the same (donor bytes adapted 2026-10-03 for this mod's pages).

## Rails

1. Never run the publish workflow or propose automating it. Publishing is the owner's
   act. Report that a deployment is owed.
2. Never treat editing store strings as a correction to a live store page.
   `metadata.lua` ships inside the mod and only an owner upload changes the live
   listing. Site content in `B:\Dev\SMR\SMR-CommunityMods\content\opt-in\` is ordinary
   editable work, but any edit remains undeployed until the owner publishes it.

## Identify the live commit

Read the public deployments API first:

```text
https://api.github.com/repos/catt144/SMR-CommunityMods/deployments?environment=github-pages&per_page=5
```

A deployment row is not proof of success. For each recent candidate, read its status
endpoint:

```text
https://api.github.com/repos/catt144/SMR-CommunityMods/deployments/<id>/statuses?per_page=3
```

The live sha is the newest deployment whose status is `success`. Do not carry a sha from
`STATE.md`, a report, or an earlier session: recorded shas and statuses are leads, not
readings. In the site repository, this shows what is committed but not live:

```text
git log --oneline <deployed-sha>..HEAD
```

Read required page content from that commit with
`git show <deployed-sha>:content/opt-in/index.md` (and `modules.md`). Then use the public
page (`https://catt144.github.io/SMR-CommunityMods/opt-in/`) as an independent witness.
Agreement between the deployed source and the live page is a control; repeating the same
reader is not.

## Reading traps

- A rendered page is a weak instrument. An issue-page HTML reader once returned zero
  comments three times when three existed. Use the GitHub JSON API and check the list
  endpoint's own counts; if they are non-zero and a reader shows nothing, the reader is
  wrong.
- Re-derive the route, not the citation. A stored deployment sha or portal conclusion
  can be stale or can describe only a first upload. Read the API and the deployed file
  again for the task at hand.
- Never silently discount a discrepancy as caching. Record what each independent source
  returned and when; "probably caching" is an attribution to prove, not a reason to
  discard a mismatch.
- Before this mod's first publication, the Opt-In pages may be committed and not
  deployed by design; that is the expected reading, not a fault.
