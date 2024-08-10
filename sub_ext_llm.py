import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from openai import OpenAI
from dotenv import load_dotenv

# Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    return None

def time_to_seconds(time_str):
    """Convert time string (mm:ss) to seconds."""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except ValueError:
        raise ValueError("Invalid time format. Please use mm:ss (e.g., '1:30' or '01:30').")

def get_full_transcript(video_id):
    """Get the full transcript of the video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([item['text'] for item in transcript])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def get_subtitles_in_range(transcript, timestamp, range_seconds=2):
    """Get subtitles within a range of the specified timestamp."""
    start_time = max(0, timestamp - range_seconds)
    end_time = timestamp + range_seconds

    relevant_subtitles = []
    for subtitle in transcript:
        if start_time <= subtitle['start'] + subtitle['duration'] and subtitle['start'] <= end_time:
            relevant_subtitles.append(subtitle['text'])

    return ' '.join(relevant_subtitles)

def analyze_with_openai(full_transcript, timestamp_transcript):
    """Analyze the transcripts using OpenAI's API."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes video transcripts."},
                {"role": "user", "content": f"Here's the full transcript of a video:\n\n{full_transcript}\n\nAnd here's a specific part of the transcript:\n\n{timestamp_transcript}\n\nPlease analyze what this specific part means in the context of the entire video. Provide a concise summary and any relevant insights."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in OpenAI API call: {str(e)}"

def analyze_youtube_transcript(url, time_str):
    """Main function to analyze YouTube transcript."""
    video_id = extract_video_id(url)
    if not video_id:
        return "Invalid YouTube URL"

    try:
        timestamp = time_to_seconds(time_str)
        full_transcript = get_full_transcript(video_id)
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        timestamp_transcript = get_subtitles_in_range(transcript_data, timestamp)
        
        analysis = analyze_with_openai(full_transcript, timestamp_transcript)
        return analysis
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
#url = "https://www.youtube.com/watch?v=CO3V3e31LJA"
#time_str = "0:29"  # 15 seconds into the video

url = input("\nEnter the youtube video url:")
time_str = input("\nEnter the timestamp in the video in the format mm:ss or m:ss : ")
result = analyze_youtube_transcript(url, time_str)
print(f"Analysis for timestamp {time_str}:\n{result}")