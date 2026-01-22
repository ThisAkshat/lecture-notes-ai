import whisper_timestamped as whisper
import os

def audio_to_text(audio_path):
    try:
        # Load model
        model = whisper.load_model("tiny")
        
        # Transcribe
        result = whisper.transcribe(model, audio_path)
        
        # Extract text
        text = result["text"]
        return text
    except Exception as e:
        return f"Error in transcription: {str(e)}"
