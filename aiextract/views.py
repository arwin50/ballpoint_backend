import os
import whisper
import traceback
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils.ocr import process_ocr
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

@api_view(["POST"])
def extract_text(request):
    if "image" not in request.FILES:
        return Response({"error": "No image file provided"}, status=400)
    
    image_file = request.FILES["image"]
    temp_path = default_storage.save(f"temp/{image_file.name}", ContentFile(image_file.read()))
    temp_full_path = default_storage.path(temp_path)

    try:
        ocr_result = process_ocr(temp_full_path)
        extracted_text = "\n".join(page.markdown for page in ocr_result.pages)
    except Exception as e:
        return Response({"error": f"OCR processing failed: {str(e)}"}, status=500)

    return Response({"text": extracted_text}, status=200)


@api_view(["POST"])
def summarize_text(request):
    user_input = request.data.get("text", "")
    if not user_input:
        return Response({"error": "No text provided"}, status=400)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize this: {user_input}"},
        ],
        stream=False
    )

    summary = response.choices[0].message.content
    return Response({"summary": summary})

class WhisperTranscribeView(APIView):
     def post(self, request):
         try:
             print("FILES:", request.FILES)
             audio_file = request.FILES.get("audio") or request.FILES.get("file")  # fallback if key is "file"
 
             if not audio_file:
                 return Response({"error": "No audio file provided"}, status=status.HTTP_400_BAD_REQUEST)
 
             temp_dir = "temp_uploads"
             os.makedirs(temp_dir, exist_ok=True)
 
             temp_filename = os.path.join(temp_dir, f"temp_{audio_file.name}")
 
             with open(temp_filename, "wb+") as f:
                 for chunk in audio_file.chunks():
                     f.write(chunk)
 
             print(f"Saved audio to: {temp_filename}")
 
             model = whisper.load_model("base")  # You can change this to "tiny", etc. for faster speed
             result = model.transcribe(temp_filename)
             transcript = result["text"]
 
             return Response({"transcript": transcript})
 
         except Exception as e:
             import traceback
             traceback.print_exc()
             return Response({"error": f"Exception occurred: {str(e)}"}, status=500)
 
         finally:
             if os.path.exists(temp_filename):
                 os.remove(temp_filename)