# PDF Integration Quick Steps

## 1. Upload PDFs
Upload to: /Volumes/workspace_7474652263326815/default/nyaya_volumes/
Files: IPC.pdf, BNS_2023.pdf

## 2. Extract Text
Run: notebooks/05_extract_from_pdf.py

## 3. Update FAISS Notebook
Edit: notebooks/02_build_faiss_index.py
Change source table to: nyaya_unified_corpus
Change text column to: text (instead of question)

## 4. Rebuild Index
Run: notebooks/02_build_faiss_index.py

## 5. Deploy
Your app is ready - just deploy!

## Expected: 800-1000 legal sections + 17K Q&A = 18K total documents
