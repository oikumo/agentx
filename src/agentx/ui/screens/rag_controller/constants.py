from agentx.model.rag.rag import RagWebExtractLevel

WEB_EXTRACT_LEVEL_LOW: RagWebExtractLevel = RagWebExtractLevel(label="Low", max_depth=1, max_breadth=1, max_pages=100)
WEB_EXTRACT_LEVEL_MID: RagWebExtractLevel = RagWebExtractLevel(label="Mid", max_depth=2, max_breadth=1, max_pages=150)
WEB_EXTRACT_LEVEL_HIGH: RagWebExtractLevel = RagWebExtractLevel(label="High", max_depth=5, max_breadth=10, max_pages=150)