from app.services.youtube_service import youtube_service
from youtube_transcript_api import YouTubeTranscriptApi
import traceback

print(f"YouTubeTranscriptApi: {YouTubeTranscriptApi}")
print(f"Dir: {dir(YouTubeTranscriptApi)}")

try:
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Roll
    print(f"Testing URL: {url}")
    # transcript = youtube_service.extract_transcript(url) # This uses get_transcript
    
    # Try direct fetch
    video_id = "dQw4w9WgXcQ"
    video_id = "dQw4w9WgXcQ"
    print(f"Calling YouTubeTranscriptApi().fetch('{video_id}')...")
    try:
        api = YouTubeTranscriptApi()
        api = YouTubeTranscriptApi()
        result = api.fetch(video_id)
        print("Success!")
        print(f"Result Type: {type(result)}")
        if hasattr(result, 'snippets'):
            snippets = result.snippets
            print(f"Snippets Type: {type(snippets)}")
            print(f"Number of snippets: {len(snippets)}")
            for i in range(min(3, len(snippets))):
                print(f"Snippet {i}: {snippets[i]}")
        else:
            print(f"Dir: {dir(result)}")
    except Exception as e:
        print(f"Instance fetch failed: {e}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
