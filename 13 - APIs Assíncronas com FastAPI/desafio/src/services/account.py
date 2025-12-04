from typing import Sequence
from databases.interfaces import Record
from src.database import database
from src.models.account import accounts
from src.schemas.account import AccountIn, AccountOut


class AccountService:
    async def read_all(self, limit: int, skip: int = 0) -> Sequence[AccountOut]:
        query = accounts.select().limit(limit).offset(skip)
        records = await database.fetch_all(query)
        return [AccountOut.model_validate(r) for r in records]

    async def create(self, account: AccountIn) -> AccountOut:
        command = (
            accounts.insert()
            .values(user_id=account.user_id, balance=account.balance)
            .returning(accounts)
        )
        record = await database.fetch_one(command)
        return AccountOut.model_validate(record)
