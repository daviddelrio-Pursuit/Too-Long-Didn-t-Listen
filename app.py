import streamlit as st
import time
import validators
import openai
import os
import yt_dlp
import requests
import feedparser
from audio_utils import chunk_audio, transcribe_chunks

# Set up OpenAI API key
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("Please set OPENAI_API_KEY in your Streamlit secrets")
    st.stop()

def download_youtube_audio(url):
    """Download audio from YouTube URL using yt-dlp"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_%(title)s.%(ext)s',
            'extractaudio': True,
            'audioformat': 'mp3',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Convert to mp3 if needed
            if not filename.endswith('.mp3'):
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            return filename
    except Exception as e:
        st.error(f"Error downloading YouTube audio: {str(e)}")
        return None

def download_podcast_audio(url):
    """Download audio from podcast URL (direct audio file or RSS feed)"""
    try:
        # Check if it's a direct audio file
        if url.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = f"temp_podcast_{int(time.time())}.mp3"
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filename
        
        # If it's an RSS feed, get the latest episode
        elif 'rss' in url.lower() or 'feed' in url.lower():
            feed = feedparser.parse(url)
            if feed.entries:
                # Get the latest episode's audio URL
                latest_episode = feed.entries[0]
                audio_url = None
                
                # Look for audio links in the episode
                for link in latest_episode.links:
                    if link.get('type', '').startswith('audio/'):
                        audio_url = link.href
                        break
                
                if audio_url:
                    return download_podcast_audio(audio_url)  # Recursive call for direct audio
                else:
                    st.error("No audio file found in podcast feed")
                    return None
            else:
                st.error("No episodes found in podcast feed")
                return None
        else:
            st.error("Unsupported podcast URL format")
            return None
            
    except Exception as e:
        st.error(f"Error downloading podcast audio: {str(e)}")
        return None

def download_audio_from_url(url):
    """Determine URL type and download audio accordingly"""
    if 'youtube.com' in url or 'youtu.be' in url:
        return download_youtube_audio(url)
    else:
        return download_podcast_audio(url)

st.set_page_config(layout="centered")

# --- 1. TITLE ---
st.title("🎙️ TLDL (Too Long Didn't Listen) Podcast Summarizer")
st.subheader("Get the insights, skip the filler.")

# --- 2. SIDEBAR FOR INPUT ---
with st.sidebar:
    st.header("Upload Audio or Enter URL")
    
    # Input method selection
    input_method = st.radio("Choose input method:", ["Upload File", "Enter URL"])
    
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload podcast/audio", type=["mp3", "wav", "m4a"])
        audio_url = None
    else:
        audio_url = st.text_input(
            "Paste Podcast or YouTube URL here:",
            placeholder="e.g., https://..." 
        )
        uploaded_file = None
    
    # Simple Slider for Summary Length
    summary_length = st.slider("Target Summary Length (sentences):", 1, 10, 5)

    # Process Button (Trigger)
    if input_method == "Upload File":
        process_button = st.button("Transcribe & Summarize File", type="primary")
    else:
        process_button = st.button("Transcribe & Summarize URL", type="primary")

# --- 3. MAIN CONTENT AREA FOR OUTPUT ---
if process_button:
    # Handle file upload
    if uploaded_file is not None:
        try:
            st.info("🚀 Processing uploaded file... This may take a moment.")
            
            # Save uploaded file temporarily
            temp_file_path = f"temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the audio
            with st.spinner('Chunking audio... Transcribing... Summarizing...'):
                chunk_files = chunk_audio(temp_file_path)
                transcript = transcribe_chunks(chunk_files)
                
                # Generate summary using GPT
                summary_prompt = f"""
                Please create a concise executive summary of the following transcript in exactly {summary_length} key bullet points. 
                Focus on actionable insights and main takeaways. Format each point as a clear, actionable statement.
                
                Transcript: {transcript}
                """
                
                summary_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=500
                )
                summary = summary_response.choices[0].message.content
            
            # Display results
            st.header("✅ Executive Summary (Actionable Insights)")
            st.info(f"Summary optimized for {summary_length} key points.")
            st.markdown("---")
            st.markdown(summary)
            
            # Full transcript in expander
            with st.expander("📄 Full Transcript"):
                st.text(transcript)
            
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            # Clean up on error
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    # Handle URL processing
    elif audio_url:
        is_valid_url = validators.url(audio_url)
        
        if is_valid_url:
            try:
                st.info("🚀 Processing URL... Downloading audio... This may take a moment.")
                
                # Download audio from URL
                with st.spinner('Downloading audio from URL...'):
                    downloaded_file = download_audio_from_url(audio_url)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    st.success("✅ Audio downloaded successfully!")
                    
                    # Process the downloaded audio
                    with st.spinner('Chunking audio... Transcribing... Summarizing...'):
                        chunk_files = chunk_audio(downloaded_file)
                        transcript = transcribe_chunks(chunk_files)
                        
                        # Generate summary using GPT
                        summary_prompt = f"""
                        Please create a concise executive summary of the following transcript in exactly {summary_length} key bullet points. 
                        Focus on actionable insights and main takeaways. Format each point as a clear, actionable statement.
                        
                        Transcript: {transcript}
                        """
                        
                        summary_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": summary_prompt}],
                            max_tokens=500
                        )
                        summary = summary_response.choices[0].message.content
                    
                    # Display results
                    st.header("✅ Executive Summary (Actionable Insights)")
                    st.info(f"Summary optimized for {summary_length} key points.")
                    st.markdown("---")
                    st.markdown(summary)
                    
                    # Full transcript in expander
                    with st.expander("📄 Full Transcript"):
                        st.text(transcript)
                    
                    # Clean up downloaded file
                    try:
                        os.unlink(downloaded_file)
                    except:
                        pass
                else:
                    st.error("Failed to download audio from URL. Please check the URL and try again.")
                    
            except Exception as e:
                st.error(f"Error processing URL: {str(e)}")
        else:
            st.sidebar.error("Please enter a valid URL (e.g., starting with http:// or https://).")
    
    else:
        if input_method == "Upload File":
            st.sidebar.error("Please upload an audio file.")
        else:
            st.sidebar.error("Please paste a URL above.")

# Keep the placeholder audio file accessible
# Make sure 'placeholder_summary.mp3' is in the root of your GitHub repo.