import threading
import hazelcast


def increment_worker(client_id):
    client = hazelcast.HazelcastClient(cluster_name="dev")
    distributed_map = client.get_map("my-distributed-map").blocking()

    for _ in range(10_000):
        value = distributed_map.get("key")
        value += 1
        distributed_map.put("key", value)

    print(f"Client {client_id} finished")
    client.shutdown()


if __name__ == "__main__":
    init_client = hazelcast.HazelcastClient(cluster_name="dev")
    init_map = init_client.get_map("my-distributed-map").blocking()
    init_map.put("key", 0)
    init_client.shutdown()

    threads = []
    for i in range(3):
        t = threading.Thread(target=increment_worker, args=(i,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    result_client = hazelcast.HazelcastClient(cluster_name="dev")
    result_map = result_client.get_map("my-distributed-map").blocking()
    final_value = result_map.get("key")
    print(f"\nExpected value: 30000")
    print(f"Actual value:   {final_value}")
    print(f"Lost updates:   {30000 - final_value}")
    result_client.shutdown()
