import re

def extract_channel_name(channel_url):
    """
    Extracts the channel name from a YouTube channel URL.
    
    Args:
        channel_url (str): The YouTube channel URL.
    Returns:
        str: The channel name, or None if the URL is invalid.
    """
    # Match channel URLs like:
    # - https://www.youtube.com/@ChannelName
    # - https://www.youtube.com/c/ChannelName
    # - https://www.youtube.com/channel/ChannelID
    match = re.match(r"https?://(?:www\.)?youtube\.com/(?:@|c/|channel/)([a-zA-Z0-9_-]+)", channel_url)
    if match:
        return match.group(1)
    return None