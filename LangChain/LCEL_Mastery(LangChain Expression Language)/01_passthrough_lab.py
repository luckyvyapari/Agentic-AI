from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
import logging

# show logs in console
logging.basicConfig(level=logging.INFO, format="%(message)s")

# load local LLM (llama3.2 via Ollama)
model = OllamaLLM(model="llama3.2")

print("--- 🛣️ RunnablePassthrough ---")

# simple function (acts like DB/tool)
def get_user_age(name):
    logging.info(f"Fetching age for: {name}")
    db = {"Alice": 25, "Bob": 42}
    return db.get(name, "Unknown")

# ❌ WRONG: loses original input ("Alice")
bad_chain = RunnableLambda(get_user_age) | ChatPromptTemplate.from_template(
    "How is life at age {age}?"
)
# Flow: "Alice" → 25 → prompt (name lost)

# ✅ CORRECT: keep input + transform in parallel
chain = {
    "age": RunnableLambda(get_user_age),   # "Alice" → 25
    "name": RunnablePassthrough()          # "Alice" → "Alice" (unchanged)
} | ChatPromptTemplate.from_template(
    "Hey {name}, how is life at age {age}?"
) | model  # send to LLM

# run chain
result = chain.invoke("Alice")

print("\n--- Output ---")
print(result)



# Input ("Alice")

#    ├── OTHER WORK → get_user_age → 25
#    └── PASSTHROUGH → keep "Alice"

# → combine both → {"age":25, "name":"Alice"}


# def main(name):
#     age = get_user_age(name)              # step 1
#     prompt = f"Hey {name}, age {age}"     # step 2
#     response = llm_call(prompt)           # step 3
#     return response


# What RunnablePassthrough() does
# RunnablePassthrough()("Alice") → "Alice"

# 👉 It simply:

# takes input
# returns it unchanged

# No logic, no processing.

# --- 🛣️ LAB 01: RunnablePassthrough ---
# Fetching age for: Alice
# HTTP Request: POST http://127.0.0.1:11434/api/generate "HTTP/1.1 200 OK"

# --- Output ---
# Alice, life at 25 can be quite exciting and overwhelming at the same time! As someone who's navigating their quarter-life, I'd say that this period is all about self-discovery and exploration.

# My advice to you, Alice, would be to focus on finding your passions and interests outside of work or school. Whether it's traveling, learning a new skill, or volunteering, make sure to allocate time for activities that bring you joy and fulfillment.

# Remember, 25 is just the beginning, and your life journey will have its ups and downs. But with an open mind, a willingness to take risks, and a positive attitude, you'll be well on your way to creating a life that truly reflects who you are.