---
layout: page
title: "QuantSmith: Reproducible Quant Research"
description: A spec-driven toolkit for turning quantitative research questions into testable, reviewable workflows.
permalink: /projects/quantsmith/
toc: true
---

QuantSmith is a spec-driven SDK and workflow scaffold for quantitative research and model development. It connects research requirements to implementation, validation, and reusable evidence, so a result is easier to inspect and hand off.

> QuantSmith is research-process infrastructure, not a packaged alpha strategy or a claim of investment performance.

## The problem

A model result is difficult to trust when its assumptions, data decisions, validation, and implementation live in disconnected places. Quantitative teams need a way to catch avoidable mistakes, explain how a result was produced, and leave behind artifacts another researcher can review.

QuantSmith is designed around that workflow problem: keep the specification and its evidence close to the code, tests, and research outputs.

## A specification-led workflow

Each feature moves through a defined lifecycle:

1. **Specify** the research question, requirements, assumptions, and acceptance criteria.
2. **Plan** the implementation and identify the evidence needed to verify it.
3. **Implement** the runtime and tests against that plan.
4. **Verify** the result with focused checks and domain-specific quality gates.
5. **Operate** with documented artifacts, limitations, and a clear handoff.

The specification is the source of truth. Design decisions, tasks, tests, and release evidence are intended to trace back to it rather than being left only in conversation or commit history.

## Two ways to adopt it

QuantSmith has two complementary layers:

- **Python package:** runnable reference pipelines and workflow utilities. For example, the daily momentum signal is a deterministic reference pipeline mapped to a specification and tests.
- **Copyable scaffold:** specialist agent contracts, reusable standards, templates, and quality gates that a team can adopt in an existing quant repository.

This split lets a team use the executable examples, the workflow standards, or both. It avoids requiring an entire new platform before the workflow can be tried.

## Making review part of the workflow

The gates cover concerns that materially affect quantitative research, including point-in-time leakage, backtest assumptions, reproducibility, data contracts, and secret handling. They are advisory by default for local exploration and can be made blocking in CI when a team is ready to enforce them.

The orchestration evidence layer adds structured records for prompts and context, assumptions, evaluation, audit events, produced artifacts, and replay. That makes an agent-assisted run more inspectable; it does not make model output correct by itself.

## Scope and limitations

The reference runtimes demonstrate reproducible workflows, not profitable strategies. Teams still need to assess each method against their data, constraints, execution costs, and acceptance criteria. Production data access and model-provider choices remain integration decisions. The text-intelligence foundation is explicitly a draft and does not activate a hosted provider or vector database.

## Explore the project

- [QuantSmith repository](https://github.com/thatquantguy44/QuantSmith)
- [Reference pipeline catalog](https://github.com/thatquantguy44/QuantSmith/tree/main/src/quantsmith/pipelines)
- [Adoption guide](https://github.com/thatquantguy44/QuantSmith/blob/main/docs/adoption_guide.md)
