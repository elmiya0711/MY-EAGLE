import asyncio
import time
import argparse
from aiohttp import ClientSession, ClientTimeout
import statistics
from hdrhistogram import HdrHistogram

BANNER = """
███╗   ███╗███████╗ ██████╗ 
████╗ ████║██╔════╝██╔════╝ 
██╔████╔██║███████╗██║  ███╗
██║╚██╔╝██║╚════██║██║   ██║
██║ ╚═╝ ██║███████║╚██████╔╝
╚═╝     ╚═╝╚══════╝ ╚═════╝ 
        MY EAGLE
"""

async def fetch(session, url, results, errors, latencies):
    start = time.time()
    try:
        async with session.post(url, data="hello, world!") as resp:
            await resp.read()
            latency = (time.time() - start) * 1000  # ms
            latencies.record_value(latency)
            results.append(resp.status)
    except Exception as e:
        errors.append(str(e))

async def benchmark(url, concurrency, duration):
    timeout = ClientTimeout(total=10)
    results = []
    errors = []
    latencies = HdrHistogram(1, 10000, 3)
    async with ClientSession(timeout=timeout) as session:
        tasks = []
        start_time = time.time()
        while time.time() - start_time < duration:
            tasks = [fetch(session, url, results, errors, latencies) for _ in range(concurrency)]
            await asyncio.gather(*tasks)
        print("\nDone!")
        return results, errors, latencies

def print_results(results, errors, latencies):
    print(f"2xx responses: {len([r for r in results if 200 <= r < 300])}")
    print(f"Non-2xx responses: {len([r for r in results if r < 200 or r >= 300])}")
    print(f"Errors: {len(errors)}")
    print(f"Latency (ms):")
    print(f"  50%: {latencies.get_value_at_percentile(50)}")
    print(f"  95%: {latencies.get_value_at_percentile(95)}")
    print(f"  99%: {latencies.get_value_at_percentile(99)}")
    print(f"  Avg: {latencies.get_mean_value()}")

async def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()
    results, errors, latencies = await benchmark(args.url, args.concurrency, args.duration)
    print_results(results, errors, latencies)

if __name__ == "__main__":
    asyncio.run(main())
