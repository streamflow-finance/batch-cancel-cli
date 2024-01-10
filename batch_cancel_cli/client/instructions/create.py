from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

from ..program_id import PROGRAM_ID


class CreateArgs(typing.TypedDict):
    start_time: int
    net_amount_deposited: int
    period: int
    amount_per_period: int
    cliff: int
    cliff_amount: int
    cancelable_by_sender: bool
    cancelable_by_recipient: bool
    automatic_withdrawal: bool
    transferable_by_sender: bool
    transferable_by_recipient: bool
    can_topup: bool
    stream_name: list[int]
    withdraw_frequency: int
    pausable: typing.Optional[bool]
    can_update_rate: typing.Optional[bool]


layout = borsh.CStruct(
    "start_time" / borsh.U64,
    "net_amount_deposited" / borsh.U64,
    "period" / borsh.U64,
    "amount_per_period" / borsh.U64,
    "cliff" / borsh.U64,
    "cliff_amount" / borsh.U64,
    "cancelable_by_sender" / borsh.Bool,
    "cancelable_by_recipient" / borsh.Bool,
    "automatic_withdrawal" / borsh.Bool,
    "transferable_by_sender" / borsh.Bool,
    "transferable_by_recipient" / borsh.Bool,
    "can_topup" / borsh.Bool,
    "stream_name" / borsh.U8[64],
    "withdraw_frequency" / borsh.U64,
    "pausable" / borsh.Option(borsh.Bool),
    "can_update_rate" / borsh.Option(borsh.Bool),
)


class CreateAccounts(typing.TypedDict):
    sender: Pubkey
    sender_tokens: Pubkey
    recipient: Pubkey
    metadata: Pubkey
    escrow_tokens: Pubkey
    recipient_tokens: Pubkey
    streamflow_treasury: Pubkey
    streamflow_treasury_tokens: Pubkey
    withdrawor: Pubkey
    partner: Pubkey
    partner_tokens: Pubkey
    mint: Pubkey
    fee_oracle: Pubkey
    streamflow_program: Pubkey


def create(
    args: CreateArgs,
    accounts: CreateAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[list[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["sender"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["sender_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["recipient"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["metadata"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["escrow_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["recipient_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["streamflow_treasury"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["streamflow_treasury_tokens"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["withdrawor"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["partner"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["partner_tokens"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["fee_oracle"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["streamflow_program"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x18\x1e\xc8(\x05\x1c\x07w"
    encoded_args = layout.build(
        {
            "start_time": args["start_time"],
            "net_amount_deposited": args["net_amount_deposited"],
            "period": args["period"],
            "amount_per_period": args["amount_per_period"],
            "cliff": args["cliff"],
            "cliff_amount": args["cliff_amount"],
            "cancelable_by_sender": args["cancelable_by_sender"],
            "cancelable_by_recipient": args["cancelable_by_recipient"],
            "automatic_withdrawal": args["automatic_withdrawal"],
            "transferable_by_sender": args["transferable_by_sender"],
            "transferable_by_recipient": args["transferable_by_recipient"],
            "can_topup": args["can_topup"],
            "stream_name": args["stream_name"],
            "withdraw_frequency": args["withdraw_frequency"],
            "pausable": args["pausable"],
            "can_update_rate": args["can_update_rate"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
