from app.services.youtube_service import youtube_service
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Hindi Video (Likely has Hindi captions but no English)
url_hi = "https://www.youtube.com/watch?v=hZv6QTI7viQ"
print(f"Testing Hindi URL: {url_hi}")
try:
    # Just try the internal logic to see the raw exception first
    api = YouTubeTranscriptApi()
    api.fetch('hZv6QTI7viQ', languages=['en', 'en-US'])
except Exception as e:
    print(f"Raw Exception (Hindi Video): {type(e).__name__}: {e}")

print("-" * 20)

# 2. Test the service wrapper
try:
    youtube_service.extract_transcript(url_hi)
except Exception as e:
    print(f"Service Exception: {e}")
