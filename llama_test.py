#%%
import os
api_key = os.getenv("LLAMA_API_KEY")
if not api_key:
    raise ValueError("LLAMA_API_KEY environment variable not set")

#%%
from llama_api_client import LlamaAPIClient
client = LlamaAPIClient()

#%%
models = client.models.list()
for model in models:
    print(model.id)

#%% encode image
from PIL import Image
import matplotlib.pyplot as plt
import base64

def display_local_image(image_path):
    img = Image.open(image_path)
    plt.figure(figsize=(5,4), dpi=200)
    plt.imshow(img)
    plt.axis('off')
    plt.show()


def encode_image(image_path):
  with open(image_path, "rb") as img:
    return base64.b64encode(img.read()).decode('utf-8')
  
display_local_image("image.png")
base64_image = encode_image("image.png")

# %%
response = client.chat.completions.create(
    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "this is a page from a manga, tell me what is happening in the image",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ],
        },
    ],
)
print(response.completion_message.content.text)

# %%
