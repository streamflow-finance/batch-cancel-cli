from __future__ import annotations

import typing

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID

from ..program_id import PROGRAM_ID


class CancelAccounts(typing.TypedDict):
    authority: Pubkey
    sender: Pubkey
    sender_tokens: Pubkey
    recipient: Pubkey
    recipient_tokens: Pubkey
    metadata: Pubkey
    escrow_tokens: Pubkey
    streamflow_treasury: Pubkey
    streamflow_treasury_tokens: Pubkey
    partner: Pubkey
    partner_tokens: Pubkey
    mint: Pubkey


def cancel(
    accounts: CancelAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[list[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["sender"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["sender_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["recipient"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["recipient_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["escrow_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["streamflow_treasury"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["streamflow_treasury_tokens"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["partner"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["partner_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xe8\xdb\xdf)\xdb\xec\xdc\xbe"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
