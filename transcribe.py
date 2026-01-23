
# import whisper
# import os

# def audio_to_text(audio_path):
#     try:
#         # Use tiny model for speed
#         model = whisper.load_model("tiny")
#         print(f"Transcribing: {audio_path}")
#         result = model.transcribe(audio_path, fp16=False)
#         return result["text"]
#     except Exception as e:
#         return f"Error in transcription: {str(e)}"
import whisper
import os
import tempfile

def audio_to_text(audio_path):
    try:
        # Check file size
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"Processing {file_size_mb:.1f} MB file...")
        
        # Choose model based on size
        if file_size_mb > 50:
            model_name = "tiny"  # tiny is faster for large files
        else:
            model_name = "small"  # small for better accuracy on smaller files
            
        model = whisper.load_model(model_name)
        
        # For very large files, use chunking
        result = model.transcribe(
            audio_path,
            fp16=False,
            language='en',
            verbose=False,  # Less output
            task='transcribe'
        )
        
        return result["text"]
    except Exception as e:
        return f"Error: {str(e)}"