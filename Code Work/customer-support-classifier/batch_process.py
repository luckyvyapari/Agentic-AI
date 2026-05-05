import pandas as pd
from agent import graph
import os

def run_batch():
    print("🚀 Starting Batch Processing...")
    df = pd.read_csv("tickets.csv")
    results = []
    
    for i, row in df.iterrows():
        print(f"Processing Ticket {row['ticket_id']}...")
        state = {"message": row["message"]}
        output = graph.invoke(state)
        
        results.append({
            "ticket_id": row["ticket_id"],
            "message": row["message"],
            "priority": output["priority"],
            "category": output["category"],
            "status": output["status"],
            "email_draft": output["email_draft"]
        })
        
    results_df = pd.DataFrame(results)
    results_df.to_csv("processed_tickets.csv", index=False)
    print("✅ Batch Processing Complete! Results saved to 'processed_tickets.csv'.")

if __name__ == "__main__":
    run_batch()
