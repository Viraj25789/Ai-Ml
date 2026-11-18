import re

def extract_video_id(video_url: str) -> str:
    """
    Safely extracts the 11-character YouTube Video ID using Regex.
    Works on standard, shortened, embedded, and mobile URLs.
    """
    # This regex pattern finds the exact 11-character ID in any YouTube link
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    
    match = re.search(pattern, video_url)
    
    if match:
        return match.group(1)
    return None

# testing
# video_id = extract_video_id("https://youtu.be/YimMzb0mHkI?si=gE-2TBEThr5ywLDN")
# print(video_id)