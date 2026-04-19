# 🧩 LCEL Runnable Comparison Table

| Runnable Type | Core Purpose | Best Use-Case | Real-World "Aha!" Moment |
| :--- | :--- | :--- | :--- |
| **`RunnablePassthrough`** | **Preserve Input** | **RAG / Search** | When you need to keep the user's question alive while you go search for context in a database. |
| **`RunnableLambda`** | **Custom Logic** | **Parsing / Formatting** | When the LLM gives you a messy string and you need to use Python's `re` or `json` to turn it into a number/list. |
| **`RunnableParallel`** | **Concurrent Tasks** | **Classification / Agents** | When you want to check a message for *Sentiment*, *Topic*, and *Safety* at the exact same time without waiting. |

---

### 🏁 Quick Summary Cheat Sheet

*   **Passthrough**: "Keep it moving." (Use when you want to bypass a step).
*   **Lambda**: "Do custom stuff." (Use when LangChain's built-in tools aren't enough).
*   **Parallel**: "Do many things." (Use when you have more than one output goal).

### 🛠 How to Combine Them
```python
chain = {
    "context": search_db,        # Fetch data
    "question": RunnablePassthrough() # Keep original question
} | prompt | model | RunnableLambda(parse_response)
```
**Flow**: Input → (Branch into Parallel/Passthrough) → Recombine in Prompt → LLM → Lambda Clean-up → Final Result.
