import streamlit as st
from pytube import YouTube
import os
from pydub import AudioSegment

def dark_mode():
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        .sidebar .sidebar-content {
            background-color: #262730;
            color: #ffffff;
        }
        .stButton > button {
            background-color: #262730;
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            background-color: #333333;
            color: #ffffff;
        }
        .stSelectbox > div > div {
            background-color: #333333;
            color: #ffffff;
        }
        .stSelectbox > div > div > div {
            color: #ffffff;
        }
        .stTextInput > label, .stSelectbox > label {
            color: #ffffff;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #ffffff;
        }
        .css-145kmo2, .css-1v0mbdj, .css-1xarl3l, .css-18ni7ap {
            color: #ffffff;
        }
        .stProgress > div > div > div > div {
            background-color: #262730;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def light_mode():
    st.markdown(
        """
        <style>
        body {
            background-color: #ffffff;
            color: #000000;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .stButton > button {
            background-color: #f0f2f6;
            color: #000000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100
    st.session_state.progress = percentage_completed

def download_video():
    url = st.session_state.url
    resolution = st.session_state.resolution
    st.session_state.progress = 0
    st.session_state.status = "Downloading..."
    try:
        yt = YouTube(url, on_progress_callback=on_progress)  
        stream = yt.streams.filter(res=resolution).first()  
        download_path = os.path.join(st.session_state.download_path, f"{yt.title}.mp4") 
        stream.download(output_path=st.session_state.download_path)
        st.session_state.status = "Downloaded!" 
    except Exception as e:
        st.session_state.status = f"Error:{str(e)}"

AudioSegment.converter = "ffmpeg"
def download_audio():
    url = st.session_state.url
    st.session_state.progress = 0
    st.session_state.status = "Downloading..."
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(output_path=st.session_state.download_path) 
        base, ext = os.path.splitext(audio_file)
        mp3_file = os.path.join(st.session_state.download_path, f"{yt.title}.mp3") 
        AudioSegment.from_file(audio_file).export(mp3_file, format="mp3")
        os.remove(audio_file)  # Remove the original file to keep only the MP3
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
# if 'file_types' not in st.session_state:
#     st.session_state.file_types=""

st.title("Youtube Downloader")

is_dark_mode = st.sidebar.checkbox("Dark mode")
if is_dark_mode:
    dark_mode()
else:
    light_mode()

col1,col2 = st.columns([3,2])

with col1:
    link = st.text_input("Enter the YouTube URL here:", key='url')

    sub_col1,sub_col2,sub_col3 = st.columns([2,1.2,1.2])

    with sub_col1:
        download_path = st.text_input("Enter the download path:", value=os.path.expanduser("~"), key='download_path') 

    file_type = ["mp4","mp3"]
    with sub_col2:
        selected_file_types = st.selectbox("Select file type:", file_type, key='file_type')

    resolutions = ["720p","360p","240p"]
    with sub_col3:
        if selected_file_types == "mp4":
            st.selectbox("Select resolution:", resolutions, key='resolution')

    if st.button("Download"):
        if link:
            if selected_file_types == 'mp4':
                download_video()
            else:
                mp3_file = download_audio()
                if mp3_file:
                    with open(mp3_file, "rb") as file:
                        btn = st.download_button(
                            label="Download MP3",
                            data=file,
                            file_name=os.path.basename(mp3_file),
                            mime="audio/mp3"
                        )
        else:
            st.error("Please enter a YouTube URL")

        
    st.progress(st.session_state.progress/100)
    st.text(st.session_state.status)

