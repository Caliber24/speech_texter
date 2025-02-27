import assemblyai as aai
from django.core.exceptions import ValidationError

def transcribe_audio(file_path):
    try:
        transcriber = aai.Transcriber()
        print(transcriber)
        transcript = transcriber.transcribe(file_path)
        print(transcript.text)
        return transcript.text
    except Exception as e:
        print(f"Error during audio-to-text conversion: {e}")
        raise ValidationError(e)