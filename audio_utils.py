# Fix for pydub Python 3.13 compatibility
import sys
import math
import tempfile
import openai
import os

# Import fallback libraries
try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Try to fix pydub import issue
try:
    if sys.version_info >= (3, 13):
        try:
            import pyaudioop
            sys.modules['audioop'] = pyaudioop
        except ImportError:
            pass
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pydub not available ({e}). Using alternative audio processing.")
    PYDUB_AVAILABLE = False

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
        if PYDUB_AVAILABLE:
            # Use pydub for chunking
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
            
        elif LIBROSA_AVAILABLE:
            # Fallback to librosa for chunking
            y, sr = librosa.load(audio_file_path)
            chunk_length_samples = int(chunk_length_ms * sr / 1000)
            total_samples = len(y)
            num_chunks = math.ceil(total_samples / chunk_length_samples)
            chunk_files = []
            
            for i in range(num_chunks):
                start_sample = i * chunk_length_samples
                end_sample = min((i + 1) * chunk_length_samples, total_samples)
                chunk = y[start_sample:end_sample]
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                sf.write(temp_file.name, chunk, sr)
                chunk_files.append(temp_file.name)
                
            return chunk_files
            
        else:
            print("Error: No audio processing library available")
            return []
            
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
