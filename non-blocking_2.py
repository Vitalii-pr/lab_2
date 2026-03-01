

import hazelcast
import threading
import time


NUM_CLIENTS = 3
ITERATIONS = 10_000


def increment_worker_optimistic(worker_id: int, barrier: threading.Barrier, results: dict):
    client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    distributed_map = client.get_map("optimistic-map").blocking()

    distributed_map.put_if_absent("key", 0)

    barrier.wait()

    start = time.time()
    total_retries = 0

    for k in range(ITERATIONS):
        while True:
            old_value = distributed_map.get("key")
            new_value = old_value + 1
            if distributed_map.replace_if_same("key", old_value, new_value):
                break  
            else:
                total_retries += 1

        if (k + 1) % 2000 == 0:
            print(f"  [Client-{worker_id}] {k + 1}/{ITERATIONS}")

    elapsed = time.time() - start
    results[worker_id] = {"time": elapsed, "retries": total_retries}
    print(f"  [Client-{worker_id}]  {elapsed:.2f} sec "
          f"(retries: {total_retries})")

    client.shutdown()


def main():
    setup_client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    setup_map = setup_client.get_map("optimistic-map").blocking()
    setup_map.clear()
    setup_client.shutdown()

    barrier = threading.Barrier(NUM_CLIENTS)
    results = {}

    threads = []
    start_total = time.time()

    for i in range(NUM_CLIENTS):
        t = threading.Thread(
            target=increment_worker_optimistic,
            args=(i, barrier, results),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_time = time.time() - start_total

    check_client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    check_map = check_client.get_map("optimistic-map").blocking()
    final_value = check_map.get("key")
    check_client.shutdown()

    expected = NUM_CLIENTS * ITERATIONS
    total_retries = sum(r["retries"] for r in results.values())

    print()
    print(f"  Expected:      {expected}")
    print(f"  Actual:       {final_value}")
    print(f"  Total time:  {total_time:.2f} sec")
    print(f"  Total retries: {total_retries}")
    for wid, data in sorted(results.items()):
        print(f"    Client-{wid}: {data['time']:.2f} sec, "
              f"{data['retries']} retries")
    print()


if __name__ == "__main__":
    main()