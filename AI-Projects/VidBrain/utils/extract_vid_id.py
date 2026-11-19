
import re
from urllib.parse import parse_qs, urlsplit

VIDEO_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")

YOUTUBE_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    "youtu.be",
}


def extract_video_id(video_url: str) -> str | None:
    """
    Extract an 11-character YouTube video ID.

    Supports:
    - Standard watch URLs
    - Shortened youtu.be URLs
    - YouTube Shorts
    - Embedded videos
    - YouTube Live URLs

    Returns None for invalid or unsupported URLs.
    """
    if not isinstance(video_url, str) or not video_url.strip():
        return None

    url = video_url.strip()

    if "://" not in url:
        url = "https://" + url

    try:
        parsed = urlsplit(url)
        hostname = (parsed.hostname or "").lower()

        if hostname not in YOUTUBE_DOMAINS:
            return None

        video_id = None

        if hostname == "youtu.be":
            video_id = parsed.path.strip("/").split("/")[0]

        else:
            query_params = parse_qs(parsed.query)
            video_id = query_params.get("v", [None])[0]

            if not video_id:
                path_parts = [
                    part for part in parsed.path.split("/") if part
                ]

                if (
                    len(path_parts) >= 2
                    and path_parts[0] in {"shorts", "embed", "live", "v"}
                ):
                    video_id = path_parts[1]

        if video_id and VIDEO_ID_PATTERN.fullmatch(video_id):
            return video_id

        return None

    except (ValueError, IndexError):
        return None
