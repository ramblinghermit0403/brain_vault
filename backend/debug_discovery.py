from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("Inspect YouTubeTranscriptApi:")
for name, data in inspect.getmembers(YouTubeTranscriptApi):
    if not name.startswith("__"):
        print(f"{name}: {data}")

try:
    print("Trying get_transcript...")
    YouTubeTranscriptApi.get_transcript("dQw4w9WgXcQ")
except Exception as e:
    print(f"get_transcript failed: {e}")

try:
    print("Trying list_transcripts...")
    # It might be list_transcripts or list
    if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
        t = YouTubeTranscriptApi.list_transcripts("dQw4w9WgXcQ")
        print(f"list_transcripts result: {t}")
    elif hasattr(YouTubeTranscriptApi, 'list'):
        t = YouTubeTranscriptApi.list("dQw4w9WgXcQ")
        print(f"list result: {t}")
except Exception as e:
    print(f"list failed: {e}")
