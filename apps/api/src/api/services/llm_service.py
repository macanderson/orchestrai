from typing import List, Dict, Any
import os
import logging
from openai import OpenAI
from api.core.config import settings


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

    async def generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate a response using the LLM"""
        logger.info(f"Generating response for query: {query}")

        # Format context for the prompt
        formatted_context = self._format_context(context_chunks)

        # Build conversation history
        messages = self._build_messages(
            query, formatted_context, conversation_history
        )

        try:
            # Generate completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=1000
            )

            # Extract the response content
            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "sources": [
                    {
                        "id": chunk["id"],
                        "content": (
                            chunk["content"][:200] + "..."
                            if len(chunk["content"]) > 200
                            else chunk["content"]
                        ),
                        "metadata": chunk["metadata"],
                        "document_title": chunk["document_title"]
                    }
                    for chunk in context_chunks
                ]
            }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": """
                    I'm sorry, I encountered an error while generating
                    a response. Please try again later. If the problem
                    persists, please contact support.
                """,
                "sources": []
            }

    def _format_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Format context chunks for the prompt"""
        formatted_chunks = []

        for i, chunk in enumerate(context_chunks):
            source = chunk["metadata"].get("source", "Unknown source")
            formatted_chunk = f"[{i+1}] Source: {source}\n{chunk['content']}\n"
            formatted_chunks.append(formatted_chunk)

        return "\n".join(formatted_chunks)

    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """Build messages for the chat completion API"""

        # Standard system prompt for the RAG system
        system_prompt = f"""
        You are a helpful AI assistant that answers questions
        based on the provided context.

        When answering:
        1.  Only use information from the provided context.
        2.  If the context doesn't contain the answer, say "I don't
            have enough information to answer that question" instead
            of making up an answer.
        3.  Keep answers concise and to the point.
        4.  If appropriate, cite the source of your information
            using [1], [2], etc. corresponding to the sources in the context.
        5.  Maintain a professional and helpful tone.

        Context information is below:
        {context}

        Remember, your goal is to provide accurate information based
        solely on the context provided."""

        # Start with the system prompt
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history)

        # Add the user query
        messages.append({"role": "user", "content": query})

        return messages
