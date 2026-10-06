import asyncio
from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.connectors.base import (
    BalanceConnector,
    NormalizedBalance,
    ProviderNotConfiguredError,
    ProviderRequestError,
)
from app.connectors.rpc import json_rpc
from app.core.config import settings

TOKEN_PROGRAMS = (
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
)


class SolanaConnector(BalanceConnector):
    network_id = "solana"

    def __init__(self, rpc_url: str | None = None) -> None:
        self.rpc_url = rpc_url or settings.solana_rpc_url

    async def get_balances(
        self, public_address: str, client: httpx.AsyncClient
    ) -> list[NormalizedBalance]:
        if not self.rpc_url:
            raise ProviderNotConfiguredError("Solana RPC is not configured.")

        native_task = json_rpc(
            client,
            self.rpc_url,
            "getBalance",
            [public_address, {"commitment": "confirmed"}],
        )
        token_tasks = [
            json_rpc(
                client,
                self.rpc_url,
                "getTokenAccountsByOwner",
                [
                    public_address,
                    {"programId": program_id},
                    {"commitment": "confirmed", "encoding": "jsonParsed"},
                ],
            )
            for program_id in TOKEN_PROGRAMS
        ]
        results = await asyncio.gather(native_task, *token_tasks)
        retrieved_at = datetime.now(UTC)
        native_result = results[0]
        native_lamports = native_result.get("value") if isinstance(native_result, dict) else None
        if not isinstance(native_lamports, int):
            raise ProviderRequestError("Solana RPC returned an invalid native balance.")

        native_context = native_result.get("context", {})
        native_slot = native_context.get("slot") if isinstance(native_context, dict) else None
        balances = [
            NormalizedBalance(
                asset_id="solana",
                symbol="SOL",
                name="Solana",
                network_id=self.network_id,
                quantity=Decimal(native_lamports).scaleb(-9),
                contract_address=None,
                decimals=9,
                source_record_ids=(),
                retrieved_at=retrieved_at,
                block_reference=f"slot:{native_slot}" if native_slot is not None else None,
            )
        ]

        tokens: dict[str, dict[str, object]] = {}
        for token_result in results[1:]:
            if not isinstance(token_result, dict) or not isinstance(token_result.get("value"), list):
                raise ProviderRequestError("Solana RPC returned invalid token account data.")
            context = token_result.get("context", {})
            slot = context.get("slot") if isinstance(context, dict) else None
            for account in token_result["value"]:
                try:
                    pubkey = account["pubkey"]
                    parsed = account["account"]["data"]["parsed"]["info"]
                    mint = parsed["mint"]
                    amount = parsed["tokenAmount"]["amount"]
                    decimals = parsed["tokenAmount"]["decimals"]
                    raw_amount = int(amount)
                    decimals = int(decimals)
                except (KeyError, TypeError, ValueError) as exc:
                    raise ProviderRequestError(
                        "Solana RPC could not parse one or more token accounts."
                    ) from exc

                token = tokens.setdefault(
                    mint,
                    {"raw_amount": 0, "decimals": decimals, "records": [], "slot": slot},
                )
                if token["decimals"] != decimals:
                    raise ProviderRequestError("Solana RPC returned inconsistent token decimals.")
                token["raw_amount"] = int(token["raw_amount"]) + raw_amount
                records = token["records"]
                if isinstance(records, list):
                    records.append(str(pubkey))
                if slot is not None:
                    token["slot"] = slot

        for mint, token in tokens.items():
            raw_amount = int(token["raw_amount"])
            if raw_amount == 0:
                continue
            decimals = int(token["decimals"])
            slot = token["slot"]
            records = token["records"]
            balances.append(
                NormalizedBalance(
                    asset_id=mint,
                    symbol=f"{mint[:4]}…{mint[-4:]}",
                    name="Unverified Solana token",
                    network_id=self.network_id,
                    quantity=Decimal(raw_amount).scaleb(-decimals),
                    contract_address=mint,
                    decimals=decimals,
                    source_record_ids=tuple(records) if isinstance(records, list) else (),
                    retrieved_at=retrieved_at,
                    block_reference=f"slot:{slot}" if slot is not None else None,
                )
            )
        return balances
