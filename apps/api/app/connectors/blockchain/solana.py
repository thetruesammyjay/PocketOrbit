import asyncio
from datetime import UTC, datetime

import httpx

from app.connectors.base import (
    BalanceConnector,
    NormalizedBalance,
    ProviderNotConfiguredError,
    ProviderRequestError,
    decimal_from_base_units,
)
from app.connectors.rpc import json_rpc
from app.core.config import settings

TOKEN_PROGRAMS = (
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
)


class SolanaConnector(BalanceConnector):
    network_id = "solana"

    def __init__(
        self,
        rpc_url: str | None = None,
        fallback_rpc_url: str | None = None,
    ) -> None:
        self.rpc_url = rpc_url or settings.solana_rpc_url
        self.fallback_rpc_url = fallback_rpc_url or settings.solana_rpc_fallback_url
        if self.fallback_rpc_url == self.rpc_url:
            self.fallback_rpc_url = None
        self.used_fallback_rpc = False
        self.token_program_failures = 0

    async def _request(
        self,
        client: httpx.AsyncClient,
        method: str,
        params: list[object],
    ) -> object:
        if not self.rpc_url:
            raise ProviderNotConfiguredError("Solana RPC is not configured.")
        try:
            return await json_rpc(client, self.rpc_url, method, params)
        except ProviderRequestError:
            if not self.fallback_rpc_url:
                raise

        result = await json_rpc(client, self.fallback_rpc_url, method, params)
        self.used_fallback_rpc = True
        return result

    async def get_balances(
        self, public_address: str, client: httpx.AsyncClient
    ) -> list[NormalizedBalance]:
        if not self.rpc_url:
            raise ProviderNotConfiguredError("Solana RPC is not configured.")

        native_task = self._request(
            client,
            "getBalance",
            [public_address, {"commitment": "confirmed"}],
        )
        token_tasks = [
            self._request(
                client,
                "getTokenAccountsByOwner",
                [
                    public_address,
                    {"programId": program_id},
                    {"commitment": "confirmed", "encoding": "jsonParsed"},
                ],
            )
            for program_id in TOKEN_PROGRAMS
        ]
        # The native balance is required, but one slow token program should not
        # discard balances returned by the native request or the other program.
        results = await asyncio.gather(native_task, *token_tasks, return_exceptions=True)
        retrieved_at = datetime.now(UTC)
        native_result = results[0]
        if isinstance(native_result, BaseException):
            raise native_result
        native_lamports = native_result.get("value") if isinstance(native_result, dict) else None
        if isinstance(native_lamports, bool) or not isinstance(native_lamports, int):
            raise ProviderRequestError("Solana RPC returned an invalid native balance.")
        if native_lamports < 0:
            raise ProviderRequestError("Solana RPC returned an invalid native balance.")

        native_context = native_result.get("context", {})
        native_slot = native_context.get("slot") if isinstance(native_context, dict) else None
        balances = [
            NormalizedBalance(
                asset_id="solana",
                symbol="SOL",
                name="Solana",
                network_id=self.network_id,
                quantity=decimal_from_base_units(native_lamports, 9),
                contract_address=None,
                decimals=9,
                source_record_ids=(),
                retrieved_at=retrieved_at,
                block_reference=f"slot:{native_slot}" if native_slot is not None else None,
            )
        ]

        tokens: dict[str, dict[str, object]] = {}
        for token_result in results[1:]:
            if isinstance(token_result, asyncio.CancelledError):
                raise token_result
            if isinstance(token_result, Exception):
                self.token_program_failures += 1
                continue
            if isinstance(token_result, BaseException):
                raise token_result
            if not isinstance(token_result, dict) or not isinstance(
                token_result.get("value"), list
            ):
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
                except (KeyError, TypeError, ValueError) as exc:
                    raise ProviderRequestError(
                        "Solana RPC could not parse one or more token accounts."
                    ) from exc
                if (
                    not isinstance(pubkey, str)
                    or not isinstance(mint, str)
                    or not isinstance(amount, str)
                    or not amount.isascii()
                    or not amount.isdecimal()
                    or isinstance(decimals, bool)
                    or not isinstance(decimals, int)
                    or not 0 <= decimals <= 255
                ):
                    raise ProviderRequestError(
                        "Solana RPC returned invalid token amount or decimal metadata."
                    )
                raw_amount = int(amount)

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
                    quantity=decimal_from_base_units(raw_amount, decimals),
                    contract_address=mint,
                    decimals=decimals,
                    source_record_ids=tuple(records) if isinstance(records, list) else (),
                    retrieved_at=retrieved_at,
                    block_reference=f"slot:{slot}" if slot is not None else None,
                )
            )
        return balances
