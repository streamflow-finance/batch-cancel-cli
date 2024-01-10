from pathlib import Path
from typing import Sequence, overload

import click
import solders
from click import Context
from solana.rpc.api import Client
from solana.transaction import Transaction
from solders.instruction import Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

from batch_cancel_cli.client.instructions import cancel as build_cancel_ix
from batch_cancel_cli.client.instructions import create as build_create_ix
from batch_cancel_cli.client.instructions import transfer_recipient as build_transfer_recipient_ix
from batch_cancel_cli.client.instructions.create import CreateAccounts, CreateArgs
from batch_cancel_cli.client.program_id import PROGRAM_ID
from batch_cancel_cli.client.structures import Contract

NETWORKS = {True: "https://api.devnet.solana.com", False: "https://api.mainnet-beta.solana.com"}
STREAMFLOW_TREASURY = Pubkey.from_string("5SEpbdjFK5FxwTvfsGMXVQTD2v4M2c5tyRTxhdsPkgDw")
WITHDRAWOR = Pubkey.from_string("wdrwhnCv4pzW8beKsbPa4S2UDZrXenjg16KJdKSpb5u")
FEE_ORACLE = Pubkey.from_string("B743wFVk2pCYhV91cn287e1xY7f1vt4gdY48hhNiuQmT")


@overload
def validate_pubkey(ctx, param, value: str) -> Pubkey:
    ...


@overload
def validate_pubkey(ctx, param, value: tuple[str, ...]) -> tuple[Pubkey, ...]:
    ...


def validate_pubkey(ctx, param, value: str | tuple[str, ...]) -> Pubkey | tuple[Pubkey, ...]:
    try:
        return (
            Pubkey.from_string(value) if not isinstance(value, tuple) else tuple(Pubkey.from_string(s) for s in value)
        )
    except:
        raise click.BadParameter("Invalid pubkey")


def validate_private_keys_file(ctx, param, value: str) -> Keypair:
    path = Path(value)
    if not path.exists():
        try:
            return Keypair.from_base58_string(value)
        except:
            raise click.BadParameter("Invalid key or keys file does not exist")
    with open(value) as r:
        try:
            return Keypair.from_json(r.read().strip())
        except:
            raise click.BadParameter("Invalid keys file")


def derive_ata(pubkey: Pubkey, mint: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(pubkey), bytes(TOKEN_PROGRAM_ID), bytes(mint)], ASSOCIATED_TOKEN_PROGRAM_ID
    )[0]


def build_create_args(net_amount_deposited: int, period: int, amount_per_period: int, name: str) -> CreateArgs:
    encoded_name = name.encode()
    name_byte_array = bytearray(64)
    name_byte_array[0 : len(encoded_name)] = encoded_name
    return CreateArgs(
        start_time=0,
        net_amount_deposited=net_amount_deposited,
        period=period,
        amount_per_period=amount_per_period,
        cliff=0,
        cliff_amount=0,
        cancelable_by_sender=True,
        cancelable_by_recipient=False,
        automatic_withdrawal=False,
        transferable_by_sender=True,
        transferable_by_recipient=False,
        can_topup=False,
        stream_name=list(name_byte_array),
        withdraw_frequency=0,
        pausable=False,
        can_update_rate=False,
    )


class Runner:
    def __init__(
        self,
        rpc_url: str,
        signer: Keypair,
        program_id: Pubkey = PROGRAM_ID,
    ):
        self.client = Client(rpc_url)
        self.signer = signer
        self.payer = signer.pubkey()
        self.program_id = program_id

    def generate_compute_budget_instruction(self) -> Instruction:
        return Instruction(
            program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
            data=bytes.fromhex("0200e20400"),
            accounts=[],
        )

    def generate_create_instruction(
        self, args: CreateArgs, contract_signer: Keypair, mint: Pubkey, recipient: Pubkey
    ) -> Instruction:
        contract_metadata = contract_signer.pubkey()
        escrow_tokens, _ = Pubkey.find_program_address([b"strm", bytes(contract_metadata)], self.program_id)
        return build_create_ix(
            args,
            CreateAccounts(
                mint=mint,
                sender=self.payer,
                sender_tokens=derive_ata(self.payer, mint),
                recipient=recipient,
                recipient_tokens=derive_ata(recipient, mint),
                streamflow_treasury=STREAMFLOW_TREASURY,
                streamflow_treasury_tokens=derive_ata(STREAMFLOW_TREASURY, mint),
                partner=self.payer,
                partner_tokens=derive_ata(self.payer, mint),
                metadata=contract_metadata,
                escrow_tokens=escrow_tokens,
                fee_oracle=FEE_ORACLE,
                withdrawor=WITHDRAWOR,
                streamflow_program=self.program_id,
            ),
            self.program_id,
        )

    def generate_transfer_instruction(
        self, new_recipient: Pubkey, contract_id: Pubkey, contract: Contract
    ) -> Instruction:
        mint = Pubkey(contract.mint)
        return build_transfer_recipient_ix(
            {
                "authority": self.payer,
                "new_recipient": new_recipient,
                "new_recipient_tokens": derive_ata(new_recipient, mint),
                "metadata": contract_id,
                "mint": mint,
            },
            self.program_id,
        )

    def generate_cancel_instruction(
        self, contract_id: Pubkey, contract: Contract, recipient: Pubkey | None = None
    ) -> Instruction:
        mint = Pubkey(contract.mint)
        recipient = recipient or Pubkey(contract.recipient)
        return build_cancel_ix(
            {
                "authority": self.payer,
                "sender": Pubkey(contract.sender),
                "sender_tokens": Pubkey(contract.sender_tokens),
                "recipient": recipient,
                "recipient_tokens": derive_ata(recipient, mint),
                "metadata": contract_id,
                "escrow_tokens": Pubkey(contract.escrow_tokens),
                "streamflow_treasury": Pubkey(contract.streamflow_treasury),
                "streamflow_treasury_tokens": Pubkey(contract.streamflow_treasury_tokens),
                "partner": Pubkey(contract.partner),
                "partner_tokens": Pubkey(contract.partner_tokens),
                "mint": mint,
            },
            self.program_id,
        )

    def generate_tx(self, *ixs: Instruction) -> Transaction:
        return Transaction(
            recent_blockhash=(self.client.get_latest_blockhash()).value.blockhash,
            fee_payer=self.payer,
        ).add(self.generate_compute_budget_instruction(), *ixs)

    def get_contract(self, contract_id: Pubkey) -> Contract:
        res = self.client.get_account_info(contract_id)
        return Contract.from_bytes(res.value.data)

    def get_contracts(self, contract_ids: Sequence[Pubkey]) -> list[Contract | None]:
        contracts = []
        res = self.client.get_multiple_accounts(list(contract_ids))
        for data in res.value:
            contracts.append(Contract.from_bytes(data.data) if data else None)
        return contracts

    def create_contract(self, args: CreateArgs, contract_signer: Keypair, mint: Pubkey, recipient: Pubkey) -> Signature:
        ix = self.generate_create_instruction(args, contract_signer, mint, recipient)
        tx = self.generate_tx(ix)
        tx.sign(self.signer, contract_signer)
        return self.client.send_raw_transaction(tx.serialize()).value

    def transfer_cancel(self, new_recipient: Pubkey, contract_id: Pubkey, contract: Contract) -> Signature:
        transfer_ix = self.generate_transfer_instruction(new_recipient, contract_id, contract)
        cancel_ix = self.generate_cancel_instruction(contract_id, contract, new_recipient)
        tx = self.generate_tx(transfer_ix, cancel_ix)
        tx.sign(self.signer)
        return self.client.send_raw_transaction(tx.serialize()).value


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--devnet", is_flag=True, show_default=True, default=False, help="Use devnet")
@click.option(
    "--key",
    "signer",
    show_default=True,
    default="signer.json",
    callback=validate_private_keys_file,
    help="Path to the keys.json file for the stream sender or base58 encoded private key",
)
@click.option("--rpc", help="Use non default RPC Pool")
@click.pass_context
def cli(ctx: Context, devnet: bool, signer: Keypair, rpc: str | None):
    ctx.ensure_object(dict)
    rpc = rpc or NETWORKS[devnet]
    ctx.obj["runner"] = Runner(
        rpc,
        signer,
        Pubkey.from_string("HqDGZjaVRXJ9MGRQEw7qDc2rAr6iH1n1kAQdCZaCMfMZ")
        if devnet
        else Pubkey.from_string("strmRqUCoQUgGUan5YhzUZa6KqdzwX5L6FpUxfmKg5m"),
    )


@cli.command(help="Create a new Contract")
@click.argument("recipient", callback=validate_pubkey)
@click.option(
    "-m",
    "--mint",
    show_default=True,
    callback=validate_pubkey,
    help="Mint of the token to vest",
)
@click.option("-n", "--net-amount", show_default=True, default=1000000, help="Total amount of tokens to vest")
@click.option("-p", "--period", show_default=True, default=30, help="Release period, release A amount every P seconds")
@click.option(
    "-a",
    "--amount-per-period",
    show_default=True,
    default=100000,
    help="Release amount, every P seconds release A amount",
)
@click.option("--name", show_default=True, default="", help="Name of a vesting stream")
@click.pass_context
def create(
    ctx: Context,
    recipient: Pubkey,
    net_amount: int,
    mint: Pubkey,
    period: int,
    amount_per_period: int,
    name: str,
):
    contract_signer = Keypair()
    args = build_create_args(net_amount, period, amount_per_period, name)
    runner: Runner = ctx.obj["runner"]
    signature = runner.create_contract(args, contract_signer, mint, recipient)
    click.echo(f"Contract id: {contract_signer.pubkey()}")
    click.echo(f"Tx: {signature}")
    click.echo("Finished")


@cli.command(help="Transfer contract_ids to new_recipient and then cancel them")
@click.argument(
    "contract_ids",
    nargs=-1,
    callback=validate_pubkey,
)
@click.option("-r", "--new-recipient", callback=validate_pubkey, help="Address for the new recipient")
@click.pass_context
def cancel(
    ctx: Context,
    contract_ids: tuple[Pubkey],
    new_recipient: Pubkey,
):
    runner: Runner = ctx.obj["runner"]
    contracts = runner.get_contracts(contract_ids)
    click.echo(f"Processing {len(contracts)} contracts")
    for contract_id, contract in zip(contract_ids, contracts, strict=True):
        if not contract:
            click.echo(f"Skipping contract {contract_id} as there is no metadata for it")
            continue
        sig = runner.transfer_cancel(new_recipient, contract_id, contract)
        click.echo(f"Cancel tx for contract {contract_id}: {sig}")
    click.echo("Finished")


def main():
    cli()


if __name__ == "__main__":
    main()
