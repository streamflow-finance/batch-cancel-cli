from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey

from ..program_id import PROGRAM_ID


class UnpauseAccounts(typing.TypedDict):
    sender: Pubkey
    metadata: Pubkey


def unpause(
    accounts: UnpauseAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[list[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["sender"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xa9\x90\x04&\n\x8d\xbc\xff"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
