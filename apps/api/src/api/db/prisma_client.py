from db.client import Prisma
from functools import lru_cache

from typing import Optional
from contextlib import asynccontextmanager
from typing import AsyncGenerator

_prisma_client: Optional[Prisma] = None


@lru_cache()
def get_prisma_client() -> Prisma:
    """
    Get a singleton instance of the Prisma client.
    Uses LRU cache to ensure only one instance is created.

    Returns:
        Prisma: A singleton instance of the Prisma client
    """
    global _prisma_client
    if _prisma_client is None:
        _prisma_client = Prisma()
    return _prisma_client


@asynccontextmanager
async def get_prisma_connection() -> AsyncGenerator[Prisma, None]:
    """
    Context manager for handling Prisma client connections.
    Ensures proper connection/disconnection lifecycle.

    Yields:
        Prisma: A connected Prisma client instance
    """
    client = get_prisma_client()
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()
