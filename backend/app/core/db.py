"""
Prisma クライアント管理
FastAPI の lifespan で connect / disconnect を行う。
"""

from prisma import Prisma

db = Prisma()


async def connect_db() -> None:
    """アプリ起動時に呼び出す。"""
    await db.connect()


async def disconnect_db() -> None:
    """アプリ終了時に呼び出す。"""
    await db.disconnect()
