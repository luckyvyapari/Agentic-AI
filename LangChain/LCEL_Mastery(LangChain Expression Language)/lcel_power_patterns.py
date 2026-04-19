from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Setup local model
model = OllamaLLM(model="llama3.2")

# --- SCENARIO 1: RunnablePassthrough (The RAG Pattern) ---
# Goal: Send a question to two places: a simulated "Search" and the final "Prompt"
def mock_database_search(query):
    # Simulated database retrieval
    return f"Context found for '{query}': The sky is blue because of Rayleigh scattering."

rag_chain = {
    "context": RunnableLambda(mock_database_search), # Retrieve facts
    "question": RunnablePassthrough()                # Keep original question
} | ChatPromptTemplate.from_template("Use this context: {context}\n\nAnswer: {question}") | model

print("--- 🔍 RAG PATTERN (Passthrough) ---")
print(rag_chain.invoke("Why is the sky blue?"))


# --- SCENARIO 2: RunnableParallel (The Multi-Task Pattern) ---
# Goal: Analyze a review for Sentiment and Language simultaneously
analyze_chain = RunnableParallel({
    "sentiment": ChatPromptTemplate.from_template("Is this positive or negative: {text}") | model,
    "language": ChatPromptTemplate.from_template("What language is this: {text}") | model,
    "original": RunnablePassthrough()
})

print("\n--- ⚡ MULTI-TASK PATTERN (Parallel) ---")
print(analyze_chain.invoke("I love this product, it works perfectly!"))


# --- SCENARIO 3: RunnableLambda (The Formatting Pattern) ---
# Goal: Transform LLM output. LLM thinks in sentences, but we want a Python number.
def extract_number(text):
    # Simple logic to find a digit in the text
    import re
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0

math_chain = (
    ChatPromptTemplate.from_template("How many letters are in the word {word}?") 
    | model 
    | RunnableLambda(extract_number) # Convert "There are 5 letters" into just 5
)

print("\n--- 🧹 FORMATTING PATTERN (Lambda) ---")
count = math_chain.invoke("Python")
print(f"Result is a Python {type(count)}: {count}")
