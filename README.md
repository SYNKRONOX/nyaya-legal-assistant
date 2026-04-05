# ⚖️ Nyaya Legal Assistant

> AI-powered multilingual legal assistant for Indian Law (IPC & Bharatiya Nyaya Sanhita)

## ⚠️ CRITICAL LEGAL UPDATE

**📅 July 1, 2024**: The Indian Penal Code (IPC 1860) was **officially repealed** and replaced by:

✅ **Bharatiya Nyaya Sanhita (BNS) 2023** - Current law of India

**For users in 2026:**
- 👥 **General Public**: App cites **BNS only** (current law applicable today)
- 🎓 **Law Students**: App provides **BNS + IPC** for educational comparison
- 📚 **Historical Queries**: Explicitly request "IPC" to see repealed provisions

**Section numbers have changed!** Example: IPC Section 302 (Murder) → BNS Section 103

---

[![Databricks](https://img.shields.io/badge/Databricks-Apps-FF3621?logo=databricks)](https://databricks.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-blue)](https://github.com/langchain-ai/langgraph)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

## 🎯 Overview

Nyaya is a production-ready legal assistant that helps users understand Indian legal codes in 11 languages. Built entirely on Databricks with LangGraph for agent orchestration and Foundation Models for LLM/translation.

**Key Features:**
- 🌐 **11 Languages**: English, Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu
- ⚡ **Fast Retrieval**: Hybrid search combining vector similarity and metadata filtering
- 📊 **Observable**: MLflow tracking for every query (latency, language, context docs)
- 🔒 **Secure**: Input validation, secrets management, error handling
- 🎨 **User-Friendly**: Clean Gradio interface with tips and disclaimers

## 🏗️ Architecture

```
┌─────────────────┐
│   Gradio UI     │  ← User asks question in any language
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│         LangGraph Agent (agents.py)             │
│  ┌──────────────────────────────────────────┐   │
│  │ 1. Validate Input                        │   │
│  │ 2. Retrieve Context (FAISS)              │   │
│  │ 3. Generate Answer (Llama 4 Maverick)    │   │
│  │ 4. Translate (if needed)                 │   │
│  │ 5. Track with MLflow                     │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│        Data Layer (Unity Catalog)               │
│  • nyaya_legal_corpus (17K legal Q&A)           │
│  • FAISS index in UC Volume                     │
│  • MLflow experiments                           │
└─────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
nyaya-legal-assistant/
├── app/
│   └── main.py                    # Gradio UI with validation
├── src/nyaya/
│   ├── agents.py                  # LangGraph agent (LLM-based translation)
│   ├── retriever.py               # FAISS-based retrieval
│   └── faiss_utils.py             # Vector search implementation
├── notebooks/
│   ├── 00_setup_secrets.py        # Instructions for Databricks Secrets
│   ├── 01_ingest_data.py          # Load data from Hugging Face
│   ├── 02_build_faiss_index.py    # Generate embeddings & FAISS index
│   └── 03_enhance_data_for_better_rag.py  # Create enriched corpus
├── app.yaml                       # Databricks App configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Databricks workspace with Unity Catalog enabled
- Access to Foundation Models API (Llama 4 Maverick)
- Hugging Face account (for dataset access)

### 2. Setup Data

```bash
# Run notebooks in order:
1. notebooks/00_setup_secrets.py       # Set up Databricks Secrets
2. notebooks/01_ingest_data.py         # Load legal dataset
3. notebooks/02_build_faiss_index.py   # Build FAISS index
4. notebooks/03_enhance_data_for_better_rag.py  # (Optional) Enhance data quality
```

### 3. Deploy App

```bash
# From Databricks workspace:
databricks apps deploy nyaya-legal-assistant

# Or use the UI:
# 1. Go to Apps → Create App
# 2. Select this directory
# 3. Click Deploy
```

### 4. Access Your App

The app will be available at: `https://<workspace>.cloud.databricks.com/apps/<app-id>`

## 🔧 Configuration

### Environment Variables (app.yaml)

```yaml
env:
  - name: "FAISS_INDEX_PATH"
    value: "/Volumes/workspace_7474652263326815/default/nyaya_volumes/legal_index.faiss"
  - name: "FAISS_METADATA_PATH"
    value: "/Volumes/workspace_7474652263326815/default/nyaya_volumes/legal_metadata.pkl"
```

### Volumes (app.yaml)

```yaml
volumes:
  - name: nyaya-data
    volume:
      path: /Volumes/workspace_7474652263326815/default/nyaya_volumes
```

## 📊 Data Source

**Dataset**: [bharatgenai/BhashaBench-Legal](https://huggingface.co/datasets/bharatgenai/BhashaBench-Legal)
- 17,047 legal questions & answers
- Covers IPC, criminal law, evidence law, family law
- Multiple difficulty levels and subject domains

## 🔮 Future Enhancements

### Phase 1: Vector Search Migration
Replace FAISS with Databricks Vector Search for:
- Automatic index updates
- Built-in hybrid search
- Production-grade scaling
- Reduced maintenance

### Phase 2: Enhanced Data
- Ingest actual IPC/BNS legal text (not just Q&A)
- Add citation extraction
- Support case law references

### Phase 3: Advanced Features
- Document analysis (PDF upload for legal docs)
- Multi-turn conversations with memory
- Legal drafting assistance
- Comparison of IPC vs BNS provisions

## 🛡️ Security

- ✅ API tokens stored in Databricks Secrets
- ✅ Input validation and sanitization
- ✅ No SQL injection vulnerabilities
- ✅ Error messages don't leak sensitive info
- ✅ MLflow tracking without PII logging

## 📈 Monitoring

All queries are tracked with MLflow:
- Language requested
- Query length
- Retrieval latency
- Number of context documents
- Answer length
- Error rates

Access MLflow dashboard: `https://<workspace>.cloud.databricks.com/ml/experiments`

## 🤝 Contributing

Improvements welcome! Key areas:
1. Better legal text corpus (actual IPC/BNS documents)
2. Enhanced multilingual support
3. Citation extraction algorithms
4. User feedback collection

## 📄 License

This project is for educational and informational purposes. Legal advice should be obtained from qualified lawyers.

## 🙏 Acknowledgments

- [BharatGPT](https://huggingface.co/bharatgenai) for the BhashaBench-Legal dataset
- Databricks for Foundation Models and infrastructure
- LangGraph for agent orchestration
- Gradio for the UI framework

## 📞 Support

For issues or questions:
1. Check MLflow logs for app errors
2. Verify FAISS index exists in Unity Catalog volume
3. Confirm Foundation Models API access
4. Review Databricks App deployment logs

---

**Built with ❤️ for accessible legal information in India**
