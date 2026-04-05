import gradio as gr
from src.nyaya.agents import LegalMultiAgent

# 1. Initialize your new bilingual agent
print("Booting up Legal Agent...")
agent = LegalMultiAgent()

def process_query(query, language):
    if not query.strip():
        return "Please enter a legal question."
    
    # 2. Call the agent with the user's chosen language
    try:
        return agent.ask(query=query, target_language=language)
    except Exception as e:
        return f"An error occurred during processing: {str(e)}"

# 3. Build the UI using Gradio Blocks for a professional layout
with gr.Blocks(title="Nyaya Legal Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ⚖️ Nyaya Legal Assistant")
    gr.Markdown("Ask questions about the Indian Penal Code (IPC) and Bharatiya Nyaya Sanhita (BNS) in your preferred language.")
    
    with gr.Row():
        with gr.Column(scale=3):
            user_input = gr.Textbox(
                label="Your Legal Question", 
                placeholder="Type your question here (e.g., चोरी के लिए क्या सजा है?)",
                lines=3
            )
        with gr.Column(scale=1):
            language_dropdown = gr.Dropdown(
                choices=[
                    "English", "Hindi", "Bengali", "Gujarati", "Kannada", 
                    "Malayalam", "Marathi", "Odia", "Punjabi", "Tamil", "Telugu"
                ],
                value="English",
                label="Select Language",
                info="Nyaya will reply in this language."
            )
            
    submit_btn = gr.Button("Ask Nyaya", variant="primary")
    
    output_box = gr.Textbox(label="Legal Assessment", lines=8)
    
    # 4. Wire the button to the function
    submit_btn.click(
        fn=process_query,
        inputs=[user_input, language_dropdown],
        outputs=output_box
    )

if __name__ == "__main__":
    # Databricks App requires routing to 0.0.0.0 on port 8080
    demo.launch(server_name="0.0.0.0", server_port=8080)