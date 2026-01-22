import whisper_timestamped as whisper
import os

def audio_to_text(audio_path):
    try:
        # Tiny model (smallest)
        model = whisper.load_model("tiny")
        
        # Transcribe
        result = whisper.transcribe(model, audio_path, verbose=False)
        
        return result["text"]
    except Exception as e:
        return f"Sample transcript for demo. Error: {str(e)[:50]}"
