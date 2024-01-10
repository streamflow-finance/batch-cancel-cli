from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID

from ..program_id import PROGRAM_ID


class UpdateArgs(typing.TypedDict):
    enable_automatic_withdrawal: typing.Optional[bool]
    withdraw_frequency: typing.Optional[int]
    amount_per_period: typing.Optional[int]


layout = borsh.CStruct(
    "enable_automatic_withdrawal" / borsh.Option(borsh.Bool),
    "withdraw_frequency" / borsh.Option(borsh.U64),
    "amount_per_period" / borsh.Option(borsh.U64),
)


class UpdateAccounts(typing.TypedDict):
    sender: Pubkey
    metadata: Pubkey
    withdrawor: Pubkey


def update(
    args: UpdateArgs,
    accounts: UpdateAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[list[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["sender"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["withdrawor"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xdb\xc8X\xb0\x9e?\xfd\x7f"
    encoded_args = layout.build(
        {
            "enable_automatic_withdrawal": args["enable_automatic_withdrawal"],
            "withdraw_frequency": args["withdraw_frequency"],
            "amount_per_period": args["amount_per_period"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
