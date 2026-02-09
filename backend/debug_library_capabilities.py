from youtube_transcript_api import YouTubeTranscriptApi
import inspect

api = YouTubeTranscriptApi()
print(f"Fetch Signature: {inspect.signature(api.fetch)}")

try:
    # Try fetching with explicit languages
    video_id = "hZv6QTI7viQ"
    print(f"Trying fetch with languages=['hi']...")
    result = api.fetch(video_id, languages=['hi'])
    print("Success with languages=['hi']!")
    if hasattr(result, 'snippets'):
        print(f"Snippets count: {len(result.snippets)}")
except Exception as e:
    print(f"Failed with languages=['hi']: {e}")

try:
    print(f"Trying fetch with languages=['en', 'hi']...")
    result = api.fetch(video_id, languages=['en', 'hi'])
    print("Success with languages=['en', 'hi']!")
except Exception as e:
    print(f"Failed with languages=['en', 'hi']: {e}")
