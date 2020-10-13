import re
from django.shortcuts import render
from youtube_transcript_api import YouTubeTranscriptApi


def get_id_from_url(url_string):
    reg_expression = r"^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*"
    matches = re.findall(reg_expression, url_string)
    if matches and len(matches[0][1]) == 11:
        return matches[0][1]
    raise Exception("Invalid URL string")


def get_timestamps_from_keyword(transcript, keyword):
    timestamps = []
    for chunk in transcript:
        if keyword.lower() in chunk["text"].lower():
            timestamps.append(round(chunk["start"]))
    return timestamps


def convert_timestamp_to_human_readable(timestamp):
    # The timestamp denotes the number of seconds elapsed.
    minutes, seconds = timestamp // 60, timestamp % 60
    return "%s : %s" % (minutes, seconds)


def home(request):
    context = {}
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        keyword = request.POST.get("keyword")

        try:
            video_id = get_id_from_url(video_url)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            timestamps = get_timestamps_from_keyword(transcript, keyword)
        except Exception as e:
            print("Error: %s" % e)

        context["keyword"] = keyword
        context["timestamps"] = list(
            map(convert_timestamp_to_human_readable, timestamps)
        )
        context["video_embed_url"] = "https://www.youtube.com/embed/%s?start=%s" % (
            video_id,
            timestamps[0] if timestamps else 0,
        )

    return render(request, "home.html", context)
