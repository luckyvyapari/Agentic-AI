from langchain_core.runnables import RunnableLambda
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3.2")

print("--- 🔧 LAB 02: RunnableLambda ---")

def clean_and_count_words(text):
    clean_text = text.strip().replace(".", "").replace(",", "")
    words = clean_text.split()
    return {
        "original_text": text,
        "clean_text": clean_text,
        "word_count": len(words)
    }

lambda_runnable = RunnableLambda(clean_and_count_words)

chain = model | lambda_runnable

print("Asking LLM to write a sentence and then counting words...")
result = chain.invoke("Write exactly 4 words about cats. No extra words.")

print("\n--- Result ---")
print(f"Original: {result['original_text']}")
print(f"Cleaned: {result['clean_text']}")
print(f"Word Count: {result['word_count']}")





print(f"LLM Result analyzed by Lambda: {result} words found.")


# User Input
#    ↓
# LLM (Ollama)
#    ↓
# RunnableLambda (your function)
#    ↓
# Final Output
