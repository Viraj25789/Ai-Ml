
import logging

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

logger = logging.getLogger(__name__)

PREFERRED_LANGUAGES = ["en", "en-US", "en-GB"]


def get_youtube_transcript(video_id: str) -> str | None:
    """
    Fetch and combine a YouTube video's transcript.

    Prefers manually created English captions, then generated English
    captions, then other available languages.

    Returns:
        Transcript text, or None if captions are unavailable.

    Raises:
        ValueError: If the video ID is invalid.
        RuntimeError: If YouTube cannot be reached or the transcript
                      cannot be fetched.
    """
    if not isinstance(video_id, str) or len(video_id) != 11:
        raise ValueError("Invalid YouTube video ID.")

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

    except TranscriptsDisabled:
        logger.warning("Captions are disabled for video %s", video_id)
        return None

    except NoTranscriptFound:
        logger.warning("No transcripts found for video %s", video_id)
        return None

    except Exception as error:
        logger.exception("Could not retrieve transcript list for %s", video_id)
        raise RuntimeError(
            "Could not connect to YouTube to retrieve captions. "
            "Please try again later."
        ) from error

    try:
        transcript = _select_best_transcript(transcript_list)

    except Exception as error:
        logger.exception("Could not select transcript for %s", video_id)
        raise RuntimeError(
            "Could not select an available transcript."
        ) from error

    if transcript is None:
        logger.warning("No usable transcript found for video %s", video_id)
        return None

    try:
        fetched_transcript = transcript.fetch()

    except NoTranscriptFound:
        logger.warning("Transcript is no longer available for %s", video_id)
        return None

    except Exception as error:
        logger.exception("Could not fetch transcript for %s", video_id)
        raise RuntimeError(
            "YouTube could not provide the transcript. "
            "The video may be temporarily unavailable."
        ) from error

    try:
        text_parts = []

        for segment in fetched_transcript:
            segment_text = (
                segment.get("text")
                if isinstance(segment, dict)
                else getattr(segment, "text", None)
            )

            if isinstance(segment_text, str) and segment_text.strip():
                text_parts.append(segment_text.strip())

        transcript_text = " ".join(text_parts).strip()

    except Exception as error:
        logger.exception("Could not process transcript for %s", video_id)
        raise RuntimeError(
            "The downloaded transcript could not be processed."
        ) from error

    return transcript_text or None


def _select_best_transcript(transcript_list):
    """Select the most suitable available transcript."""

    try:
        return transcript_list.find_manually_created_transcript(
            PREFERRED_LANGUAGES
        )
    except NoTranscriptFound:
        pass

    try:
        return transcript_list.find_generated_transcript(
            PREFERRED_LANGUAGES
        )
    except NoTranscriptFound:
        pass

    manual_transcripts = [
        transcript
        for transcript in transcript_list
        if not transcript.is_generated
    ]

    if manual_transcripts:
        return manual_transcripts[0]

    for transcript in transcript_list:
        return transcript

    return None
