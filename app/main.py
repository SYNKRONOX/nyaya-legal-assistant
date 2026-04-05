import gradio as gr
from src.nyaya.agents import LegalMultiAgent
import traceback

# Initialize the bilingual legal agent
print("🚀 Initializing Nyaya Legal Assistant...")
try:
    agent = LegalMultiAgent()
    print("✅ Agent initialization successful!")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    traceback.print_exc()
    agent = None

def process_query(query: str, language: str) -> str:
    """
    Process a legal query with input validation and error handling.
    
    Args:
        query: The user's legal question
        language: Target language for the response
        
    Returns:
        The legal answer or error message
    """
    # Check if agent initialized successfully
    if agent is None:
        return "❌ The legal assistant is not available. Please contact support."
    
    # Input validation
    if not query or not query.strip():
        return "⚠️ Please enter a legal question."
    
    query = query.strip()
    
    if len(query) < 10:
        return "⚠️ Please enter a more detailed question (at least 10 characters)."
    
    if len(query) > 2000:
        return f"⚠️ Query is too long ({len(query)} characters). Please limit to 2000 characters."
    
    # Sanitize input (basic security)
    # Remove any potential SQL injection attempts
    dangerous_patterns = ["DROP TABLE", "DELETE FROM", "INSERT INTO", "UPDATE ", "--", "/*", "*/"]
    query_upper = query.upper()
    for pattern in dangerous_patterns:
        if pattern in query_upper:
            return "⚠️ Invalid query detected. Please rephrase your question."
    
    # Process the query
    try:
        print(f"Processing query in {language}: {query[:100]}...")
        response = agent.ask(query=query, target_language=language)
        return response
    except Exception as e:
        error_type = type(e).__name__
        print(f"Error processing query: {error_type} - {str(e)}")
        traceback.print_exc()
        return f"❌ An error occurred while processing your question. Please try again or rephrase. (Error: {error_type})"

# Build the Gradio UI
with gr.Blocks(
    title="Nyaya Legal Assistant", 
    theme=gr.themes.Soft(),
    css="""
    .container { max-width: 1200px; margin: auto; }
    .header { text-align: center; padding: 20px; }
    """
) as demo:
    
    gr.Markdown(
        """
        # ⚖️ Nyaya Legal Assistant
        ### Your AI-powered guide to Indian Law (IPC & Bharatiya Nyaya Sanhita)
        
        Ask questions about Indian Penal Code, criminal law, or legal procedures in your preferred language.
        """,
        elem_classes=["header"]
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            user_input = gr.Textbox(
                label="Your Legal Question",
                placeholder="Example: What is the punishment for theft under IPC? / चोरी के लिए क्या सजा है?",
                lines=4,
                max_lines=10
            )
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
                submit_btn = gr.Button("🔍 Ask Nyaya", variant="primary", scale=2)
        
        with gr.Column(scale=1):
            language_dropdown = gr.Dropdown(
                choices=[
                    "English",
                    "Hindi",
                    "Bengali", 
                    "Gujarati",
                    "Kannada",
                    "Malayalam",
                    "Marathi",
                    "Odia",
                    "Punjabi",
                    "Tamil",
                    "Telugu"
                ],
                value="English",
                label="Response Language",
                info="Select your preferred language for the answer"
            )
            
            gr.Markdown(
                """
                ### 💡 Tips
                - Be specific in your questions
                - Mention relevant sections if known
                - For better accuracy, provide context
                """
            )
    
    output_box = gr.Textbox(
        label="Legal Assessment",
        lines=12,
        max_lines=20,
        show_copy_button=True
    )
    
    gr.Markdown(
        """
        ---
        **Disclaimer:** This is an AI-powered assistant for informational purposes only. 
        For legal advice, please consult a qualified lawyer.
        
        **Powered by:** Databricks | LangGraph | Foundation Models
        """
    )
    
    # Event handlers
    submit_btn.click(
        fn=process_query,
        inputs=[user_input, language_dropdown],
        outputs=output_box
    )
    
    user_input.submit(  # Allow Enter key to submit
        fn=process_query,
        inputs=[user_input, language_dropdown],
        outputs=output_box
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[user_input, output_box]
    )

if __name__ == "__main__":
    print("🌐 Starting Gradio server on 0.0.0.0:8080...")
    # Databricks Apps require routing to 0.0.0.0 on port 8080
    demo.launch(
        server_name="0.0.0.0",
        server_port=8080,
        show_error=True,
        share=False
    )
