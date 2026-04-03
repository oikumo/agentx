# App Modules - Data Stores - Agent-X

**Path**: `/app_modules/data_stores/`

FAISS vector store creation and persistence.

---

## Module Structure

```
app_modules/data_stores/
└── vector_store_faiss.py      # FAISS vector store
```

---

## FAISS Vector Store

### vector_store_faiss.py

**Function**: `create_faiss(vectorstore_path: str, docs: List[Document], embeddings: Embeddings)`

Builds FAISS index from documents, saves to disk, reloads and returns the vector store.

**Flow**:
1. `FAISS.from_documents(docs, embeddings)`
2. `vectorstore.save_local(vectorstore_path)`
3. `FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)`
