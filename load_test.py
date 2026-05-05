import asyncio
import httpx

URL     = "http://127.0.0.1:8000/api/signals"
PAYLOAD = {"component_id": "CACHE_CLUSTER_01", "signal_type": "CPU_HIGH", "value": 92.5}

results = {"202": 0, "429": 0, "other": 0}

async def send_signal(client, i):
    try:
        response = await client.post(URL, json=PAYLOAD)
        code = str(response.status_code)
        if code == "202":
            results["202"] += 1
        elif code == "429":
            results["429"] += 1
        else:
            results["other"] += 1
        print(f"Request {i:3d} → {response.status_code}")
    except Exception as e:
        print(f"Request {i:3d} → ERROR: {e}")

async def main():
    print("Sending 150 simultaneous requests...")
    # Increase connection pool limits to handle 150 at once
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=200)
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = [send_signal(client, i) for i in range(1, 151)]
        await asyncio.gather(*tasks)

    print("\n── Summary ──────────────────")
    print(f"✅ Accepted (202): {results['202']}")
    print(f"🚫 Rate limited (429): {results['429']}")
    print(f"❓ Other: {results['other']}")
    print("─────────────────────────────")

asyncio.run(main())