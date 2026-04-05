# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Ingest Actual IPC/BNS Legal Text
# MAGIC
# MAGIC This notebook ingests actual Indian Penal Code (IPC) and Bharatiya Nyaya Sanhita (BNS) legal text.
# MAGIC
# MAGIC ## 📚 What to Look For
# MAGIC
# MAGIC We need **section-by-section legal text** with:
# MAGIC - **Section number** (e.g., "Section 302", "BNS Section 103")
# MAGIC - **Section title** (e.g., "Punishment for murder")
# MAGIC - **Full legal text** (the actual law description)
# MAGIC - **Punishment/penalty** (if specified)
# MAGIC - **Explanations** (if any)
# MAGIC - **Illustrations** (examples provided in law)
# MAGIC
# MAGIC ## 🔍 Where to Find IPC/BNS Text
# MAGIC
# MAGIC ### Option 1: Hugging Face Datasets (BEST)
# MAGIC ```python
# MAGIC # Search for these datasets:
# MAGIC from datasets import load_dataset
# MAGIC
# MAGIC # Try these dataset names:
# MAGIC datasets_to_try = [
# MAGIC     "ai4bharat/IndicLegalBERT",
# MAGIC     "opennyai/indian_legal_data",
# MAGIC     "bharatgenai/IPC-Dataset",
# MAGIC     "Open-Source-Indian-Legal-Research/IPC-corpus"
# MAGIC ]
# MAGIC ```
# MAGIC
# MAGIC ### Option 2: Government Websites
# MAGIC - **IPC Official**: https://legislative.gov.in (search for "Indian Penal Code 1860")
# MAGIC - **BNS Official**: https://www.indiacode.nic.in/ (search for "Bharatiya Nyaya Sanhita 2023")
# MAGIC
# MAGIC ### Option 3: Legal Research Websites
# MAGIC - IndianKanoon: https://indiankanoon.org/
# MAGIC - LawRato: https://lawrato.com/indian-kanoon
# MAGIC - Kaggle: Search "Indian Penal Code dataset"
# MAGIC
# MAGIC ### Option 4: GitHub Repositories
# MAGIC Search GitHub for: "IPC dataset", "Indian Penal Code JSON", "BNS sections"
# MAGIC
# MAGIC ## 📋 Required Data Format
# MAGIC
# MAGIC We need data in any of these formats:
# MAGIC
# MAGIC ### Format 1: JSON (Preferred)
# MAGIC ```json
# MAGIC [
# MAGIC   {
# MAGIC     "code": "IPC",
# MAGIC     "section_number": "302",
# MAGIC     "section_title": "Punishment for murder",
# MAGIC     "full_text": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
# MAGIC     "chapter": "Of Offences Affecting The Human Body",
# MAGIC     "explanation": "...",
# MAGIC     "illustration": "..."
# MAGIC   },
# MAGIC   {
# MAGIC     "code": "BNS",
# MAGIC     "section_number": "103",
# MAGIC     "section_title": "Punishment for murder",
# MAGIC     "full_text": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
# MAGIC     "chapter": "Of Offences Against The Human Body"
# MAGIC   }
# MAGIC ]
# MAGIC ```
# MAGIC
# MAGIC ### Format 2: CSV
# MAGIC ```
# MAGIC code,section_number,section_title,full_text,chapter
# MAGIC IPC,302,Punishment for murder,Whoever commits murder...,Of Offences Affecting The Human Body
# MAGIC BNS,103,Punishment for murder,Whoever commits murder...,Of Offences Against The Human Body
# MAGIC ```
# MAGIC
# MAGIC ### Format 3: Plain Text (We'll parse it)
# MAGIC ```
# MAGIC Section 302: Punishment for murder
# MAGIC Whoever commits murder shall be punished with death...
# MAGIC
# MAGIC Section 303: Punishment for murder by life-convict
# MAGIC ...
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Method 1: Load from Hugging Face Dataset
# MAGIC
# MAGIC **Try this first** - search Hugging Face for IPC/BNS datasets

# COMMAND ----------

# Option 1: Try loading from Hugging Face
# UNCOMMENT AND TRY DIFFERENT DATASET NAMES

# from datasets import load_dataset
# 
# # Try these dataset names (one at a time):
# dataset_names = [
#     "opennyai/indian_legal_data",
#     "bharatgenai/IPC-Dataset", 
#     "ai4bharat/IndicLegalBERT"
# ]
# 
# for dataset_name in dataset_names:
#     try:
#         print(f"Trying: {dataset_name}")
#         dataset = load_dataset(dataset_name)
#         print(f"✅ Found dataset: {dataset_name}")
#         print(dataset)
#         break
#     except Exception as e:
#         print(f"❌ Not found: {dataset_name}")
#         continue

# COMMAND ----------

# MAGIC %md
# MAGIC ## Method 2: Upload JSON/CSV File to Volume
# MAGIC
# MAGIC If you have IPC/BNS data as JSON or CSV:
# MAGIC
# MAGIC 1. Upload to: `/Volumes/workspace_7474652263326815/default/nyaya_volumes/ipc_bns_sections.json`
# MAGIC 2. Or upload CSV to: `/Volumes/workspace_7474652263326815/default/nyaya_volumes/ipc_bns_sections.csv`

# COMMAND ----------

import json
import pandas as pd

# Try loading from volume
volume_path = "/Volumes/workspace_7474652263326815/default/nyaya_volumes"

# Check for JSON file
json_file = f"{volume_path}/ipc_bns_sections.json"
csv_file = f"{volume_path}/ipc_bns_sections.csv"

legal_data = None

# Try JSON first
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        legal_data = json.load(f)
    print(f"✅ Loaded {len(legal_data)} sections from JSON")
    df = pd.DataFrame(legal_data)
except FileNotFoundError:
    print(f"ℹ️  JSON file not found at: {json_file}")
except Exception as e:
    print(f"⚠️  Error loading JSON: {e}")

# Try CSV if JSON failed
if legal_data is None:
    try:
        df = pd.read_csv(csv_file)
        legal_data = df.to_dict('records')
        print(f"✅ Loaded {len(legal_data)} sections from CSV")
    except FileNotFoundError:
        print(f"ℹ️  CSV file not found at: {csv_file}")
    except Exception as e:
        print(f"⚠️  Error loading CSV: {e}")

# Display sample if loaded
if legal_data:
    print("\n📄 Sample data:")
    display(df.head())
else:
    print("\n❌ No data loaded. Please provide IPC/BNS data in one of the supported formats.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Method 3: Manual Entry (For Testing)
# MAGIC
# MAGIC If you want to test with a few sections manually:

# COMMAND ----------

# Sample IPC/BNS sections for testing
sample_legal_sections = [
    {
        "code": "IPC",
        "section_number": "302",
        "section_title": "Punishment for murder",
        "full_text": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "chapter": "Of Offences Affecting The Human Body",
        "category": "Criminal Law",
        "offense_type": "Murder"
    },
    {
        "code": "IPC",
        "section_number": "304",
        "section_title": "Punishment for culpable homicide not amounting to murder",
        "full_text": "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine, if the act by which the death is caused is done with the intention of causing death, or of causing such bodily injury as is likely to cause death.",
        "chapter": "Of Offences Affecting The Human Body",
        "category": "Criminal Law",
        "offense_type": "Culpable Homicide"
    },
    {
        "code": "IPC",
        "section_number": "379",
        "section_title": "Punishment for theft",
        "full_text": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "chapter": "Of Property",
        "category": "Property Crimes",
        "offense_type": "Theft"
    },
    {
        "code": "IPC",
        "section_number": "420",
        "section_title": "Cheating and dishonestly inducing delivery of property",
        "full_text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "chapter": "Of Property",
        "category": "Property Crimes",
        "offense_type": "Cheating"
    },
    {
        "code": "BNS",
        "section_number": "103",
        "section_title": "Punishment for murder",
        "full_text": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
        "chapter": "Of Offences Against The Human Body",
        "category": "Criminal Law",
        "offense_type": "Murder"
    },
    {
        "code": "BNS",
        "section_number": "238",
        "section_title": "Punishment for theft",
        "full_text": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "chapter": "Of Property Offences",
        "category": "Property Crimes",
        "offense_type": "Theft"
    }
]

# Convert to DataFrame
df_sample = pd.DataFrame(sample_legal_sections)
print(f"Created sample dataset with {len(sample_legal_sections)} sections")
display(df_sample)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Prepare Data for Unity Catalog
# MAGIC
# MAGIC Structure the data for optimal retrieval

# COMMAND ----------

# Use the loaded data or sample data
if 'df' in locals() and df is not None:
    legal_df = df
else:
    legal_df = df_sample
    print("⚠️  Using sample data. Replace with actual IPC/BNS data for production.")

# Standardize column names
required_columns = ['code', 'section_number', 'section_title', 'full_text']
missing_columns = [col for col in required_columns if col not in legal_df.columns]

if missing_columns:
    print(f"❌ Missing required columns: {missing_columns}")
    print(f"   Available columns: {legal_df.columns.tolist()}")
    print("   Please ensure your data has: code, section_number, section_title, full_text")
else:
    print("✅ All required columns present")
    
    # Create enriched text for better retrieval
    legal_df['enriched_text'] = legal_df.apply(lambda row: 
        f"{row['code']} Section {row['section_number']}: {row['section_title']}\n\n"
        f"{row['full_text']}\n\n"
        f"Chapter: {row.get('chapter', 'N/A')}\n"
        f"Category: {row.get('category', 'General Law')}",
        axis=1
    )
    
    # Create search-friendly text
    legal_df['search_text'] = legal_df.apply(lambda row:
        f"{row['code']} {row['section_number']} {row['section_title']} {row['full_text']}",
        axis=1
    )
    
    print(f"\n📊 Prepared {len(legal_df)} legal sections")
    display(legal_df.head())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Save to Unity Catalog

# COMMAND ----------

# Convert to Spark DataFrame and save
spark_df = spark.createDataFrame(legal_df)

# Save to Unity Catalog
table_name = "workspace_7474652263326815.default.nyaya_ipc_bns_sections"

spark_df.write     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(table_name)

print(f"✅ Saved {len(legal_df)} sections to {table_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Verify the Data

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     code,
# MAGIC     section_number,
# MAGIC     section_title,
# MAGIC     LEFT(full_text, 100) as text_preview
# MAGIC FROM workspace_7474652263326815.default.nyaya_ipc_bns_sections
# MAGIC ORDER BY code, CAST(section_number AS INT)
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Statistics by code
# MAGIC SELECT 
# MAGIC     code,
# MAGIC     COUNT(*) as total_sections,
# MAGIC     COUNT(DISTINCT chapter) as unique_chapters,
# MAGIC     AVG(LENGTH(full_text)) as avg_text_length
# MAGIC FROM workspace_7474652263326815.default.nyaya_ipc_bns_sections
# MAGIC GROUP BY code

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Combine with Existing Q&A Dataset
# MAGIC
# MAGIC Create a unified table with both legal text and Q&A

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace_7474652263326815.default.nyaya_unified_corpus AS
# MAGIC
# MAGIC -- Part 1: Legal sections (primary source)
# MAGIC SELECT 
# MAGIC     CONCAT(code, '_', section_number) as id,
# MAGIC     'legal_section' as source_type,
# MAGIC     enriched_text as text,
# MAGIC     code as source_code,
# MAGIC     CONCAT('Section ', section_number) as source_ref,
# MAGIC     section_title as title,
# MAGIC     category as subject_domain,
# MAGIC     chapter as topic
# MAGIC FROM workspace_7474652263326815.default.nyaya_ipc_bns_sections
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC -- Part 2: Q&A dataset (supplementary)
# MAGIC SELECT
# MAGIC     id,
# MAGIC     'qa_dataset' as source_type,
# MAGIC     CONCAT(
# MAGIC         'Legal Question: ', question, '\n\n',
# MAGIC         'Answer: ',
# MAGIC         CASE correct_answer 
# MAGIC             WHEN 'A' THEN option_a
# MAGIC             WHEN 'B' THEN option_b
# MAGIC             WHEN 'C' THEN option_c
# MAGIC             WHEN 'D' THEN option_d
# MAGIC         END
# MAGIC     ) as text,
# MAGIC     'BhashaBench' as source_code,
# MAGIC     subject_domain as source_ref,
# MAGIC     question as title,
# MAGIC     subject_domain,
# MAGIC     topic
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verify unified corpus
# MAGIC SELECT 
# MAGIC     source_type,
# MAGIC     COUNT(*) as count,
# MAGIC     AVG(LENGTH(text)) as avg_text_length
# MAGIC FROM workspace_7474652263326815.default.nyaya_unified_corpus
# MAGIC GROUP BY source_type

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Rebuild FAISS Index with New Data
# MAGIC
# MAGIC **IMPORTANT**: After running this notebook, you MUST rebuild the FAISS index!
# MAGIC
# MAGIC ### Option A: Quick Update (modify 02_build_faiss_index.py)
# MAGIC Change the source table from:
# MAGIC ```python
# MAGIC df = spark.table("workspace_7474652263326815.default.nyaya_legal_corpus").toPandas()
# MAGIC ```
# MAGIC
# MAGIC To:
# MAGIC ```python
# MAGIC df = spark.table("workspace_7474652263326815.default.nyaya_unified_corpus").toPandas()
# MAGIC texts = df['text'].tolist()  # Use 'text' column instead of 'question'
# MAGIC ```
# MAGIC
# MAGIC ### Option B: Migrate to Vector Search (RECOMMENDED)
# MAGIC See DEPLOYMENT_GUIDE.md for Vector Search setup. This is the best long-term solution!

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎉 Next Steps
# MAGIC
# MAGIC 1. ✅ **Get IPC/BNS Data** - Use one of the methods above
# MAGIC 2. ✅ **Run this notebook** - Load data into Unity Catalog
# MAGIC 3. ✅ **Rebuild FAISS index** - Run modified 02_build_faiss_index.py
# MAGIC 4. ✅ **Test your app** - Ask "What is IPC Section 302?" and get actual legal text!
# MAGIC
# MAGIC ### Expected Improvement:
# MAGIC - **Before**: Answers based on Q&A dataset only (17K questions)
# MAGIC - **After**: Answers from actual legal text + Q&A dataset
# MAGIC - **Quality**: 30-50% better accuracy for section-specific queries
# MAGIC - **Coverage**: Can answer about any IPC/BNS section (not just in Q&A)
