# App Modules - Document Loaders - Agent-X

**Path**: `src/app_modules/document_loaders/`

PDF loading and text chunking.

---

## Module Structure

```
src/app_modules/document_loaders/
└── pdf_loader.py              # PDF loading
```

---

## PDF Loader

### pdf_loader.py

**Function**: `pdf_loader(pdf_path: str)`

Loads PDF via `PyPDFLoader`, splits with `CharacterTextSplitter` (chunk_size=1000, chunk_overlap=30, separator="\n").
