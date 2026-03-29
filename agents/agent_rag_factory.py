from agents.rag_pdf.agent_rag_pdf import AgentRagPdf
from app.common.utils.file_utils import create_directory_with_timestamp
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_QWEN_2_5, model_factory_llamacpp
from llm_models.local.ollama.ollama_embeddings import create_embeddings_model


def create_agent_rag_local():
    vector_db_path = create_directory_with_timestamp("faiss_index_react", "local_vector_databases")
    config = LlamaCppConfig()
    config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
    config.context_size = 32768
    llm = model_factory_llamacpp.create_model_instance(config)
    ollama_embeddings = create_embeddings_model()

    pdf_path = "_resources/react.pdf"
    vectorstore_path = vector_db_path
    llm = llm
    embeddings = ollama_embeddings

    return AgentRagPdf(
        pdf_path=pdf_path,
        vectorstore_path=vectorstore_path,
        llm=llm,
        embeddings=embeddings
    )