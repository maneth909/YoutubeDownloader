import streamlit as st
from pytube import YouTube
import os
from pydub import AudioSegment
from pytube import Playlist
import re

st.set_page_config(layout="wide")

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100
    st.session_state.progress = percentage_completed
    progress_bar.progress(int(percentage_completed))  

def download_video():
    url = st.session_state.url
    resolution = st.session_state.resolution
    st.session_state.progress = 0
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolution).first()
        if stream is None:
            st.session_state.status = "No video stream available for the selected resolution."
            return
        download_path = os.path.join(st.session_state.download_path, f"{yt.title}.mp4")
        stream.download(output_path=st.session_state.download_path)
        st.session_state.status = "Downloaded!"
    except Exception as e:
        st.session_state.status = f"Error: {str(e)}"

def download_playlist():
    url = st.session_state.url
    st.session_state.progress = 0
    try:
        playlist = Playlist(url)
        total_videos = len(playlist.video_urls)
        for i, video_url in enumerate(playlist.video_urls, start=1):
            yt = YouTube(video_url, on_progress_callback=on_progress)
            sanitized_title = sanitize_filename(yt.title)
            if st.session_state.file_type == 'mp4':
                stream = yt.streams.filter(res=st.session_state.resolution, file_extension='mp4').first()
                if stream is None:
                    stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
                if stream is None:
                    st.error(f"No video stream available for {yt.title} at the selected resolution.")
                    continue
                download_path = os.path.join(st.session_state.download_path, f"{sanitized_title}.mp4")
                stream.download(output_path=st.session_state.download_path)
            elif st.session_state.file_type == 'mp3':
                audio_stream = yt.streams.filter(only_audio=True).first()
                if audio_stream is None:
                    st.error(f"No audio stream available for {yt.title}.")
                    continue
                audio_file = audio_stream.download(output_path=st.session_state.download_path)
                base, ext = os.path.splitext(audio_file)
                mp3_file = os.path.join(st.session_state.download_path, f"{sanitized_title}.mp3")
                
                # Set the ffmpeg and ffprobe paths for pydub
                AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"  # Example path for ffmpeg
                AudioSegment.ffprobe = "/usr/local/bin/ffprobe"  # Example path for ffprobe

                AudioSegment.from_file(audio_file).export(mp3_file, format="mp3")
                os.remove(audio_file)
                st.session_state.status = f"Downloaded MP3: {mp3_file}"
        st.session_state.progress = (i / total_videos) * 100
    except Exception as e:
        st.session_state.status = f"Error: {str(e)}"


def get_playlist_info(url):
    try:
        playlist = Playlist(url)
        videos_info = []
        for video_url in playlist.video_urls:
            yt = YouTube(video_url)
            video_info = {
                "title": yt.title,
                "video_id": yt.video_id,
                "author": yt.author,
                "length": yt.length,
            }
            videos_info.append(video_info)
        return videos_info
    except Exception as e:
        st.error(f"Failed to retrieve playlist information: {str(e)}")
        return []

def download_audio():
    url = st.session_state.url
    st.session_state.progress = 0
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(output_path=st.session_state.download_path)
        base, ext = os.path.splitext(audio_file)
        sanitized_title = sanitize_filename(yt.title)
        mp3_file = os.path.join(st.session_state.download_path, f"{sanitized_title}.mp3")
        
        # Set the ffmpeg and ffprobe paths for pydub
        AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"  # Example path for ffmpeg
        AudioSegment.ffprobe = "/usr/local/bin/ffprobe"  # Example path for ffprobe

        AudioSegment.from_file(audio_file).export(mp3_file, format="mp3")
        os.remove(audio_file)
        st.session_state.status = f"Downloaded MP3: {mp3_file}"
        return mp3_file
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


if 'url' not in st.session_state:
    st.session_state.url=""
if 'resolution' not in st.session_state:
    st.session_state.resolution = "720p"
if 'progress' not in st.session_state:
    st.session_state.progress=0
if 'status' not in st.session_state:
    st.session_state.status=""

# col1, col2, col3, col4, col5 = st.columns([0.5, 6, 0.5, 5, 0.5])
col1, col2, col3, col4, col5 = st.columns([1, 8, 1, 8, 1])


with col2:
    st.title("Youtube Downloader")
    link = st.text_input("Enter the YouTube URL here:", key='url')

    sub_col1, sub_col2, sub_col3 = st.columns([2, 1.2, 1.2])

    with sub_col1:
        #download_path = st.text_input("Enter the download path:", value=os.path.expanduser("~"), key='download_path')
        #download_path = st.text_input("Enter the download path:", value=os.path.join("C:", "Users", os.getlogin(), "Downloads"), key='download_path')
        download_path = st.text_input("Enter the download path:", value=os.path.join(os.path.expanduser("~"), "Downloads"), key='download_path')

    file_type = ["mp4", "mp3"]
    with sub_col2:
        selected_file_types = st.selectbox("File type:", file_type, key='file_type')

    resolutions = ["240", "360", "720p", "1080p", "1440p", "2160p"]
    with sub_col3:
        if selected_file_types == "mp4":
            st.selectbox("Resolution:", resolutions, key='resolution')

    progress_bar = st.progress(0)  # Initialize progress bar

    if st.button("Download"):
        if link:
            if "playlist" in link:
                download_playlist()
                st.success(f"MP4 downloaded successfully")
            else:
                if selected_file_types == 'mp4':
                    download_video()
                    st.success(f"MP4 downloaded successfully")
                else:
                    mp3_file = download_audio()
                    if mp3_file:
                        st.success(f"Audio downloaded successfully: {mp3_file}")
        else:
            st.error("Please enter a YouTube URL")

        st.text(st.session_state.status)

with col4:
    if link:
        if "playlist" in link:
            playlist_info = get_playlist_info(link)
            if playlist_info:
                st.write("### Playlist Preview")
                for video in playlist_info:
                    youtube_embed_url = f"https://www.youtube.com/embed/{video['video_id']}"
                    st.markdown(
                        f"""
                        <iframe width="320" height="180" src="{youtube_embed_url}" frameborder="0" allowfullscreen></iframe>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.write(f"**Title:** {video['title']}")
                    st.write(f"**Author:** {video['author']}")
                    st.write(f"**Length:** {video['length'] // 60} minutes {video['length'] % 60} seconds")
                    st.write("---")
        else:
            video_id = link.split("v=")[1] if "v=" in link else link.split("/")[-1]
            youtube_embed_url = f"https://www.youtube.com/embed/{video_id}"
            st.markdown(
                f"""
                <iframe width="360" height="200" src="{youtube_embed_url}" frameborder="0" allowfullscreen></iframe>
                """,
                unsafe_allow_html=True,
            )
            try:
                yt = YouTube(link)
                a1, a2 = st.columns([1, 1])
                with a1:
                    st.image(yt.thumbnail_url, caption="Thumbnail")
                with a2:
                    st.write(f"**Title:** {yt.title}")
                    st.write(f"**Author:** {yt.author}")
                    st.write(f"**Length:** {yt.length // 60} minutes {yt.length % 60} seconds")
            except Exception as e:
                st.error(f"Failed to retrieve video information: {str(e)}")
