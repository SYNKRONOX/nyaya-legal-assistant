# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Setup Secrets for Nyaya Legal Assistant
# MAGIC
# MAGIC This notebook helps you securely store API tokens and credentials using Databricks Secrets.
# MAGIC
# MAGIC **⚠️ IMPORTANT: Run this notebook ONCE to set up your secrets, then use the secrets in other notebooks.**
# MAGIC
# MAGIC ## What are Databricks Secrets?
# MAGIC
# MAGIC Databricks Secrets allow you to securely store sensitive information like API keys without hardcoding them in notebooks.
# MAGIC
# MAGIC ## Setup Steps
# MAGIC
# MAGIC You need to use the Databricks CLI to create secrets. Run these commands in your terminal:
# MAGIC
# MAGIC ```bash
# MAGIC # Install Databricks CLI (if not already installed)
# MAGIC pip install databricks-cli
# MAGIC
# MAGIC # Configure CLI with your workspace
# MAGIC databricks configure --token
# MAGIC
# MAGIC # Create a secret scope
# MAGIC databricks secrets create-scope --scope nyaya_secrets
# MAGIC
# MAGIC # Add your Hugging Face token (replace YOUR_TOKEN with actual token)
# MAGIC databricks secrets put --scope nyaya_secrets --key huggingface_token
# MAGIC # This will open an editor - paste your token, save and close
# MAGIC ```
# MAGIC
# MAGIC ## Alternative: Use Databricks UI
# MAGIC
# MAGIC 1. Go to your Databricks workspace
# MAGIC 2. Navigate to: Settings → Workspace Settings → Secrets (if available)
# MAGIC 3. Or use the Databricks CLI as shown above

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Secrets Setup

# COMMAND ----------

try:
    # Test reading the secret (will show [REDACTED] for security)
    token = dbutils.secrets.get(scope="nyaya_secrets", key="huggingface_token")
    print("✅ Secret 'huggingface_token' is configured!")
    print(f"   Token value: {token}")  # Databricks automatically redacts this
except Exception as e:
    print("❌ Secret not found. Please run the setup commands above.")
    print(f"   Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example: Using Secrets in Your Code
# MAGIC
# MAGIC Once secrets are set up, use them like this in your notebooks:

# COMMAND ----------

# Example: Login to Hugging Face using secrets
from huggingface_hub import login

try:
    token = dbutils.secrets.get(scope="nyaya_secrets", key="huggingface_token")
    login(token=token, add_to_git_credential=False)
    print("✅ Successfully logged in to Hugging Face!")
except Exception as e:
    print(f"❌ Failed to login: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Security Benefits
# MAGIC
# MAGIC ✅ Tokens are never visible in notebook code  
# MAGIC ✅ Secrets are encrypted at rest  
# MAGIC ✅ Access can be controlled with ACLs  
# MAGIC ✅ Secrets don't appear in logs or job outputs  
# MAGIC ✅ Easy to rotate tokens without code changes  

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC After setting up secrets:
# MAGIC 1. Update `01_ingest_data.py` to use `dbutils.secrets.get()` instead of hardcoded token
# MAGIC 2. Remove the hardcoded token from version control
# MAGIC 3. Share the secret scope with team members who need access
