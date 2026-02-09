try:
    import youtube_transcript_api
    from youtube_transcript_api import YouTubeTranscriptApi
    from importlib.metadata import version
    print(f"Version: {version('youtube-transcript-api')}")
    print(f"Attributes: {dir(YouTubeTranscriptApi)}")
except ImportError:
    print("Library not found")
except Exception as e:
    print(f"Error: {e}")
