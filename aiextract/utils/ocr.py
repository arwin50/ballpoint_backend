from mistralai import Mistral
from dotenv import load_dotenv
import os
from .load_image import load_image

load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

def process_ocr(image_path):
    try:
        base64_url = load_image(image_path)

        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": base64_url,
            },
        )
        print(ocr_response)
        return ocr_response
    except Exception as e:
        return {"error": str(e)}
