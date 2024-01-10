from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

from ..program_id import PROGRAM_ID


class TransferRecipientAccounts(typing.TypedDict):
    authority: Pubkey
    new_recipient: Pubkey
    new_recipient_tokens: Pubkey
    metadata: Pubkey
    mint: Pubkey


def transfer_recipient(
    accounts: TransferRecipientAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[list[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["new_recipient"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["new_recipient_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xeb\xf6\xe0@i\xa6\x14\x8a"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
