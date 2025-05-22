from prisma import Prisma
from functools import lru_cache

@lru_cache()
def get_prisma_client():
    return Prisma()
