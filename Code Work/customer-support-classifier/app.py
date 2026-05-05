import gradio as gr
import pandas as pd
import os
from agent import graph, get_graph_image
from PIL import Image
import io

# Load Dataset
csv_path = "tickets.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    df = pd.DataFrame(columns=["ticket_id", "message"])

def process_ticket(message):
    if not message:
        return "Please enter a message.", "", "", "", None
    
    # Run Graph
    result = graph.invoke({"message": message})
    
    # Get Graph Image
    img_data = get_graph_image()
    img = Image.open(io.BytesIO(img_data))
    
    return (
        result.get("priority", "N/A"),
        result.get("category", "N/A"),
        result.get("status", "N/A"),
        result.get("email_draft", "N/A"),
        img
    )

def load_example(idx):
    if idx < len(df):
        return df.iloc[idx]["message"]
    return ""

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎫 Customer Support Ticket Classifier")
    gr.Markdown("Assigns priority, categorizes, and drafts responses using LangGraph.")
    
    with gr.Row():
        with gr.Column(scale=2):
            message_input = gr.Textbox(label="Support Ticket Message", lines=5, placeholder="Paste ticket message here...")
            submit_btn = gr.Button("Classify Ticket", variant="primary")
            
            gr.Markdown("### Examples from CSV")
            examples = gr.Examples(
                examples=df["message"].head(10).tolist(),
                inputs=message_input,
                label="Click an example to load it"
            )
            
        with gr.Column(scale=1):
            priority_out = gr.Textbox(label="Priority")
            category_out = gr.Textbox(label="Category")
            status_out = gr.Textbox(label="Status")
    
    with gr.Row():
        draft_out = gr.Textbox(label="Email Draft", lines=10)
        
    with gr.Row():
        gr.Markdown("### Workflow Visualization")
        graph_img = gr.Image(label="LangGraph Flow")

    submit_btn.click(
        process_ticket,
        inputs=[message_input],
        outputs=[priority_out, category_out, status_out, draft_out, graph_img]
    )

if __name__ == "__main__":
    demo.launch(share=False)
