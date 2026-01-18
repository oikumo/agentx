import asyncio

from agent_x.modules.llm.langchain.tools.tavily_web_ingestion.custom_ingestion_map_extract import data_ingestion

if __name__ == "__main__":
    asyncio.run(data_ingestion())