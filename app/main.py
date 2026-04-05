import gradio as gr
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nyaya.agents import LegalMultiAgent

agent = LegalMultiAgent()

def respond(message, history):
    return agent.ask(message)

with gr.Blocks(title="Nyaya Legal Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ⚖️ Nyaya Legal Assistant")
    gr.Markdown("Ask any question about Indian Penal Code (IPC) or Bharatiya Nyaya Sanhita (BNS)")
    
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your question", placeholder="e.g., What is the punishment for theft?")
    clear = gr.Button("Clear")
    
    msg.submit(respond, [msg, chatbot], chatbot).then(lambda: "", None, msg)
    clear.click(lambda: None, None, chatbot)

# Databricks dynamically injects DATABRICKS_APP_PORT
demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("DATABRICKS_APP_PORT", 8080)))