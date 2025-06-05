from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech
from backend.settings import get_google_credentials
import mimetypes

def upload_to_gcs(local_path, bucket_name, destination_blob_name):
    storage_client = storage.Client(credentials=get_google_credentials())
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_path)
    return f"gs://{bucket_name}/{destination_blob_name}"

def get_encoding_from_filename(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type == "audio/wav":
        return speech.RecognitionConfig.AudioEncoding.LINEAR16
    elif mime_type == "audio/mp3" or filename.endswith(".mp3"):
        return speech.RecognitionConfig.AudioEncoding.MP3
    elif mime_type == "audio/flac" or filename.endswith(".flac"):
        return speech.RecognitionConfig.AudioEncoding.FLAC
    else:
        raise ValueError("Unsupported audio format. Please upload WAV, MP3, or FLAC.")
