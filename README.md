# CodeInsight - 30 Day Vibe Coding Plan

Goal:
Build a production-ready Code Intelligence Platform starting from zero.

Primary Feature:
GitHub PR Code Review System

---

# Week 1 - Foundation (Core System)

## Day 1
- Initialize repo structure
- Setup FastAPI backend
- Setup basic project modules

## Day 2
- Implement GitHub webhook receiver
- Parse PR events

## Day 3
- Implement diff fetcher
- Normalize diff format

## Day 4
- Build basic repository parser
- Extract file structure

## Day 5
- Integrate tree-sitter (basic AST parsing)

## Day 6
- Build symbol extraction system

## Day 7
- End-to-end pipeline v0:
  PR → diff → simple review → output

---

# Week 2 - Context Engine

## Day 8
- Implement embedding-based retrieval

## Day 9
- Add symbol-based retrieval

## Day 10
- Build AST-based context extraction

## Day 11
- Add hybrid ranking system

## Day 12
- Build context builder module

## Day 13
- Improve retrieval accuracy

## Day 14
- Context Engine v1 complete

---

# Week 3 - Reasoning Layer

## Day 15
- Build single brain reviewer

## Day 16
- Add bug detection module

## Day 17
- Add security analysis module

## Day 18
- Add architecture analysis module

## Day 19
- Add performance analysis module

## Day 20
- Merge reasoning outputs

## Day 21
- Structured review report system

---

# Week 4 - Productization

## Day 22
- Build rule engine (YAML-based)

## Day 23
- Add policy validation before LLM

## Day 24
- GitHub PR comment integration

## Day 25
- Add structured JSON output API

## Day 26
- Build basic dashboard (optional)

## Day 27
- Add evaluation dataset

## Day 28
- Improve hallucination control

## Day 29
- Optimize latency and caching

## Day 30
- Release v1.0 MVP

---

# Final Output

A system that can:
- automatically review PRs
- detect bugs and security issues
- enforce engineering rules
- generate structured reports
- integrate into GitHub workflow