from typing import List, Dict, Any
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, CSVLoader, TextLoader
)
# from langchain.document_loaders.html import BSHTMLLoader
from sentence_transformers import SentenceTransformer
import os
import asyncio
import aiohttp
import logging
from api.core.config import settings
from api.db.prisma_client import get_prisma_client
import time

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    DocumentProcessor is a class that processes documents and
    creates embeddings for them.
    """

    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        self.prisma = get_prisma_client()

    async def process_url(
        self,
        url: str,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process a document from a URL"""
        logger.info(f"Processing URL: {url}")

        # Create document record first
        document = await self.prisma.document.create({
            "data": {
                "title": url,
                "description": f"Content from {url}",
                "project_id": project_id,
                "source_url": url,
                "content_type": "text/html",
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "created_by": user_id,
                "updated_by": user_id,
            }
        })

        # Start crawling and processing in the background
        asyncio.create_task(
            self._process_url_async(url, document.id, user_id)
        )

        return {
            "id": document.id,
            "title": document.title,
            "status": "processing",
        }

    async def _process_url_async(
        self,
        url: str,
        document_id: str,
        user_id: str
    ):
        """Asynchronously process URL content"""
        try:
            # Fetch URL content
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(
                            f"""
                            Failed to fetch URL: {url},
                            status: {response.status}
                            """
                        )
                        return

                    html_content = await response.text()

            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title = soup.title.text if soup.title else url

            # Update document title
            await self.prisma.document.update(
                where={"id": document_id},
                data={
                    "title": title,
                    "updated_at": int(time.time()),
                    "updated_by": user_id,
                }
            )

            # Extract and clean text content
            text_content = self._extract_text_from_html(soup)

            # Split text into chunks
            chunks = self.text_splitter.split_text(text_content)

            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Create metadata
                metadata = {
                    "source": url,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }

                # Generate embedding
                embedding = self.embedding_model.encode(chunk).tolist()

                # Store in database
                await self.prisma.document_chunk.create({
                    "data": {
                        "document_id": document_id,
                        "content": chunk,
                        "metadata": metadata,
                        "embedding": embedding,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time()),
                        "created_by": user_id,
                        "updated_by": user_id,
                    }
                })

            logger.info(
                f"""
                Successfully processed URL: {url}, document_id: {document_id}
                """
            )

        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")

    def _extract_text_from_html(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()

        # Get text
        text = soup.get_text(separator='\n')

        # Normalize whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (
            phrase.strip() for line in lines for phrase in line.split("  ")
        )
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    async def process_file(
        self, file_path: str, file_type: str, project_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Process a document from a file"""
        logger.info(f"Processing file: {file_path}, type: {file_type}")

        file_name = os.path.basename(file_path)

        # Create document record first
        document = await self.prisma.document.create({
            "data": {
                "title": file_name,
                "description": f"Content from {file_name}",
                "project_id": project_id,
                "file_path": file_path,
                "content_type": file_type,
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "created_by": user_id,
                "updated_by": user_id,
            }
        })

        # Start processing in the background
        asyncio.create_task(
            self._process_file_async(
                file_path,
                file_type,
                document.id,
                user_id
            )
        )

        return {
            "id": document.id,
            "title": document.title,
            "status": "processing",
        }

    async def _process_file_async(
        self, file_path: str, file_type: str, document_id: str, user_id: str
    ):
        """Asynchronously process file content"""
        try:
            # Load document based on file type
            if file_type == 'application/pdf':
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                raw_text = " ".join([doc.page_content for doc in docs])
            elif file_type == 'text/csv':
                loader = CSVLoader(file_path)
                docs = loader.load()
                raw_text = " ".join([doc.page_content for doc in docs])
            elif file_type in ['text/plain', 'text/markdown']:
                loader = TextLoader(file_path)
                docs = loader.load()
                raw_text = docs[0].page_content
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            # Split text into chunks
            chunks = self.text_splitter.split_text(raw_text)

            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Create metadata
                metadata = {
                    "source": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }

                # Generate embedding
                embedding = self.embedding_model.encode(chunk).tolist()

                # Store in database
                await self.prisma.document_chunk.create({
                    "data": {
                        "document_id": document_id,
                        "content": chunk,
                        "metadata": metadata,
                        "embedding": embedding,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time()),
                        "created_by": user_id,
                        "updated_by": user_id,
                    }
                })

            logger.info(
                f"""
                Successfully processed file: {file_path},
                document_id: {document_id}
                """
            )

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")

    async def process_csv_data(
        self, csv_data: List[Dict[str, Any]], project_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Process crawled data from a CSV"""
        logger.info(f"Processing CSV data with {len(csv_data)} entries")

        # Create document record first
        # TODO: SAVE DOCUMENT TO THE DATABASE
        # TODO: MAKE THIS WORK FOR MULTIPLE DOCUMENTS
        # TODO: MAKE A PYDANTIC MODEL FOR DOCUMENTS WITH MULTIPLE TYPES (PDF, TXT, CSV, DOCX, DOC, PPT, PPTX, XLS, XLSX, RTF, PAGES, KEYNOTE, SHEET, )
        document = await self.prisma.document.create({
            "data": {
                "title": "Crawled Website Data",
                "description": "Content from crawled website data",
                "project_id": project_id,
                "content_type": "text/csv",
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "created_by": user_id,
                "updated_by": user_id,
            }
        })

        # Start processing in the background
        asyncio.create_task(
            self._process_csv_data_async(csv_data, document.id, user_id)
        )

        return {
            "id": document.id,
            "title": document.title,
            "status": "processing",
        }

    async def _process_csv_data_async(
        self, csv_data: List[Dict[str, Any]], document_id: str, user_id: str
    ):
        """Asynchronously process CSV data"""
        try:
            # Process each row from CSV
            for i, row in enumerate(csv_data):
                # Extract text content - prioritize markdown if available
                content = row.get("markdown", "") or row.get("text", "")
                url = row.get("url", "") or row.get("crawl/loadedUrl", "")

                if not content:
                    logger.warning(f"Empty content for row {i}")
                    continue

                # Split text into chunks
                chunks = self.text_splitter.split_text(content)

                # Process each chunk
                for j, chunk in enumerate(chunks):
                    # Create metadata with original URL and
                    # other useful information
                    metadata = {
                        "source": url,
                        "title": row.get("metadata/title", ""),
                        "description": row.get("metadata/description", ""),
                        "chunk_index": j,
                        "total_chunks": len(chunks),
                        "original_row": i
                    }

                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk).tolist()

                    # Store in database
                    await self.prisma.document_chunk.create({
                        "data": {
                            "document_id": document_id,
                            "content": chunk,
                            "metadata": metadata,
                            "embedding": embedding,
                            "created_at": int(time.time()),
                            "updated_at": int(time.time()),
                            "created_by": user_id,
                            "updated_by": user_id,
                        }
                    })

            logger.info(
                f"Successfully processed CSV data, document_id: {document_id}"
            )

        except Exception as e:
            logger.error(f"Error processing CSV data: {str(e)}")
