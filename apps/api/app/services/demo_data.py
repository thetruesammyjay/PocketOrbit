"""Illustrative fixtures. These values are not connected to a live wallet or market feed."""

DEMO_HOLDINGS = [
    {
        "asset": {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "network": None,
            "contractAddress": None,
        },
        "quantity": "0.084",
        "unitPrice": "118500.00",
        "value": "9954.00",
        "change24h": "1.8",
        "sourceIds": ["hardware-wallet", "exchange-import"],
    },
    {
        "asset": {
            "id": "ethereum",
            "symbol": "ETH",
            "name": "Ethereum",
            "network": "Ethereum",
            "contractAddress": None,
        },
        "quantity": "1.82",
        "unitPrice": "3820.00",
        "value": "6952.40",
        "change24h": "0.9",
        "sourceIds": ["exchange-import"],
    },
    {
        "asset": {
            "id": "solana",
            "symbol": "SOL",
            "name": "Solana",
            "network": "Solana",
            "contractAddress": None,
        },
        "quantity": "34.12",
        "unitPrice": "186.40",
        "value": "6359.97",
        "change24h": "2.4",
        "sourceIds": ["solana-wallet"],
    },
    {
        "asset": {
            "id": "usd-coin",
            "symbol": "USDC",
            "name": "USD Coin",
            "network": "Ethereum",
            "contractAddress": None,
        },
        "quantity": "8420",
        "unitPrice": "1.00",
        "value": "8420.00",
        "change24h": "0.0",
        "sourceIds": ["solana-wallet", "exchange-import"],
    },
]

DEMO_SOURCES = [
    {
        "id": "solana-wallet",
        "name": "Everyday wallet",
        "kind": "wallet",
        "network": "Solana",
        "addressLabel": "8F3…d72",
        "lastUpdatedAt": None,
        "quality": "estimated",
    },
    {
        "id": "hardware-wallet",
        "name": "Hardware wallet",
        "kind": "wallet",
        "network": "Bitcoin",
        "addressLabel": "bc1…4xq",
        "lastUpdatedAt": None,
        "quality": "estimated",
    },
    {
        "id": "exchange-import",
        "name": "Exchange statement",
        "kind": "exchange_import",
        "network": None,
        "addressLabel": "Sample CSV",
        "lastUpdatedAt": None,
        "quality": "estimated",
    },
]

DEMO_ACTIVITY = [
    {
        "id": "activity-1",
        "kind": "received",
        "assetSymbol": "USDC",
        "quantity": "320.00",
        "sourceName": "Everyday wallet",
        "occurredAt": "Sample record",
        "status": "confirmed",
    },
    {
        "id": "activity-2",
        "kind": "fee",
        "assetSymbol": "SOL",
        "quantity": "0.004",
        "sourceName": "Everyday wallet",
        "occurredAt": "Sample record",
        "status": "confirmed",
    },
    {
        "id": "activity-3",
        "kind": "trade",
        "assetSymbol": "ETH",
        "quantity": "0.25",
        "sourceName": "Exchange statement",
        "occurredAt": "Sample record",
        "status": "needs_review",
    },
]
