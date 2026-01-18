

"""
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    show_progress_bar=False,
    chunk_size=50,
    retry_min_seconds=10,)
"""
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_tavily import TavilyExtract, TavilyMap

from agent_x.applications.web_ingestion_app.constants import vectorstore_chroma_dir

load_dotenv()

embeddings = OllamaEmbeddings(model="nomic-embed-text")
#embeddings = OllamaEmbeddings(model="embeddinggemma")

vectorstore = Chroma(persist_directory=vectorstore_chroma_dir, embedding_function=embeddings)
#vectorstore = PineconeVectorStore(index_name=os.environ["INDEX_NAME_DOCUMENT_HELPER"], embedding=embeddings)

tavily_extract = TavilyExtract()
tavily_map = TavilyMap(max_depth=5, max_breadth=2, max_pages=1000)
#tavily_crawl = TavilyCrawl()