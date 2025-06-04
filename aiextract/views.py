import os
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
from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech
import time
from pydub import AudioSegment
from aiextract.utils.google_stt_utils import upload_to_gcs, get_encoding_from_filename

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
             {"role": "system", 
             "content": (
                          "You are a helpful assistant that summarizes text.\n"
                           "Do not include any introductory phrases, explanations, or disclaimers. Respond directly with the summarize output only.\n"
                           "Make sure to include all important details and key points in the summary."
                           "Strictly ensure that the text has limited styles (can be bold, italicized, underlined, no defined font sizes and horizontal breaks), plain text is ideal"
                         )},
            {"role": "user", "content": f"Summarize this: {user_input}"},
        ],
        stream=False
    )

    summary = response.choices[0].message.content
    return Response({"summary": summary})

# @api_view(['POST'])
# def whisper_transcribe(request):
#     try:
#         print("FILES:", request.FILES)
#         audio_file = request.FILES.get("audio") or request.FILES.get("file")  # fallback if key is "file"
 
#         if not audio_file:
#             return Response({"error": "No audio file provided"}, status=status.HTTP_400_BAD_REQUEST)
 
#         temp_dir = "temp_uploads"
#         os.makedirs(temp_dir, exist_ok=True)
 
#         temp_filename = os.path.join(temp_dir, f"temp_{audio_file.name}")
 
#         with open(temp_filename, "wb+") as f:
#             for chunk in audio_file.chunks():
#                 f.write(chunk)
 
#         print(f"Saved audio to: {temp_filename}")
 
#         model = whisper.load_model("base")  # You can change this to "tiny", etc. for faster speed
#         result = model.transcribe(temp_filename)
#         transcript = result["text"]
 
#         return Response({"transcript": transcript})
 
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return Response({"error": f"Exception occurred: {str(e)}"}, status=500)
 
#     finally:
#         if os.path.exists(temp_filename):
#             os.remove(temp_filename)
                 
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
                    "content": (
                    "You are a helpful assistant that organizes and formats unstructured text into a clear and readable format. "
                    "Do not include any introductory phrases, explanations, or disclaimers. Respond directly with the formatted output only."
                    "Make sure to include all important details and key points in the organized text."
                    "Do not provide a title for the overall organized text. Just the sections."
                    "Strictly ensure that the text has limited styles (can be bold, italicized, underlined, bulleted or number bulleted; no defined font sizes and horizontal breaks)"
                )
                },
              
                {"role": "user", "content": f"Organize this: {prompt}"},
                
            ],
            stream=False
        )

        organized_text = response.choices[0].message.content
        return Response({"organized": organized_text})

    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Organization failed: {str(e)}"}, status=500)
    
@api_view(["POST"])
def complete_text(request):
    selected_text = request.data.get("selected_text", "")
    note_content = request.data.get("note_content", "")

    if not selected_text or not note_content:
        return Response({"error": "Both selectedText and noteContent are required."}, status=400)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": (
                "You are a helpful assistant that completes or clarifies vague or incomplete text. "
                "Use the provided context from the note to make the completion relevant. "
                "You may also use relevant external information if it enhances the clarity or meaning, "
                "but only if it is strongly related to the topic discussed in the note."
                "Provide the final, polished completion or answer only."
                "Avoid unnecessary explanations or disclaimers."
                 "Strictly ensure that the text has limited styles (can be bold, italicized, underlined,  no defined font sizes and horizontal breaks), plain text is ideal"
                
            )},
            {"role": "user", "content": (
                f"The note content is:\n{note_content}\n\n"
                f"The selected vague or incomplete text is:\n\"{selected_text}\"\n\n"
                "Please complete or clarify this text using the note and relevant information."
            )},
        ],
        stream=False
    )

    completed_text = response.choices[0].message.content
    return Response({"completedText": completed_text})

@api_view(["POST"])
def query_text(request):
    selected_text = request.data.get("selected_text", "")
    note_content = request.data.get("note_content", "")
    query = request.data.get("query", "")

    if not selected_text or not note_content or not query:
        return Response({"error": "selectedText, noteContent, and query are all required."}, status=400)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": (
                "You are a helpful assistant. A user is asking a question about a confusing or unclear part of their note. "
                "Use the selected text and the full note content as primary context. "
                "You may include relevant external information, but only if it is directly related to the note's topic."
                "Provide the final, polished completion or answer only."
                "Avoid unnecessary explanations or disclaimers."
                "Limit your response to 3-5 sentences."
                "Strictly ensure that the text has limited styles (can be bold, italicized, underlined, no defined font sizes and horizontal breaks), plain text is ideal"
                
            )},
            {"role": "user", "content": (
                f"Here is the note:\n{note_content}\n\n"
                f"The selected text in question is:\n\"{selected_text}\"\n\n"
                f"The user asks: {query}\n\n"
                "Please provide a clear and helpful explanation or answer based on the context."
            )},
        ],
        stream=False
    )

    answer = response.choices[0].message.content
    return Response({"answer": answer})

@api_view(["POST"])
def async_transcribe(request):
    try:
        audio_file = request.FILES.get("audio") or request.FILES.get("file")
        if not audio_file:
            return Response({"error": "No audio file provided"}, status=400)

        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, audio_file.name)

        with open(temp_path, "wb+") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        
        audio_segment = AudioSegment.from_file(temp_path)
        actual_sample_rate = audio_segment.frame_rate

        converted_path = os.path.join(temp_dir, f"converted_{audio_file.name}")
        sound = AudioSegment.from_file(temp_path)
        sound = sound.set_channels(1) 
        sound = sound.set_frame_rate(16000)
        sound.export(converted_path, format="wav")

        bucket_name = "ballpoint-bucket"
        gcs_uri = upload_to_gcs(converted_path, bucket_name, f"uploads/converted_{audio_file.name}")

        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(uri=gcs_uri)
        try:
            encoding = get_encoding_from_filename(audio_file.name)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)

        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True
        )

        operation = client.long_running_recognize(config=config, audio=audio)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=300)

        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "

        return Response({"transcript": transcript.strip()})

    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Exception occurred: {str(e)}"}, status=500)

    finally:
        for path in [temp_path, converted_path]:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
