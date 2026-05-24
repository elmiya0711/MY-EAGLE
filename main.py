import asyncio
import time
import argparse
from aiohttp import ClientSession, ClientTimeout
import statistics
import random
import warnings
warnings.filterwarnings("ignore")

BANNER = """"
_______ _     _    _______ _______ _______ _       _______ 
(_______) |   | |  (_______|_______|_______|_)     (_______)
 _  _  _| |___| |   _____   _______ _   ___ _       _____   
| ||_|| |_____  |  |  ___) |  ___  | | (_  | |     |  ___)  
| |   | |_____| |  | |_____| |   | | |___) | |_____| |_____ 
|_|   |_(_______|  |_______)_|   |_|\_____/|_______)_______)
 """"

async def fetch(session, url, results, errors, latencies):
    start = time.time()
    try:
        async with session.post(url, data="hello, world!") as resp:
            print(f"SEND THREADS: {url} STATUS: {resp.status}")
            await resp.read()
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)
            results.append(resp.status)
    except Exception as e:
        print(f"SEND THREADS: {url} Error: {e}")
        errors.append(str(e))

async def benchmark(url, concurrency, duration, proxies):
    timeout = ClientTimeout(total=10)
    results = []
    errors = []
    latencies = []
    async with ClientSession(timeout=timeout) as session:
        tasks = []
        start_time = time.time()
        while time.time() - start_time < duration:
            proxy = random.choice(proxies)
            tasks = [fetch(session, url, results, errors, latencies) for _ in range(concurrency)]
            await asyncio.gather(*tasks)
        print("\nDone!")
        return results, errors, latencies

def print_results(results, errors, latencies):
    print(f"2xx responses: {len([r for r in results if 200 <= r < 300])}")
    print(f"Non-2xx responses: {len([r for r in results if r < 200 or r >= 300])}")
    print(f"Errors: {len(errors)}")
    print(f"Latency (ms):")
    print(f" 50%: {statistics.median(latencies) if latencies else 0}")
    print(f" 95%: {sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0}")
    print(f" 99%: {sorted(latencies)[int(len(latencies)*0.99)] if latencies else 0}")
    print(f" Avg: {statistics.mean(latencies) if latencies else 0}")

async def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--proxy-file", default="http.txt")
    args = parser.parse_args()
    with open(args.proxy_file, "r") as f:
        proxies = [line.strip() for line in f.readlines()]
    results, errors, latencies = await benchmark(args.url, args.concurrency, args.duration, proxies)
    print_results(results, errors, latencies)

if __name__ == "__main__":
    asyncio.run(main())
