import logging
from typing import Dict

from asyncpg.pool import Pool, create_pool
from marshmallow import Schema, fields, post_load

__all__ = (
    "DB",
    "DBSchema",
)


class DB:
    __slots__ = ("_pool", "_logger")

    def __init__(self, pool: Pool, logger: logging.Logger):
        self._pool = pool
        self._logger = logger

    async def setup(self) -> None:
        await self._pool

    async def cleanup(self) -> None:
        await self._pool.close()

    async def check_health(self) -> bool:
        return await self._pool.fetchval("select $1::bool", True)

    @classmethod
    def from_dict(cls, data: Dict) -> "DB":
        return DBSchema().load(data)


class PoolSchema(Schema):
    dsn = fields.Str(required=True)
    min_size = fields.Int(missing=0)
    max_size = fields.Int(missing=10)
    max_queries = fields.Int(missing=1000)
    max_inactive_connection_lifetime = fields.Float(missing=3600)
    timeout = fields.Float(missing=10)
    command_timeout = fields.Float(missing=10)
    statement_cache_size = fields.Int(missing=1024)
    max_cached_statement_lifetime = fields.Int(missing=3600)

    @post_load
    def make_pool(self, data: Dict, **kwargs) -> Pool:
        return create_pool(**data)


class LoggerSchema(Schema):
    name = fields.Str(required=True)

    @post_load
    def make_logger(self, data: Dict, **kwargs) -> logging.Logger:
        return logging.getLogger(**data)


class DBSchema(Schema):
    pool = fields.Nested(PoolSchema, required=True)
    logger = fields.Nested(LoggerSchema, required=True)

    @post_load
    def make_db(self, data: Dict, **kwargs) -> DB:
        return DB(**data)