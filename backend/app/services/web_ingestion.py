import httpx
from bs4 import BeautifulSoup
import re
import traceback

class WebIngestionService:
    async def fetch_url(self, url: str):
        """
        Fetch content from a URL using httpx (async).
        Returns a dictionary with 'title' and 'content'.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            # Use HTTP/2 for better compatibility with modern sites
            # Increase timeout - some sites are slow to respond
            timeout = httpx.Timeout(60.0, connect=10.0)
            async with httpx.AsyncClient(
                timeout=timeout, 
                follow_redirects=True,
                http2=True
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                # Get text with proper encoding
                html_content = response.text
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract title
                title = url
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                    script.decompose()
                
                # Get text content
                content = soup.get_text(separator='\n', strip=True)
                
                # Basic cleanup: remove excessive newlines
                content = re.sub(r'\n{3,}', '\n\n', content)
                
                # Sanitize content: remove null bytes and non-printable characters
                # This prevents PostgreSQL encoding errors
                content = content.replace('\x00', '')
                content = ''.join(char for char in content if char.isprintable() or char in '\n\r\t')
                title = title.replace('\x00', '')
                title = ''.join(char for char in title if char.isprintable() or char in '\n\r\t')
                
                if not content or len(content) < 50:
                    raise ValueError("No meaningful content extracted from URL")
                
                return {
                    "title": title,
                    "content": content.strip(),
                    "source": url
                }
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching URL {url}: {e.response.status_code} - {e.response.reason_phrase}")
            raise e
        except Exception as e:
            print(f"Error fetching URL {url}: {type(e).__name__}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Fallback: try without SSL verification and HTTP/2
            try:
                print(f"Attempting fallback without SSL verification...")
                async with httpx.AsyncClient(timeout=timeout, verify=False, follow_redirects=True) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string.strip() if soup.title and soup.title.string else url
                    for script in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                        script.decompose()
                    content = soup.get_text(separator='\n', strip=True)
                    content = re.sub(r'\n{3,}', '\n\n', content)
                    # Sanitize content
                    content = content.replace('\x00', '')
                    content = ''.join(char for char in content if char.isprintable() or char in '\n\r\t')
                    title = title.replace('\x00', '')
                    title = ''.join(char for char in title if char.isprintable() or char in '\n\r\t')
                    return {"title": title, "content": content.strip(), "source": url}
            except Exception as e2:
                print(f"Fallback also failed: {type(e2).__name__}: {e2}")
                print(f"Fallback traceback: {traceback.format_exc()}")
                raise e

web_ingestion = WebIngestionService()

