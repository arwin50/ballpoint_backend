import base64
import mimetypes

def load_image(image_path):
  mime_type, _ = mimetypes.guess_type(image_path)
  with open(image_path, "rb") as image_file:
    image_data = image_file.read()
  base64_encoded = base64.b64encode(image_data).decode('utf-8')
  base64_url = f"data:{mime_type};base64,{base64_encoded}"
  return base64_url