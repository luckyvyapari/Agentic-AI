import time
import logging
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_ollama import OllamaLLM

# ---------------- LOGGING SETUP ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

model = OllamaLLM(model="llama3.2")

print("--- ⚡ LAB 03: RunnableParallel with Timing ---")

# ---------------- PROMPTS ----------------
def funny_prompt(x):
    logging.info("➡️ Funny check STARTED")
    return f"Rate this joke from 0 to 10 (only number):\n{x}"

def harmful_prompt(x):
    logging.info("➡️ Safety check STARTED")
    return f"Is this joke harmful? Answer YES or NO:\n{x}"

# ---------------- POST PROCESS ----------------
def funny_post(x):
    logging.info("✅ Funny check FINISHED")
    return "😂 Funny Score: " + x

def harmful_post(x):
    logging.info("✅ Safety check FINISHED")
    return "🛡️ Safety: " + x

# ---------------- PARALLEL RUN ----------------
joke_tester = RunnableParallel({
    "funny_score": RunnableLambda(funny_prompt) | model | RunnableLambda(funny_post),
    "harmful_check": RunnableLambda(harmful_prompt) | model | RunnableLambda(harmful_post)
})

# ---------------- TIMING ----------------
start_time = time.time()

logging.info("🚀 Parallel execution START")

results = joke_tester.invoke(
    "Why did the chicken cross the road? To get to the other side!"
)

end_time = time.time()
total_time = end_time - start_time

logging.info("🏁 Parallel execution FINISHED")

# ---------------- OUTPUT ----------------
print("\n--- Results ---")
print(results["funny_score"])
print(results["harmful_check"])

print(f"\n⏱️ Total Execution Time: {total_time:.2f} seconds")