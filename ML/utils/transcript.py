from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging

logger = logging.getLogger(__name__)

PREFERRED_LANGUAGES = ["en", "en-US", "en-GB"]

def get_youtube_transcript(video_id: str) -> str:
    """
    Fetches and flattens the transcript for a YouTube video into plain text.

    Selection preference:
      1. A manually created transcript in a preferred (English) language
      2. An auto-generated transcript in a preferred language
      3. Any other manually created transcript
      4. Any other available transcript

    Returns the joined transcript text, or None if no transcript is available.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
    except TranscriptsDisabled:
        logger.warning("Captions are disabled for video %s", video_id)
        return None
    except Exception:
        logger.exception("Failed to list transcripts for video %s", video_id)
        return None
    
    transcript = _select_best_transcript(transcript_list)
    if transcript is None:
        logger.warning("No usable transcript found for video %s", video_id)
        return None
    
    try:
        raw_transcript = transcript.fetch()
    except NoTranscriptFound:
        logger.warning("Transcript disappeared before fetch for video %s", video_id)
        return None
    except Exception:
        logger.exception("Failed to fetch transcript for video %s", video_id)
        return None
            
    texts = [
        chunk["text"] if isinstance(chunk, dict) else chunk.text
        for chunk in raw_transcript
    ]
    text = " ".join(texts).strip()
    return text or None


def _select_best_transcript(transcript_list):
    """Picks the best available transcript from a TranscriptList."""
    try:
        return transcript_list.find_manually_created_transcript(PREFERRED_LANGUAGES)
    except NoTranscriptFound:
        pass

    try:
        return transcript_list.find_generated_transcript(PREFERRED_LANGUAGES)
    except NoTranscriptFound:
        pass

    manual_transcripts = [t for t in transcript_list if not t.is_generated]
    if manual_transcripts:
        return manual_transcripts[0]

    for transcript in transcript_list:
        return transcript

    return None


# for testing
# video_data = get_youtube_transcript("YimMzb0mHkI")
# with open("data.txt", 'w', encoding="utf-8") as f:
#     data = f.write(video_data)