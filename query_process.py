import ass_functions as af 

def process_the_query(query):
    if "weather" in query:
        af.get_weather()
        return None
    elif "volume up" in query:
        af.increase_volume()
        return None
    elif "volume down" in query:
        af.decrease_volume()
        return None
    elif "screenshot" in query:
        af.screenshot()
        retun None
    elif "set volume" in query:
        volume=int(query[11:])
        af.set_volume(volume)
        return None
    elif "volume mute" in query:
        af.set_volume(0)
        return None
    elif "volume unmute" in query:
        af.set_volume(100)
        retun None 
    elif "spotify" in query:
        song_name=query[8:]
        af.spotify_search(song_name)
        retun None
    elif "youtube" in query:
        video_name=query[8:]
        af.youtube_search(video_name)
        return None
    elif "web search" in query:
        site_name=query[11:]
        af.web_search(site_name)
        return None
    else:
        af.command_execute(query)

query="screenshot"
process_the_query(query)