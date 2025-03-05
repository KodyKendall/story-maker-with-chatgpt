from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Iterator, AsyncIterator, Union
from dotenv import load_dotenv
import os
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

from typing import Optional, List, Mapping, Any
import asyncio

from openai import AsyncOpenAI
import base64

class BaseAgent(ABC):
    """Base class for implementing agents."""
    
    def __init__(self, name: str, description: str):
        """Initialize the agent with a name and optional description.
        
        Args:
            name: The name of the agent
            description: Optional description of the agent's purpose
        """
        self.name = name
        self.description = description

        load_dotenv()

        self.gpt_4o_client = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
            temperature=0.5,
            max_completion_tokens=16384
        )

        self.o3_client = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="o3-mini-2025-01-31",
            temperature=1.0,
            max_completion_tokens=65536
        )
        
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """Abstract run method that all agents must implement."""
        pass

    # Helper for o3_mini 2025-01-31
    async def get_o3_mini_response(self, prompt) -> str:
        """Get a single response from O3 mini."""
        try:
            response = await self.o3_client.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"Error in get_o3_mini_response: {str(e)}")
            raise

    async def get_o3_mini_response_stream(self, prompt, stream: bool = True) -> AsyncIterator[str]:
        """Stream responses from O3 mini."""
        try:
            async for chunk in self.o3_client.astream(prompt):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            self.logger.error(f"Error in get_o3_mini_response_stream: {str(e)}")
            raise

    async def send_image_to_claude_vision(self, image_data: str, image_media_type: str, prompt: str = "") -> str:
        """Send an image to Claude Vision and get response."""
        try:
            # Prepare the image as a Data URL
            data_url = f"data:{image_media_type};base64,{image_data}"

            # Create the message content
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                },
            ]

            # Create the HumanMessage
            message = HumanMessage(content=content)

            # Send the message and await the response
            response = await self.claude_client.ainvoke([message])

            # Get the response content (no need to await here since it's not a coroutine)
            response_text = response.content
            self.logger.info(response_text)
            return response_text
        except Exception as e:
            self.logger.error(f"Error in send_image_to_claude_vision: {str(e)}")
            raise

    async def generate_image(self, prompt: str) -> str:
        """Generate an image using O3."""
        try:
            response = await self.o3_client.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"Error in generate_image: {str(e)}")
            raise

    async def o1_vision_from_url(self, prompt: str, url: str) -> str:
        """Process an image URL with O1 Vision."""
        try:
            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model="o1",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": url}
                ]}]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error in o1_vision_from_url: {str(e)}")
            raise

    async def o1_vision_from_image_path(self, prompt, image_path):
        client = AsyncOpenAI()

        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        # Getting the Base64 string
        base64_image = encode_image(image_path)

        response = await client.chat.completions.create(
            model="o1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )

        llm_response = response.choices[0]
        print(response.choices[0])
        llm_response_content = llm_response.message.content

        # response = await self.o1_client.ainvoke(prompt)
        return llm_response_content