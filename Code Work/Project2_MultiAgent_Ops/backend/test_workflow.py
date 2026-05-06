import requests
import time

BASE_URL = "http://localhost:8003"

def test_multi_agent_workflow():
    print("🚀 Starting Multi-Agent Operations Test...")
    
    # 1. Start Workflow
    task = "Find the latest system stats and then clean up the log directory /var/logs"
    print(f"Submitting Task: {task}")
    
    response = requests.post(f"{BASE_URL}/run", json={"query": task})
    
    try:
        data = response.json()
    except Exception as e:
        print(f"FAILED TO DECODE JSON: {e}")
        print(f"RAW RESPONSE: {response.text}")
        return
    
    thread_id = data["thread_id"]
    print(f"Thread ID: {thread_id}")
    print(f"Current Status: {data['next']}")
    
    # We expect it to reach 'human_approval' or 'executor' with a pending tool call
    if data.get("pending_approval"):
        print(f"⚠️  APPROVAL REQUIRED: {data['pending_approval']}")
        
        # 2. Approve the action
        print("Approving tool execution...")
        app_response = requests.post(f"{BASE_URL}/approve", json={
            "thread_id": thread_id,
            "approve": True
        })
        
        try:
            final_data = app_response.json()
        except Exception as e:
            print(f"FAILED TO DECODE FINAL JSON: {e}")
            print(f"RAW FINAL RESPONSE: {app_response.text}")
            return

        print(f"Workflow Resumed. Logs:")
        for log in final_data["logs"]:
            print(f"  [{log['node']}] {log['action']}")
            
        print("✅ Workflow Completed Successfully.")
    else:
        print("❌ Workflow finished prematurely or missed approval step.")
        print(f"Final messages: {data['messages']}")

if __name__ == "__main__":
    time.sleep(2)
    test_multi_agent_workflow()
