from youtube_transcript_api import YouTubeTranscriptApi
import traceback

VIDEO_ID = 'bvb3M6P9wIA'

print(f"--- DETAILED DEBUG FOR {VIDEO_ID} ---")
try:
    txn_list = YouTubeTranscriptApi.list_transcripts(VIDEO_ID)
    print("Listing success. Available:")
    for t in txn_list:
        print(f" - {t.language_code} (Generated: {t.is_generated})")
        
        # Try to fetch THIS specific transcript
        print(f"   Attempting fetch for {t.language_code}...")
        try:
            data = t.fetch()
            print(f"   SUCCESS! Got {len(data)} lines.")
            break
        except Exception as e:
            print(f"   FETCH FAILED: {type(e).__name__}: {e}")
            # traceback.print_exc() 
            
except Exception as e:
    print(f"LISTING FAILED: {e}")
    traceback.print_exc()
