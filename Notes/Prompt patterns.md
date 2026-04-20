# Prompt Patterns: Few-shot, Chain-of-Thought (CoT), ReAct

---

## 1. Few-shot Prompting

Provide examples (input → output) so the model learns the pattern.

### Structure
```text
Input: Example 1
Output: Example 1 result

Input: Example 2
Output: Example 2 result

Input: New query
Output:
```

### Use Cases
- Pattern learning
- Formatting tasks
- Classification problems

---

## 2. Chain-of-Thought (CoT)

Encourages step-by-step reasoning.

### Structure
```text
Question: ...
Think step by step.
Answer:
```

### Example
```text
Q: If a train travels 60 km in 1 hour, how far in 3 hours?
A: Step-by-step: 60 × 3 = 180 km
```

### Use Cases
- Mathematical problems
- Logical reasoning
- Multi-step problem solving

---

## 3. ReAct (Reason + Act)

Combines reasoning with actions like tool usage or retrieval.

### Structure
```text
Question: ...
Thought: reasoning
Action: tool call
Observation: result
Thought: updated reasoning
Answer: final answer
```

### Use Cases
- AI agents
- Tool integration
- Dynamic decision-making

---

## Key Differences

| Pattern  | Purpose                          |
|----------|----------------------------------|
| Few-shot | Learns from examples             |
| CoT      | Step-by-step reasoning           |
| ReAct    | Reasoning + interaction/actions  |
