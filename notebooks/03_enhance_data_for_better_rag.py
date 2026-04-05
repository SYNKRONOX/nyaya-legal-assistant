# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Enhance Legal Corpus for Better RAG
# MAGIC
# MAGIC This notebook creates an enhanced version of the legal corpus that includes:
# MAGIC - Full context (question + correct answer)
# MAGIC - Rich metadata for filtering
# MAGIC - Better structured text for embeddings
# MAGIC
# MAGIC **Run this after 01_ingest_data.py to improve retrieval quality**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create Enhanced Corpus Table
# MAGIC
# MAGIC This table adds the correct answer text to each question for richer context.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace_7474652263326815.default.nyaya_legal_corpus_enhanced AS
# MAGIC SELECT 
# MAGIC     id,
# MAGIC     question,
# MAGIC     
# MAGIC     -- Combine question with the correct answer for better context
# MAGIC     CONCAT(
# MAGIC         'Legal Question: ', question, '\n\n',
# MAGIC         'Answer: ',
# MAGIC         CASE correct_answer 
# MAGIC             WHEN 'A' THEN option_a
# MAGIC             WHEN 'B' THEN option_b
# MAGIC             WHEN 'C' THEN option_c
# MAGIC             WHEN 'D' THEN option_d
# MAGIC             ELSE 'Not specified'
# MAGIC         END, '\n\n',
# MAGIC         'Legal Domain: ', subject_domain, '\n',
# MAGIC         'Topic: ', topic, '\n',
# MAGIC         'Difficulty: ', question_level
# MAGIC     ) as full_context,
# MAGIC     
# MAGIC     -- Keep original fields for metadata
# MAGIC     topic,
# MAGIC     subject_domain,
# MAGIC     question_level,
# MAGIC     language,
# MAGIC     correct_answer,
# MAGIC     
# MAGIC     -- Add the correct answer text
# MAGIC     CASE correct_answer 
# MAGIC         WHEN 'A' THEN option_a
# MAGIC         WHEN 'B' THEN option_b
# MAGIC         WHEN 'C' THEN option_c
# MAGIC         WHEN 'D' THEN option_d
# MAGIC     END as answer_text
# MAGIC     
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus
# MAGIC WHERE correct_answer IN ('A', 'B', 'C', 'D')  -- Filter out any invalid data

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Verify the Enhanced Table

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check row count
# MAGIC SELECT COUNT(*) as total_rows
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus_enhanced

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Preview the enhanced data
# MAGIC SELECT 
# MAGIC     id,
# MAGIC     question,
# MAGIC     answer_text,
# MAGIC     subject_domain,
# MAGIC     topic,
# MAGIC     question_level
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus_enhanced
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- See a full_context example
# MAGIC SELECT full_context
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus_enhanced
# MAGIC WHERE question LIKE '%IPC%'
# MAGIC LIMIT 1

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Analyze Data Distribution

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Distribution by subject domain
# MAGIC SELECT 
# MAGIC     subject_domain,
# MAGIC     COUNT(*) as count,
# MAGIC     ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM workspace_7474652263326815.default.nyaya_legal_corpus_enhanced), 2) as percentage
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus_enhanced
# MAGIC GROUP BY subject_domain
# MAGIC ORDER BY count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Distribution by difficulty level
# MAGIC SELECT 
# MAGIC     question_level,
# MAGIC     COUNT(*) as count
# MAGIC FROM workspace_7474652263326815.default.nyaya_legal_corpus_enhanced
# MAGIC GROUP BY question_level
# MAGIC ORDER BY count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔄 Next Steps
# MAGIC
# MAGIC After running this notebook:
# MAGIC
# MAGIC 1. **Rebuild FAISS Index** - Run `02_build_faiss_index.py` but modify it to use `full_context` column instead of just `question`
# MAGIC 2. **Test Retrieval Quality** - The richer context should improve answer accuracy
# MAGIC 3. **Consider Vector Search** - For production, migrate to Databricks Vector Search for automatic index updates
# MAGIC
# MAGIC ### 🚀 Future Enhancement: Databricks Vector Search
# MAGIC
# MAGIC Instead of maintaining FAISS manually, you can create a Vector Search index directly on this enhanced table:
# MAGIC
# MAGIC ```sql
# MAGIC -- Create Vector Search index (requires Vector Search endpoint)
# MAGIC CREATE VECTOR SEARCH INDEX IF NOT EXISTS nyaya_legal_index
# MAGIC ON workspace_7474652263326815.default.nyaya_legal_corpus_enhanced
# MAGIC (
# MAGIC   id,
# MAGIC   full_context USING COLUMN AS TEXT,
# MAGIC   subject_domain,
# MAGIC   topic,
# MAGIC   question_level
# MAGIC )
# MAGIC WITH (
# MAGIC   primary_key = 'id',
# MAGIC   endpoint_name = 'nyaya-legal-endpoint',
# MAGIC   embedding_dimension = 1024,
# MAGIC   embedding_model = 'databricks-bge-large-en'
# MAGIC );
# MAGIC ```
# MAGIC
# MAGIC Benefits:
# MAGIC - Automatic index updates when table changes
# MAGIC - Built-in hybrid search (vector + keyword)
# MAGIC - Production-grade scaling and availability
# MAGIC - No manual embedding generation needed
