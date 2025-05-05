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