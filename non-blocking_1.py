

import hazelcast
import threading
import time


NUM_CLIENTS = 3
ITERATIONS = 10_000


def increment_worker_locked(worker_id: int, barrier: threading.Barrier, results: dict):
    client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    distributed_map = client.get_map("locked-map").blocking()

    distributed_map.put_if_absent("key", 0)

    barrier.wait()

    start = time.time()

    for k in range(ITERATIONS):
        distributed_map.lock("key")
        try:
            value = distributed_map.get("key")
            value += 1
            distributed_map.put("key", value)
        finally:
            distributed_map.unlock("key")

        if (k + 1) % 2000 == 0:
            print(f"  [Client-{worker_id}] {k + 1}/{ITERATIONS}")

    elapsed = time.time() - start
    results[worker_id] = elapsed
    print(f"  [Client-{worker_id}] Ended in {elapsed:.2f} sec")

    client.shutdown()


def main():

    setup_client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    setup_map = setup_client.get_map("locked-map").blocking()
    setup_map.clear()
    setup_client.shutdown()

    barrier = threading.Barrier(NUM_CLIENTS)
    results = {}

    threads = []
    start_total = time.time()

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=increment_worker_locked, args=(i, barrier, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_time = time.time() - start_total

    check_client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    check_map = check_client.get_map("locked-map").blocking()
    final_value = check_map.get("key")
    check_client.shutdown()

    expected = NUM_CLIENTS * ITERATIONS

    print(f"  RESULT WITH PESSIMISTIC LOCKING")
    print(f"  Expected:    {expected}")
    print(f"  Obtained:     {final_value}")
    print(f"  Total time: {total_time:.2f} sec")


if __name__ == "__main__":
    main()