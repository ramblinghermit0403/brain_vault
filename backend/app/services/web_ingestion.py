from langchain_community.document_loaders import WebBaseLoader
import re

class WebIngestionService:
    def fetch_url(self, url: str):
        """
        Fetch content from a URL using LangChain's WebBaseLoader.
        Returns a dictionary with 'title' and 'content'.
        """
        try:
            # Use a generic user agent to avoid blocking
            loader = WebBaseLoader(
                web_path=url,
                header_template={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            docs = loader.load()
            
            if not docs:
                return None
                
            doc = docs[0]
            title = doc.metadata.get("title", url)
            content = doc.page_content
            
            # Basic cleanup: remove excessive newlines
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            return {
                "title": title.strip(),
                "content": content.strip(),
                "source": url
            }
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            raise e

web_ingestion = WebIngestionService()
