from typing import Any

import httpx

from app.connectors.base import ProviderRequestError


async def json_rpc(
    client: httpx.AsyncClient,
    endpoint: str,
    method: str,
    params: list[Any],
) -> Any:
    try:
        response = await client.post(
            endpoint,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        )
        if response.status_code == 429:
            raise ProviderRequestError("The configured data provider rate-limited this request.")
        response.raise_for_status()
        payload = response.json()
    except ProviderRequestError:
        raise
    except (httpx.HTTPError, ValueError) as exc:
        # Do not include exception text: RPC URLs can contain provider credentials.
        raise ProviderRequestError("The configured data provider could not be reached.") from exc

    if not isinstance(payload, dict):
        raise ProviderRequestError("The configured data provider returned an invalid response.")
    if payload.get("error"):
        raise ProviderRequestError("The configured data provider rejected a read request.")
    if "result" not in payload:
        raise ProviderRequestError("The configured data provider returned an incomplete response.")
    return payload["result"]
