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

@api_view(["POST"])
def organize_text(request):
    user_input = request.data.get("text", "")
    mode = request.data.get("mode", "").lower().strip()  # example: 'bulleted' or 'paragraph'

    if not user_input:
        return Response({"error": "No text provided"}, status=400)
    if mode not in ["bulleted", "paragraph"]:
        return Response({"error": "Invalid or missing mode. Supported modes: 'bulleted', 'paragraph'."}, status=400)

    if mode == "bulleted":
        prompt = (
            "Organize the following text using **clear headings, subheadings, and bullet points**. "
            "Group related ideas and make the structure easy to scan:\n\n" + user_input
        )
    elif mode == "paragraph":
        prompt = (
            "Organize the following text using **headings and subheadings**, but write the content in "
            "**paragraph form under each section**. Make the structure logical and easy to follow:\n\n" + user_input
        )
    else:
        prompt = f"Organize and format the following text into {mode} format:\n\n{user_input}"  # fallback

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that organizes and formats unstructured text into a clear and readable format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=False
        )

        organized_text = response.choices[0].message.content
        return Response({"organized": organized_text})

    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Organization failed: {str(e)}"}, status=500)