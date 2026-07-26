import ollama  # Uses the actual Ollama service running on your Mac

# Stream the real output directly from Ollama
response = ollama.chat(
    model="hf.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M",
    messages=[
        {
            "role": "user",
            "content": "tell me a story about a brave knight and a dragon",
        },
    ],
    stream=True,
)

print("--- Output from Ollama (M1 GPU) ---\n")
for chunk in response:
    print(chunk["message"]["content"], end="", flush=True)
print("\n")