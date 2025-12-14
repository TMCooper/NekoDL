from ..core.core import Info

def get_title(info):
    """
    Returns the title of the YouTube video.

    Can be None if the information is missing or extraction failed.
    """
    return Info._get_title(info)

def get_creator(info):
    """
    Returns the name of the creator or uploader of the video.

    yt-dlp may provide this information via different fields depending on the video.
    """
    return Info._get_creator(info)

def get_like_count(info):
    """
    Returns the number of likes for the video.

    Can be None if the data is unavailable.
    """
    return Info._get_like_count(info)

def get_age_limit(info):
    """
    Returns the age restriction for the video (e.g., 18).

    None if no restriction is set.
    """
    return Info._get_age_limit(info)

def get_availability(info):
    """
    Returns the availability status of the video.

    Examples: "public", "private", "unlisted", etc.
    """
    return Info._get_availability(info)

def get_available_at(info):
    """
    Returns the Unix timestamp (in seconds) when the video becomes available.

    None if not defined.
    """
    return Info._get_available_at(info)

def get_comment_count(info):
    """
    Returns the number of comments on the video.

    Can be None if comments are disabled or unavailable.
    """
    return Info._get_comment_count(info)

def get_duration(info):
    """
    Returns the duration of the video in seconds.

    Can be None if the duration is unknown.
    """
    return Info._get_duration(info)

def get_formats(info):
    """
    Returns the list of available formats for the video.

    Each format is a dictionary provided by yt-dlp.
    """
    return Info._get_formats(info)

def get_id(info):
    """
    Returns the unique ID of the YouTube video.
    """
    return Info._get_id(info)

def get_tags(info):
    """
    Returns the tags associated with the video.

    Can be an empty list or None if no tags are defined.
    """
    return Info._get_tags(info)

def get_thumbnail(info):
    """
    Returns the URL of the main thumbnail of the video.
    """
    return Info._get_thumbnail(info)

def get_timestamp(info):
    """
    Returns the Unix timestamp of the video publication.

    None if unknown.
    """
    return Info._get_timestamp(info)

def get_url(info):
    """
    Returns the URL of the YouTube video.
    """
    return Info._get_url(info)