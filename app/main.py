import sys
import os

# Add source code directory to Python path
source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)

import gradio as gr
from src.nyaya.agents import LegalMultiAgent
import traceback

print("=" * 80)
print("🚀 Initializing Nyaya Legal Assistant...")
print("=" * 80)

try:
    agent = LegalMultiAgent()
    print("\n✅ Agent initialization successful!")
except Exception as e:
    print(f"\n❌ Failed to initialize agent: {e}")
    traceback.print_exc()
    agent = None

print("=" * 80)

# Language options
LANGUAGES = {
    "English": "English",
    "हिंदी (Hindi)": "Hindi",
    "தமிழ் (Tamil)": "Tamil",
    "తెలుగు (Telugu)": "Telugu",
    "ಕನ್ನಡ (Kannada)": "Kannada",
    "മലയാളം (Malayalam)": "Malayalam",
    "मराठी (Marathi)": "Marathi",
    "বাংলা (Bengali)": "Bengali",
    "ગુજરાતી (Gujarati)": "Gujarati",
    "ਪੰਜਾਬੀ (Punjabi)": "Punjabi",
    "اردو (Urdu)": "Urdu"
}

def chat(message, history, language):
    """Handle chat interactions with language selection"""
    if agent is None:
        return "❌ Agent failed to initialize. Please check the logs for details."
    
    try:
        target_lang = LANGUAGES.get(language, "English")
        response = agent.ask(message, target_language=target_lang)
        return response
    except Exception as e:
        return f"❌ Error processing query: {str(e)}"

# Create Gradio interface
demo = gr.ChatInterface(
    fn=chat,
    title="⚖️ Nyaya Legal Assistant",
    description='''Ask legal questions about Indian law. Get answers citing:
    • **BNS (Bharatiya Nyaya Sanhita 2023)** - Current law
    • **IPC (Indian Penal Code 1860)** - Historical reference (repealed July 1, 2024)
    
    The assistant automatically detects your intent and provides appropriate legal references.''',
    additional_inputs=[
        gr.Dropdown(
            choices=list(LANGUAGES.keys()),
            value="English",
            label="🌐 Response Language"
        )
    ],
    theme="soft"
)

if __name__ == "__main__":
    print("🌐 Starting Gradio server on 0.0.0.0:8080...")
    demo.launch(server_name="0.0.0.0", server_port=8080, share=True)
