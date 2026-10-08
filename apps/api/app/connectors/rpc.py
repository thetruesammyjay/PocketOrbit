from typing import Any

import httpx

from app.connectors.base import ProviderRequestError


async def json_rpc(
    client: httpx.AsyncClient,
    endpoint: str,
    method: str,
    params: list[Any],
    *,
    allow_unsupported_method: bool = False,
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
    except httpx.HTTPStatusError as exc:
        if allow_unsupported_method and exc.response.status_code in {403, 404, 405, 501}:
            # Some RPC gateways report a disabled extension as HTTP rather than
            # returning JSON-RPC -32601. Let callers use their safe fallback.
            return None
        raise ProviderRequestError(
            f"The configured data provider returned HTTP {exc.response.status_code}."
        ) from None
    except httpx.TimeoutException:
        raise ProviderRequestError("The configured data provider timed out.") from None
    except httpx.HTTPError:
        # Suppress the transport exception because it can contain a credential-bearing URL.
        raise ProviderRequestError("The configured data provider could not be reached.") from None
    except ValueError:
        raise ProviderRequestError("The configured data provider returned invalid JSON.") from None

    if not isinstance(payload, dict):
        raise ProviderRequestError("The configured data provider returned an invalid response.")
    if payload.get("error"):
        error = payload["error"]
        message = error.get("message", "") if isinstance(error, dict) else ""
        code = error.get("code") if isinstance(error, dict) else None
        if allow_unsupported_method and (
            code == -32601 or "method not found" in str(message).lower()
        ):
            return None
        raise ProviderRequestError("The configured data provider rejected a read request.")
    if "result" not in payload:
        raise ProviderRequestError("The configured data provider returned an incomplete response.")
    return payload["result"]
