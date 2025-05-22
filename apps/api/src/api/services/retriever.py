from typing import List, Dict, Any
import logging

import numpy as np
from sentence_transformers.SentenceTransformer import SentenceTransformer

from ..core.config import settings
from ..db.prisma_client import get_prisma_client

logger = logging.getLogger(__name__)


class DocumentRetriever:
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.prisma = get_prisma_client()

    async def retrieve(
        self,
        query: str,
        project_id: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for a query"""
        logger.info(f"Retrieving documents for query: {query}")

        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query).tolist()

        # Get all documents for the project
        documents = await self.prisma.document.find_many(
            where={"project_id": project_id, "deleted_at": None}
        )

        if not documents:
            logger.warning(f"No documents found for project {project_id}")
            return []

        # Get document IDs
        document_ids = [doc.id for doc in documents]

        # Perform vector search in the database
        # Note: This uses pgvector's cosine similarity search
        # The actual SQL would be something like:
        # SELECT * FROM document_chunks
        # WHERE document_id IN (...) AND deleted_at IS NULL
        # ORDER BY embedding <=> [query_embedding] LIMIT [top_k]

        # For simplicity in this prototype, we'll get all chunks
        # and sort in Python. In production, this should use
        # pgvector's cosine similarity directly

        # Get all chunks for these documents
        chunks = await self.prisma.document_chunk.find_many(
            where={"document_id": {"in": document_ids}, "deleted_at": None},
            include={"document": True},
        )

        if not chunks:
            logger.warning(f"No chunks found for documents {document_ids}")
            return []

        # Calculate cosine similarity and rank chunks
        results = []
        for chunk in chunks:
            if chunk.embedding:
                chunk_embedding = chunk.embedding
                # Calculate cosine similarity
                similarity = self._cosine_similarity(
                    query_embedding, chunk_embedding
                )  # noqa: E501

                results.append({"chunk": chunk, "similarity": similarity})

        # Sort by similarity (highest first)
        results = sorted(results, key=lambda x: x["similarity"], reverse=True)

        # Take top-k results
        top_results = results[:top_k]

        # Format the results
        formatted_results = []
        for result in top_results:
            chunk = result["chunk"]
            formatted_results.append(
                {
                    "id": chunk.id,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "similarity": result["similarity"],
                    "document_id": chunk.document_id,
                    "document_title": (
                        chunk.document.title if chunk.document else ""
                    ),  # chunk.document is not always present
                    "source": chunk.metadata.get("source", ""),
                }
            )

        return formatted_results

    def _cosine_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings"""
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)

        # Normalize vectors
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 0

        return np.dot(arr1, arr2) / (norm1 * norm2)
