from api.db.prisma_client import (
    get_prisma_client as get_db_client,
    Prisma as PrismaClient,
)

__all__ = [
    "get_db_client",
    "PrismaClient",
]
