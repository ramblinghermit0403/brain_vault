from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import traceback
import sys

def test_video(video_id, name):
    print(f"\n--- Testing {name} ({video_id}) ---")
    try:
        # 1. Try listing
        print("1. Listing transcripts...")
        txn_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("   Available:", [t.language_code for t in txn_list])
        
        # 2. Try fetching English
        print("2. Fetching English...")
        try:
            t = txn_list.find_transcript(['en', 'en-US', 'en-GB'])
            print(f"   Found English ({t.language_code}), fetching...")
            data = t.fetch()
            print(f"   Success! {len(data)} lines.")
            print(f"   Sample: {data[0]['text']}")
        except:
            print("   No direct English found. Trying auto-generated...")
            try:
                t = txn_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
                print(f"   Found Auto-En ({t.language_code}), fetching...")
                data = t.fetch()
                print(f"   Success! {len(data)} lines.")
            except:
                print("   No English auto-generated found.")

    except Exception:
        print("   FAILED.")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        from importlib.metadata import version
        print(f"Library Version: {version('youtube-transcript-api')}")
    except:
        print("Library Version: Unknown")

    # User's video
    test_video('bvb3M6P9wIA', "User Video")
    
    # Control video (Rick Roll - known to have manual + auto captions)
    test_video('dQw4w9WgXcQ', "Control Video")
