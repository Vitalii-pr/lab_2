import hazelcast
import threading
import time
from collections import defaultdict


def producer(barrier: threading.Barrier, stop_event: threading.Event):
    client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    queue = client.get_queue("bounded-queue").blocking()

    barrier.wait()

    start = time.time()

    for i in range(1, 101):
        success = queue.offer(i, 10)  
        if success:
            print(f"  [PRODUCER] → put({i})  (queue size: {queue.size()})")
        else:
            print(f"  [PRODUCER]  TIMEOUT put({i}) — queue full")
        time.sleep(0.05)

    elapsed = time.time() - start

    stop_event.set() 
    client.shutdown()


def consumer(consumer_id: int, barrier: threading.Barrier,
             stop_event: threading.Event, consumed: dict, lock: threading.Lock):
    client = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    queue = client.get_queue("bounded-queue").blocking()

    barrier.wait()

    items = []

    while not stop_event.is_set() or queue.size() > 0:
        item = queue.poll(1)  
        if item is not None:
            items.append(item)
            print(f"  [CONSUMER-{consumer_id}] ← got({item})")

    with lock:
        consumed[consumer_id] = items

    print(f"\n  [CONSUMER-{consumer_id}] ✓ Read {len(items)} items")
    client.shutdown()


def run_producer_consumers():

    setup = hazelcast.HazelcastClient(
        cluster_name="dev",
    )
    queue = setup.get_queue("bounded-queue").blocking()
    queue.clear()
    setup.shutdown()

    barrier = threading.Barrier(3) 
    stop_event = threading.Event()
    consumed = {}
    lock = threading.Lock()

    threads = [
        threading.Thread(target=producer, args=(barrier, stop_event)),
        threading.Thread(target=consumer, args=(1, barrier, stop_event, consumed, lock)),
        threading.Thread(target=consumer, args=(2, barrier, stop_event, consumed, lock)),
    ]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total_time = time.time() - start

    all_items = []
    for cid in sorted(consumed.keys()):
        items = consumed[cid]
        all_items.extend(items)
        print(f"\n  Consumer-{cid}: received {len(items)} items")
        print(f"    Values: {items[:15]}{'...' if len(items) > 15 else ''}")

    all_items_sorted = sorted(all_items)
    expected = list(range(1, 101))
    missing = [x for x in expected if x not in all_items]
    duplicates = [x for x in all_items if all_items.count(x) > 1]

    print(f"\n  Read :  {len(all_items)}")
    print(f"  Expected:         100")
    print(f"  Duplicates:        {len(set(duplicates))}")
    print(f"  Missing:         {len(missing)}")


    c1_count = len(consumed.get(1, []))
    c2_count = len(consumed.get(2, []))
    print(f"    Consumer-1: {c1_count} elements "
          f"({'█' * (c1_count // 2)} {c1_count}%)")
    print(f"    Consumer-2: {c2_count} elements "
          f"({'█' * (c2_count // 2)} {c2_count}%)")

    print(f"\n  Total time: {total_time:.2f} sec")

    print(f"\n CONCLUSION: Distributed Queue works like a classic queue —")
    print(f"     each message is received by ONLY ONE consumer.")
    print(f"     Two consumers share the load between them.")


def run_full_queue_test():

    client = hazelcast.HazelcastClient(
        cluster_name="dev",
        client_name="full-queue-test",
    )
    queue = client.get_queue("bounded-queue").blocking()
    queue.clear()

    print(f"\n  Queue cleared. Size: {queue.size()}")
    print(f"  Attempting to add 15 elements (queue limit = 10)...\n")

    start = time.time()

    for i in range(1, 16):
        t_start = time.time()

        success = queue.offer(i, 3)

        t_elapsed = time.time() - t_start
        size = queue.size()

    total_time = time.time() - start

    print(f"\n  Final queue size: {queue.size()}")
    print(f"  Total time: {total_time:.2f} sec")

    print(f"\n  CONCLUSION:")
    print(f"     When the queue is full (10/10) and no one is reading:")
    print(f"     • offer(item, timeout) — BLOCKS for timeout seconds,")
    print(f"       then returns False (item NOT added)")
    print(f"     • put(item) — BLOCKS FOREVER until space is available")
    print(f"     • offer(item) without timeout — immediately returns False")
    print(f"     → Producer stops (backpressure mechanism)")

    print(f"\n  ── Test put() (blocking write without timeout) ──")
    print(f"  Queue full ({queue.size()}/10). Starting put() in a separate thread...")

    put_completed = threading.Event()

    def blocking_put():
        queue.put(999)
        put_completed.set()

    t = threading.Thread(target=blocking_put, daemon=True)
    t.start()

    time.sleep(3)
    if put_completed.is_set():
        pass
    else:
        item = queue.poll(1)
        time.sleep(0.5)

        if put_completed.is_set():
            pass
        else:
            pass

    t.join(timeout=2)

    queue.clear()
    client.shutdown()



def main():
    run_producer_consumers()

    run_full_queue_test()



if __name__ == "__main__":
    main()