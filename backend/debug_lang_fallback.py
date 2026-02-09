from youtube_transcript_api import YouTubeTranscriptApi

video_id = "hZv6QTI7viQ" # The failing video (Hindi)

try:
    print(f"Fetching transcripts for {video_id}...")
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    # Try fetching English
    try:
        transcript = transcript_list.find_transcript(['en'])
        print("Found English transcript!")
    except:
        print("No English transcript found. Looking for others...")
        # Just grab the first one
        for t in transcript_list:
             print(f"Found transcript: {t.language_code} ({t.language}) - Generated: {t.is_generated}")
        
        transcript = next(iter(transcript_list))
        print(f"Selected: {transcript.language_code}")
        
        if transcript.is_translatable:
            print("Translating to English...")
            transcript = transcript.translate('en')
            print("Translation successful object selection.")

    print("Fetching data...")
    result = transcript.fetch()
    print(f"First line: {result[0]}")
    
except Exception as e:
    print(f"Error: {e}")
