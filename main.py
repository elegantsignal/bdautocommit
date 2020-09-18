import asyncio
import os

from aiopg.sa import Engine
from aiopg.sa import SAConnection
from aiopg.sa import create_engine
from dotenv import load_dotenv


def aiopg_autocommit(func):
    async def wrapper(*args, **kwargs):
        self = args[0]  # non-obvious, important
        args = args[1:]
        async with Context.engine.acquire() as connection:
            return await func(self, connection, *args, **kwargs)

    return wrapper


def aiopg_transaction(func):
    async def wrapper(*args, **kwargs):
        self = args[0]
        args = args[1:]
        async with Context.engine.acquire() as connection:
            async with connection.begin():
                return await func(self, connection, *args, **kwargs)

    return wrapper


class Context:
    engine: Engine

    @classmethod
    async def setup(cls):
        cls.engine = await create_engine(
            host=os.getenv("POSTGRES_HOST"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DATABASE"),
        )


class Account:
    def __init__(self, name):
        self.name = name


class AccountRepository:
    async def save(self, connection: SAConnection, account: Account):  # noqa: Method 'save' may be 'static'
        query = f"INSERT INTO account (name) VALUES ('{account.name}')"
        await connection.execute(query)

    @staticmethod  # also work
    async def static_save(connection: SAConnection, account: Account):
        query = f"INSERT INTO account (name) VALUES ('{account.name}')"
        await connection.execute(query)


class AccountService:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    @aiopg_autocommit
    async def autocommit_save(self, connection: SAConnection, account: Account):
        await self.repository.save(connection, account)

    @aiopg_transaction
    async def rollback_save(self, connection: SAConnection, account: Account):
        await self.repository.save(connection, account)
        raise Exception("RollbackException")


async def main():
    await Context.setup()
    account_repository = AccountRepository()
    account_service = AccountService(account_repository)

    await account_service.autocommit_save(Account("Alice"))

    try:
        await account_service.rollback_save(Account("Rollback"))
    except Exception as e:
        print(e)

    Context.engine.close()
    await Context.engine.wait_closed()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
