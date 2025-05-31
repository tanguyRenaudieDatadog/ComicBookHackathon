#%% 
IMG_PATH="avatar_last_airbender.png"
import os
os.getenv('LLAMA_API_KEY')
# %%
import os
from llama_api_client import LlamaAPIClient
import base64
client = LlamaAPIClient(
    api_key=os.environ.get("LLAMA_API_KEY"),  # This is the default and can be omitted
)

create_chat_completion_response = client.chat.completions.create(
    messages=[
        {
            "content": "string",
            "role": "user",
        }
    ],
    model="Llama-4-Scout-17B-16E-Instruct-FP8",
)
print(create_chat_completion_response.completion_message)
# %%
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
encoded_image = encode_image(IMG_PATH)
response = client.chat.completions.create(
    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract the text boxes from the image",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}",
                    },
                },
            ],
        },
    ],
    stream=True,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "text_extraction_response",
            "schema": {
                "type": "object",
                "properties": {
                    "text_boxes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "The extracted text content"
                                },
                            },
                            "required": ["text"],
                        }
                    }
                },
            }
        }
    }
)

for chunk in response:
    print(chunk.event.delta.text, end="", flush=True)

# %%
