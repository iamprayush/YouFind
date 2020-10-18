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
    return "%s:%s" % (str(minutes).rjust(2, "0"), str(seconds).rjust(2, "0"))


def clean_error(error):
    try:
        clean_error = error.CAUSE_MESSAGE
    except AttributeError:
        clean_error = "Invalid Youtube URL"
    return "Error: %s" % clean_error


def home(request):
    context = {}
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        keyword = request.POST.get("keyword")

        try:
            video_id = get_id_from_url(video_url)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            timestamps = get_timestamps_from_keyword(transcript, keyword)
        except Exception as error:
            context["error_message"] = clean_error(error)
            return render(request, "home.html", context)

        context["video_id"] = video_id
        context["keyword"] = keyword
        context["timestamps"] = list(
            map(convert_timestamp_to_human_readable, timestamps)
        )
        context["video_embed_url"] = "https://www.youtube.com/embed/%s?start=%s" % (
            video_id,
            timestamps[0] if timestamps else 0,
        )

    return render(request, "home.html", context)
