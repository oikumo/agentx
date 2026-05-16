import asyncio
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_tavily import TavilyExtract, TavilyMap


class WebExtract:
    def __init__(self, max_depth: int, max_breadth: int, max_pages: int):
        self.tavily_extract = TavilyExtract()
        self.tavily_map = TavilyMap(max_depth=max_depth,
                                    max_breadth=max_breadth,
                                    max_pages=max_pages)
        # tavily_crawl = TavilyCrawl()

    async def extract_batch(self, urls: List[str], batch_num: int) -> List[Dict[str, Any]]:
        """Extract documents from a batch of URLs."""
        try:
            print(f"🔄 Processing batch {batch_num} with {len(urls)} URLs")
            docs = await self.tavily_extract.ainvoke(input={"urls": urls})
            results = docs.get('results', [])
            print(f"✅ Batch {batch_num} completed - extracted {len(results)} documents")
            return results
        except Exception as e:
            print(f"❌ Batch {batch_num} failed: {e}")
            return []


    async def async_extract(self, urls_batches: List[List[str]]):
        print("DOCUMENT EXTRACTION")
        print(f"Concurrent extraction of {len(urls_batches)}")

        tasks = [self.extract_batch(batch, i + 1) for i, batch in enumerate(urls_batches)]

        print("EXTRACT BEGIN")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("EXTRACT END")

        all_pages = []
        failed_batches = 0

        for result in results:
            if isinstance(result, Exception):
                print("Error")
                failed_batches += 1
            else:
                for extracted_page in result:
                    document = Document(
                        page_content=extracted_page["raw_content"],
                        metadata={"source": extracted_page["url"]}
                    )

                    all_pages.append(document)

        return all_pages