import os
from openai import OpenAI
from dotenv import load_dotenv
import json

class ImageGenerator:
    def __init__(self, api_key=None):
        load_dotenv()
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate_image(self, prompt, size="1024x1024", quality="hd", n=1):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        return response.data[0].url

# def main():


if __name__ == "__main__":
    # main()
    generator = ImageGenerator()
    
    #Load a JSON file with the following JSON output
    # {
    # "images": [
    #   {
    #     "chunkIndex": 1,
    #     "title": "Introduction: Harsh Realities of Jamestown",
    #     "description": "An aged parchment letter set against a faded map of early Virginia. The image conveys a grim, historical tone that hints at the brutal survival struggles and hardships faced by the early settlers.",
    #     "style": "Antique, textured, sepia-toned"
    #   },
    
    input_file_path = "Edward_Robert/images/ch_1_images.json"
    output_file_path = "Edward_Robert/images/ch_1_images_with_urls.json"
    json_input = json.load(open(input_file_path))
    images = []
    
    for image in json_input["images"]:
        prompt = image["description"]
        image_url = generator.generate_image(prompt)
        print(image_url)
        image["image_url"] = image_url
        images.append(image)
        
    json.dump(images, open(output_file_path, "w"))
