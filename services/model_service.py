import os
from typing import Optional, List
from sagemaker.predictor import Predictor
from sagemaker import Session
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from models.ai_message import AIMessage as CustomAIMessage
import re


class ModelService:
    def __init__(self):
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        self.region_name = os.getenv("AWS_REGION")
        self.endpoint_url = os.getenv("SAGEMAKER_ENDPOINT_URL")

        # Predictor configuration
        self.predictor = Predictor(
            endpoint_name=self.sagemaker_endpoint,
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer(),
        )

        # Create a dictionary to hold memory for each session
        self.session_memory = {}

    def get_memory(self, property_id: str) -> ConversationBufferMemory:
        if property_id not in self.session_memory:
            self.session_memory[property_id] = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
        return self.session_memory[property_id]

    def convert_to_custom_ai_messages(
        self, messages: List[HumanMessage | AIMessage]
    ) -> List[CustomAIMessage]:
        return [
            CustomAIMessage(
                role="user" if isinstance(msg, HumanMessage) else "assistant",
                content=msg.content,
            )
            for msg in messages
        ]

    def query_model(self, property_id: str, prompt: str, max_new_tokens: int = 2048):
        try:
            memory = self.get_memory(property_id)

            # Initialize conversation history if it doesn't exist
            chat_history = memory.chat_memory.messages
            if not chat_history:
                initial_system_message = HumanMessage(
                    content="You are a helpful assistant named amastay. You help with answering questions about short term rentals. and other general information"
                )
                initial_assistant_message = AIMessage(
                    content="Hello! Im Amastay here to help you."
                )
                memory.chat_memory.add_message(initial_system_message)
                memory.chat_memory.add_message(initial_assistant_message)

            # Convert chat history to CustomAIMessage format
            custom_messages = self.convert_to_custom_ai_messages(chat_history)

            # Add the new user prompt
            custom_messages.append(CustomAIMessage(role="user", content=prompt))
            print(custom_messages)

            # Prepare payload for the model
            payload = {
                "messages": [msg.dict() for msg in custom_messages],
                "max_new_tokens": max_new_tokens,
            }
            print(f"Payload for session {property_id}: {payload}")

            # Query the model
            response = self.predictor.predict(payload)

            # Extract and clean the response from the model
            cleaned_response = self.clean_text(
                response["choices"][0]["message"]["content"]
            )

            # Save the user's input and assistant's response to memory
            memory.chat_memory.add_message(HumanMessage(content=prompt))
            memory.chat_memory.add_message(AIMessage(content=cleaned_response))

            return cleaned_response

        except Exception as e:
            print(f"Error querying model: {str(e)}")
            return (
                "I apologize, but I encountered an error while processing your request."
            )

    @staticmethod
    def clean_text(text):
        # Remove Markdown formatting
        text = re.sub(r"\*\*|__", "", text)

        # Remove bullet points and numbering
        text = re.sub(r"^\s*[\d*-]\s*", "", text, flags=re.MULTILINE)

        # Remove quotes and parentheses
        text = re.sub(r"[\"\'()]", "", text)

        # Remove backslashes
        text = text.replace("\\n", " ")

        # Remove extra whitespace and double spaces
        text = re.sub(r"\s+", " ", text).strip()

        # Remove period with two spaces followed by another period
        text = re.sub(r"\. {2}\.", ".", text)

        return text
