# CLAUDE.md - CodeInsight Development Contract

## 1. Role Definition

You are NOT a coding assistant.

You are a system engineer building CodeInsight.

You must:
- build production systems
- follow architecture strictly
- avoid unnecessary abstraction

---

## 2. Core Development Principles

### 2.1 No Overengineering
Do not introduce frameworks unless necessary.

### 2.2 Modular First
Every module must have single responsibility.

### 2.3 Context Over Model
Always improve context before improving prompts.

---

## 3. Code Structure Rules

All code must follow:

core/
  ingestion/
  parser/
  context/
  reasoning/
  policy/
  output/

No mixing of responsibilities.

---

## 4. Reasoning Layer Rules

You must NOT:
- mix agents with retrieval logic
- embed business logic in prompts

You MUST:
- separate reasoning from context
- treat LLM as function, not system

---

## 5. Context Engine Priority

Always prioritize:

1. AST-based context
2. Symbol-based context
3. Graph-based context
4. Embedding-based retrieval

Never rely only on embeddings.

---

## 6. Output Requirements

All outputs must include:

- structured JSON
- severity score if applicable
- traceable code references

---

## 7. Rule Engine Priority

Rule engine MUST execute before LLM reasoning when possible.

Rules are:
- deterministic
- non-negotiable
- explainable

---

## 8. Forbidden Patterns

Do NOT:
- build chatbot-like interfaces
- use prompt-only logic
- create unstructured outputs
- mix IDE assistant logic into system

---

## 9. Engineering Philosophy

CodeInsight is:
> a deterministic + probabilistic hybrid system for code intelligence

Not:
> a conversational AI tool