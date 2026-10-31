# Research agent libraries

Project status and numbered research folders are listed in the [research index](../docs/research/README.md).

These libraries support this website's research and development work. They are
source guidance, not article evidence, automatically installed plugins, or
executed research reviewers. Both `agents/` and `docs/` are excluded from the
website build.

| Library | Available material | Recorded revision |
| --- | --- | --- |
| **agent-skills** | Complete local snapshot in `agent-skills/`, including its license, workflows, personas and reference files | [`agent-skills.lock.json`](agent-skills.lock.json): `f63ec56a3cc936408d792956ae583c3c96a825bd` |
| **QuantSmith** | Reference to a separate local checkout; no SDK source is copied here | [`quantsmith.reference.json`](quantsmith.reference.json): `5deea85438f6d46a8a14ddb85e3821a65fa62f4e`, with 61 selected guidance-file hashes |

## Applying the guidance

Start with agent-skills' [discovery skill](agent-skills/skills/using-agent-skills/SKILL.md)
and select only the workflows relevant to the work. For the paused AI-hype literature draft,
context and documentation guidance help organize section evidence; engineering
review patterns can inform bounded assistant checks. Its repository-wide
`AGENTS.md` governs changes inside that library, not this website as a whole.

For QuantSmith, inspect the relevant role and standards at the recorded version.
The research orientation covered `agents/research_analyst/`,
`agents/role_operations/prior_art_scanner/`, `agents/backtest_review/`, and
source, hypothesis, confidence and storytelling guidance. These additional
research roles are not all included in the reference's 61-file hash inventory;
review their committed contents separately before adopting them.

QuantSmith's `agents/research-reporter/README.md` describes a proposed family,
scoped but not implemented at the reviewed revision. Reading its design does
not execute its proposed source verifier, calculation verifier, writer or other
reviewers. A governed research catalog is not configured in this website project.

The [research source notes](../docs/research/001_AIHype/source-notes.md#library-familiarity-refresh-for-the-literature-draft)
record inspected versions, scope and limits. The [article review record](../docs/research/001_AIHype/article-draft-review.md)
distinguishes actual assistant passes from primary-source and independent human
verification. Neither library closes the article's evidence gates by itself.

## QuantSmith location and pin boundary

The reference JSON retains the supplied machine-specific `default_path` and
legacy `path_env` name. They are configuration metadata; this project has no
implemented resolver or `scripts/verify_quantsmith.py` command. On another
machine, choose an existing QuantSmith checkout and read the reference's revision
and file hashes explicitly. Do not assume the default location exists.

The external working checkout can advance independently. At commit preparation,
its HEAD was `7f3a0b6f13300024b9e5bc2760806c81796d8ed9`, ahead of the recorded
reference, and its current README no longer matched that pin. This is not a
verified current-working-tree reference. Keep the historical pin: inspect the
pinned committed contents without switching or resetting another active checkout.
A read-only example, with your own local path, is:

```sh
quant_checkout="/path/to/local/QuantSmith"
git -C "$quant_checkout" show 5deea85438f6d46a8a14ddb85e3821a65fa62f4e:agents/research_analyst/instructions.md
```

Before using a reference, compare its revision/tree and selected-file SHA-256
values with committed contents. Before using current working files, check those
bytes separately; a historical pin does not validate later changes. Missing local
objects or changed guidance should be reported, not silently replaced with a
floating remote branch. Fetching, installation, hooks and runtime adoption remain
separate work.

## Offline snapshot checks

The following validators use local files and built-in Node modules:

```sh
node agents/agent-skills/scripts/validate-skills.js
node agents/agent-skills/scripts/validate-commands.js
node agents/agent-skills/scripts/validate-artifact-paths.js
node agents/agent-skills/scripts/validate-reference-links.js
```

Do not run the evaluation runner as a routine metadata check. The vendored
`validate-versions.js` also consults the current Git repository, so running it
unchanged here would use this website's tags rather than the original snapshot's
version history. Keep the snapshot and lock together; deliberate upgrades need
new provenance and content review. No automatic update or install is configured.

The immutable snapshot preserves upstream whitespace as well as source bytes.
Its existing whitespace warnings are not reformatted during adoption, because
doing so would invalidate the recorded snapshot. Check project-authored changes
separately from the pinned upstream content.
