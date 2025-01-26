import os
import asyncio
import requests
from PIL import Image
from time import sleep
from dotenv import get_key
from random import randint

# Function to open and display images based on a given prompt.
def open_images(prompt):
    folder_path = r"Data"   # Folder where the images get stored
    prompt = prompt.replace(" ","_")    # Replace spaces in prompt with underscores.

    # Generate the filenames for the image.
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        # print(image_path)
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {prompt}")
            img.show()
            sleep(1)    # Pause for 1 second before showing the next image

        except IOError:
            print(f"Unable to open {image_path}")

# API details for the Hugging face stable diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env','HuggingFaceAPIKey')}"}

# Async function to generate images based on the given prompt
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        return response.content
    except Exception as e:
        print( f"API Error: {e}")
        return None

# Async function to generate image based on the given content
async def generate_images(prompt: str):
    tasks = []

    # Create 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ','_')}{i + 1}.jpg", 'wb') as f:
            f.write(image_bytes)


# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt)) # Run the async image generation
    open_images(prompt) # open the generated images

# Main loop to monitor for image generation requests
while True:
    try:
        # Read the status and prompt from the data file.
        with open(r"Frontend\Files\ImageGeneration.data",'r') as f:
            Data: str = f.read()
            
        
        Prompt, Status = Data.split(",")

        # If the status indicates an image generation request
        if Status == 'True':
            print("Generating Image.....")
            ImageStatus = GenerateImages(prompt=Prompt)

            # Reset the status in the file after generating images
            with open(r"Frontend\Files\ImageGeneration.data",'w') as f:
                f.write("False,False")
                break # Exit the loop after processing the request
        else:
            sleep(1) # Wait for 1 second before checking again.
    
    except:
        pass