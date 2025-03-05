import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from base_agent import BaseAgent
#Outputs a JSON file that maps content to image descriptions, in order to plan out the images for the story.
class ImagePlanningAgent:
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
    agent = ImagePlanningAgent()
    
    #Load a JSON file with the following JSON output
    # {
    # "images": [
    #   {
    #     "chunkIndex": 1,
    #     "title": "Introduction: Harsh Realities of Jamestown",
    #     "description": "An aged parchment letter set against a faded map of early Virginia. The image conveys a grim, historical tone that hints at the brutal survival struggles and hardships faced by the early settlers.",
    #     "style": "Antique, textured, sepia-toned"
    #   },
    
    chapter_number = 1
    input_file_path = f"90s_Founder_in_SF/images/json/ch_{chapter_number}_images.json"
    output_file_path = f"90s_Founder_in_SF/images/json/ch_{chapter_number}_images_with_urls.json"
    json_input = json.load(open(input_file_path))
    images = []
    
    for image in json_input["images"]:
        prompt = image["description"]
        image_url = agent.generate_image(prompt)
        
        # Create the directory structure if it doesn't exist
        image_dir = os.path.dirname(f"90s_Founder_in_SF/images/raw_images/ch_{chapter_number}_{image['chunkIndex']}.jpg")
        os.makedirs(image_dir, exist_ok=True)
        
        # download the image and save it to the images folder (necessary because the link will eventually expire)
        image_path = f"90s_Founder_in_SF/images/raw_images/ch_{chapter_number}_{image['chunkIndex']}.jpg"
        response = requests.get(image_url)
        with open(image_path, "wb") as f:
            f.write(response.content)

        print(image_path)
        image["image_url"] = image_path
        images.append(image)
        
    json.dump(images, open(output_file_path, "w"))
