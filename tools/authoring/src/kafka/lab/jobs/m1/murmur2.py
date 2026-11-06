"""Kafka's default partitioner (Java client): toPositive(murmur2(keyBytes)) % numPartitions."""
def murmur2(data: bytes) -> int:
    m, r = 0x5bd1e995, 24
    h = (0x9747b28c ^ len(data)) & 0xffffffff
    n = len(data) // 4
    for i in range(n):
        k = int.from_bytes(data[4 * i:4 * i + 4], "little")
        k = (k * m) & 0xffffffff; k ^= k >> r; k = (k * m) & 0xffffffff
        h = (h * m) & 0xffffffff; h ^= k
    rest = data[4 * n:]
    if len(rest) == 3: h ^= rest[2] << 16
    if len(rest) >= 2: h ^= rest[1] << 8
    if len(rest) >= 1: h ^= rest[0]; h = (h * m) & 0xffffffff
    h ^= h >> 13; h = (h * m) & 0xffffffff; h ^= h >> 15
    return h
def partition(key: str, n: int) -> int:
    return (murmur2(key.encode()) & 0x7fffffff) % n
if __name__ == "__main__":
  for city in ["Mumbai", "Pune", "Delhi", "Chennai"]:
    print(f"{city:8} murmur2={murmur2(city.encode()):10}  3 partitions -> {partition(city, 3)}   6 partitions -> {partition(city, 6)}")
