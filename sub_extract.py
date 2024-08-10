from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    # If we can't find the ID, return None
    return None

def time_to_seconds(time_str):
    """Convert time string (mm:ss) to seconds."""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except ValueError:
        raise ValueError("Invalid time format. Please use mm:ss (e.g., '1:30' or '01:30').")

def get_subtitles_in_range(url, time_str, range_seconds=3):
    """Get subtitles within a range of the specified timestamp for a YouTube video."""
    video_id = extract_video_id(url)
    if not video_id:
        return "Invalid YouTube URL"

    try:
        timestamp = time_to_seconds(time_str)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

    start_time = max(0, timestamp - range_seconds)
    end_time = timestamp + range_seconds

    relevant_subtitles = []
    for subtitle in transcript:
        if start_time <= subtitle['start'] + subtitle['duration'] and subtitle['start'] <= end_time:
            relevant_subtitles.append(subtitle['text'])

    if not relevant_subtitles:
        return "No subtitles found in the specified range"

    return ' '.join(relevant_subtitles)

# Example usage
url = "https://www.youtube.com/watch?v=69Tzh_0lHJ8"
time_str = "1:18"  # 15 seconds into the video

subtitles = get_subtitles_in_range(url, time_str)
print(f"Subtitles around {time_str} (+/- 3 seconds): {subtitles}")

