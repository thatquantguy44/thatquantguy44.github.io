# Personal coding case-study protocol

Protocol version: 0.1.0

Prepared: 2026-10-29 (America/New_York)

Parents: [access decision](coding-study-decision.md), [research brief](ai-hype-research-brief.md), [claim AIH-C05](evidence-matrix.md#aih-c05--our-coding-experiment-is-not-yet-an-observation).

**Scope: one confirmed developer (`P01`), exploratory personal case study.** No observations exist. Independent reviewer access is unconfirmed; the planned assessment is automated checks plus author assessment. Offline-only remains in effect. This document prepares the study and does not bind a model or start AI calls.

## Question and planning size

In this developer's selected maintenance tasks, how does AI access relate to accepted completion, observed author effort, correction, and defects under frozen checks? Explain mechanisms and failures alongside timings. Do not claim population-level productivity effects, independent quality equivalence, or reviewer-time savings.

The user selected **four pairs (eight distinct tasks)**, with pairs 1–2 before pairs 3–4, using an isolated committed QuantSmith SDK copy. A **60-minute active-author-work cap per task** remains a proposal, not a bound execution setting, power calculation, or observed workload. Bind actual session availability, per-task active cap, wall-time cap, and fixed correction/defect follow-up window before assignment. If the selected workload proves infeasible before collection, document a versioned scope change before randomization rather than dropping tasks after outcomes.

## Tasks and assignment

1. Use the selected QuantSmith SDK commit `2601cabd74622c832e99457a9a84ddb4a11f073c`, excluding working changes, and bind the environment. The selected tasks are bounded maintenance/extensions, not reproduced bug tickets. Pair by expected scope, difficulty, and familiarity before knowing condition assignments; equal effort remains an unmeasured judgment.
2. Use distinct tasks and underlying cases. Do not ask the developer to solve the same issue twice. Avoid pairs where the first solution directly supplies the second; record any shared-case relationship and prior solution exposure.
3. Freeze task instructions, acceptance checks, task IDs, pairing, and the full task-pool hash before randomization. Do not replace inconvenient tasks after assignment. The participant/curator overlap and familiarity must be disclosed; this is not a blinded task-naivety study.
4. Generate and retain a random seed after the task pool is frozen and the session is ready. Within each pair, randomize one task to `ai_enabled` and the other to `no_ai`. Respect the selected stages: P1/P2 before P3/P4; randomize pair order only within each stage and balance which condition comes first where feasible. This is restricted order, not unrestricted pair randomization. Archive the schedule, seed, algorithm, and restriction. Stage 2 inclusion is not conditional on stage 1 performance.
5. Start each task in a clean worktree/copy from the frozen base. Do not transfer a previous task's AI output or patch into a control attempt. Record learning, fatigue, interruptions, and deviations; a reset cannot erase human learning.

The versioned [task bank](experiments/coding-study/task-bank.json) and its file-hash lock identify the prepared source, all eight briefs/checks, and stage restriction. This is not a frozen execution session: model/tools, timings/caps, familiarity inventory, and practical measurement remain unbound. No schedule or condition assignment is generated. Warm-up uses separate unscored tasks, with the same preparation rules across conditions; record warm-up/setup effort separately.

The [repository/task record](coding-task-recommendations.md) documents the accepted scope. Public acceptance tests define desired behavior and examples; they are available equally in both conditions and contain no implementation patch/reference solution. Only the current task's brief/check is exported. The author has already seen task themes/source structure; do not claim task naivety or independent human review.

## Conditions and controls

| Condition | Allowed work |
| --- | --- |
| `no_ai` | Frozen editor, terminal, repository, tests, and allowed documentation; AI completion/chat/agents disabled |
| `ai_enabled` | The same environment and material, plus one frozen AI tool/model configuration; retain tool usage, prompts/responses where permissible, failures, and known/unknown costs |

Specify the exact editor/extensions, repository/docs snapshots, AI model/tool identity, permitted assistance, output artifacts, and caps before running. Keep source material and non-AI tools comparable. Any later change is a versioned deviation, not an invisible fix. Web access is currently disabled; remote AI execution remains outside the current offline work. Even local AI execution requires the study configuration to be bound first.

## Measurement and acceptance

Record nonoverlapping author-active intervals as implementation/debugging, author verification, or correction/rework. Capture AI interaction as active effort when the developer is reading, prompting, or checking output. Time simply waiting for a model is not automatically active labor; if useful work happens during a wait, count it once in its active category and document the overlap.

Record model waiting, other waiting, interruptions, and calendar time separately. Logs must distinguish observed zeros from missing values. Do not fill unknown usage/cost/review time with zero. Reviewer effort stays null while external review is unobserved/not performed. Author verification belongs to author effort, not independent reviewer effort.

Freeze the definition of acceptance per task before assignment. Record both automated check results and author assessment with supporting artifact references. An `accepted` status means these specified checks pass; it does not certify independent quality. If an independent reviewer becomes available, define identity separation, practical blinding, and common review coverage before collection. Selective later review must be labeled separately.

Retain every scheduled task, including not-started, timeout, abandoned, rejected, and protocol-deviating attempts. Record partial work and consumed effort. At the bound cap, stop and label timeout; the cap is not time to accepted completion. Freeze any permitted correction phase and follow-up rules before assignment. Corrections found within the declared window remain attributed to the original task; disclose findings outside the window separately.

## Analysis and claim limits

- Show every task's condition, pair/order, familiarity, terminal state, acceptance checks, observed effort components, waiting, deviations, and follow-up findings.
- Report acceptance counts over all scheduled tasks by condition, including not-started/missing cases explicitly. Do not treat missing effort as zero or an unstarted task as a fast failure.
- Report accumulated observed author effort including failed attempts. Report author effort per accepted task only with complete required timing; it is undefined if no tasks are accepted and incomplete when required effort is missing. This is not total team delivery cost while external-review effort is unmeasured.
- If presenting times for accepted tasks or pair differences, label the subset and display noncompletion alongside it. Task differences and order/carryover effects limit interpretation even with randomized assignment.
- Use raw task-level displays and descriptive summaries. This initial case-study plan specifies no population confidence interval, significance test, or confirmatory effect estimate. Additional tasks remain observations from one developer, not new developers.

Allowed article wording after actual observations: “In my selected tasks using this configuration, I observed …; acceptance used automated checks and my assessment.” Until collection, describe only the proposed method. The [literature verification gates](source-notes.md#verification-backlog) remain separate.

## Freeze and execution checklist

- [x] Confirm participant count and choose the personal exploratory route.
- [x] Prepare scope/assignment/measurement rules and blank records.
- [x] Select the pinned repository, all eight task definitions, acceptance contracts, and stage order; prepare clean-copy/export/preflight tooling.
- [ ] Bind actual time slots and task/follow-up caps; resolve practical matching/familiarity concerns before assignment.
- [ ] Verify timing can be captured without double counting; label author-assessed acceptance and actual reviewer status.
- [ ] Bind comparable tools/docs and the AI configuration, logging, privacy boundaries, and actual execution availability.
- [ ] Freeze task-pool hash, randomization, schedule, and [session manifest](experiments/coding-study/session.example.json) before starting tasks.
- [ ] Collect all assignments and failures; retain source records and report missingness/deviations.

Templates and recording instructions: [coding-study package](experiments/coding-study/README.md). No data collection or recruitment occurred in preparing this protocol.
