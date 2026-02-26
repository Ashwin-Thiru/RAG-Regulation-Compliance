import requests
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_compliance_answer(question):
    url = "http://127.0.0.1:8000/v1/retrieve"
    data = {"query": question, "k": 3}
    
    try:
        response = requests.post(url, json=data).json()
    except Exception as e:
        return None, f"Error connecting to Pathway: {e}", []
    
    # Extract data for the LLM and for the "Semantic Search" display
    context = "\n\n".join([res['text'] for res in response])
    sources = list(set([res['metadata']['name'] for res in response]))
    semantic_results = response # Keep the full list for the demo display

    # Generate response using Groq
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": "You are a Senior Financial Audit & Compliance Officer. "
                           "Analyze the context and answer clearly. "
                           "Use professional formatting and bold key thresholds."
            },
            {
                "role": "user", 
                "content": f"CONTEXT:\n{context}\n\nUSER QUESTION: {question}"
            }
        ],
        temperature=0.1, 
    )
    
    return semantic_results, completion.choices[0].message.content, sources

def run_demo():
    print("\n" + "="*60)
    print("🏦 PATHWAY + GROQ: REAL-TIME COMPLIANCE AGENT")
    print("="*60)
    print("Welcome, Ashwin. I am connected to your live Google Drive.")
    print("I can monitor regulatory changes in real-time.")
    
    while True:
        print("\n" + "-"*60)
        query = input("🤖 Agent: What can I analyze for you today? (type 'exit' to quit): ")
        
        if query.lower() in ['exit', 'quit']:
            print("Shutting down compliance agent. Goodbye!")
            break

        print(f"\n🔍 [Step 1] Performing Semantic Search on Pathway Vector Store...")
        semantic_data, ai_response, docs = get_compliance_answer(query)

        if not semantic_data:
            print(ai_response)
            continue

        # --- OUTPUT 1: AI Reasoning ---
        print("\n📋 [Step 2] GROQ COMPLIANCE REPORT:")
        print("." * 30)
        print(ai_response)

        # --- OUTPUT 2: Semantic Evidence (The "Top K" display) ---
        print("\n🧠 [Step 3] TOP-K SEMANTIC SEARCH RESULTS (The 'Evidence'):")
        print("." * 30)
        for i, res in enumerate(semantic_data):
            # We show the text and the 'Distance' to prove AI accuracy
            score = round(1 - res['dist'], 4) # Simple similarity score
            print(f"Rank {i+1} | Similarity: {score} | Source: {res['metadata']['name']}")
            print(f"Snippet: {res['text'][:150]}...")
            print("-" * 15)

        # --- OUTPUT 3: Citations ---
        print("\n📚 [Step 4] CITATIONS:")
        for doc in docs:
            print(f"✅ Verified against: {doc}")

if __name__ == "__main__":
    run_demo()