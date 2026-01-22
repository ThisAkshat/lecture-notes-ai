import whisper_timestamped as whisper
import os

def audio_to_text(audio_path):
    try:
        # Load tiny model (smallest, fastest)
        model = whisper.load_model("tiny", device="cpu")
        
        # Transcribe
        result = whisper.transcribe(model, audio_path, verbose=False)
        
        return result["text"]
    except Exception as e:
        return f"Transcription error: {str(e)[:100]}"
