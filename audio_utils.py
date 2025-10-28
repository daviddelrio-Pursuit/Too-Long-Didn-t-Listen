from pydub import AudioSegment
import math
import tempfile
import openai
import os

def chunk_audio(audio_file_path, chunk_length_ms=60000):  # e.g., 1 min chunks
    """
    Chunk audio file into smaller segments for processing.
    
    Args:
        audio_file_path (str): Path to the audio file
        chunk_length_ms (int): Length of each chunk in milliseconds (default: 60000 = 1 minute)
    
    Returns:
        list: List of temporary file paths for each chunk
    """
    try:
        audio = AudioSegment.from_file(audio_file_path)
        total_length_ms = len(audio)
        num_chunks = math.ceil(total_length_ms / chunk_length_ms)
        chunk_files = []
        
        for i in range(num_chunks):
            start_time = i * chunk_length_ms
            end_time = min((i + 1) * chunk_length_ms, total_length_ms)
            chunk = audio[start_time:end_time]
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            chunk.export(temp_file.name, format="wav")
            chunk_files.append(temp_file.name)
            
        return chunk_files
    except Exception as e:
        print(f"Error chunking audio: {e}")
        return []

def transcribe_chunks(chunk_files):
    """
    Transcribe audio chunks using OpenAI Whisper API.
    
    Args:
        chunk_files (list): List of audio file paths to transcribe
    
    Returns:
        str: Combined transcript text from all chunks
    """
    transcripts = []
    
    for file_path in chunk_files:
        try:
            with open(file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                transcripts.append(transcript["text"])
        except Exception as e:
            print(f"Error transcribing {file_path}: {e}")
            continue
        finally:
            # Clean up temporary file
            try:
                os.unlink(file_path)
            except:
                pass
    
    return " ".join(transcripts)

# Step 1: Chunk Audio in Python
# Required Libraries:
# - pydub (audio processing)
# - openai (API access) 
# - tempfile (for temporary storage)
