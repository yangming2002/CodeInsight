# CodeInsight Architecture v1.0

## 1. Project Definition

CodeInsight is an AI-native Code Intelligence Platform.

It is NOT:
- a coding assistant
- a chatbot
- a Copilot alternative

It IS:
- a Code Understanding System
- a Code Risk Analysis Engine
- a Repository Intelligence Platform

Primary Capability v1:
→ Pull Request Code Review System

---

## 2. System Overview

CodeInsight is composed of 6 core layers:

GitHub / GitLab
↓
Ingestion Layer (Webhook + Diff Fetcher)
↓
Code Understanding Layer (Parser + AST + Symbol)
↓
Context Engine (Retrieval + Graph + Embedding)
↓
Reasoning Layer (Multi-Agent or Single Brain)
↓
Policy Layer (Rule Engine)
↓
Output Layer (PR Comment / Report / API)


---

## 3. Core Modules

### 3.1 Ingestion Layer

Responsibilities:
- GitHub PR webhook
- diff fetching
- commit tracking

Output:
- structured diff object

---

### 3.2 Code Understanding Layer

Goal:
Convert raw code into semantic structure.

Components:
- tree-sitter parser
- symbol extractor
- function/class indexer
- call graph builder

Output:
- semantic code graph

---

### 3.3 Context Engine

This replaces traditional RAG.

It includes:

- vector retrieval
- symbol-based retrieval
- AST-based retrieval
- dependency traversal
- file proximity ranking

Key principle:
> Context quality > model size

---

### 3.4 Reasoning Layer

v1:
- Single Brain Reviewer

v2:
- Multi-Agent System:
  - Bug Agent
  - Security Agent
  - Architecture Agent
  - Performance Agent

---

### 3.5 Policy Layer (Critical)

Rules are deterministic constraints:

Examples:
- no SQL injection patterns
- no unsafe eval usage
- API must remain backward compatible
- no circular dependency allowed

Rule engine is evaluated BEFORE LLM reasoning.

---

### 3.6 Output Layer

Outputs:
- GitHub PR comment
- structured JSON report
- markdown report
- CI status check

---

## 4. Data Flow (Critical Path)

1. PR event triggered
2. diff fetched
3. code parsed into AST
4. context retrieved (hybrid engine)
5. reasoning executed
6. rule engine validation
7. final report generated
8. GitHub comment posted

---

## 5. Key Design Principles

### 5.1 Context First Principle
Model is secondary. Context determines quality.

### 5.2 Deterministic First Principle
Rules > LLM reasoning

### 5.3 Structured Output Principle
All outputs must be machine-readable first, human-readable second.

---

## 6. Why Not Use Existing Tools (Continue / Copilot)

Existing tools focus on:
- code completion
- IDE assistance

CodeInsight focuses on:
- system-level code understanding
- risk detection
- structural reasoning

---

## 7. Future Extensions

- Test generation engine
- Refactoring advisor
- Dependency risk analysis
- Architecture evolution tracking