import time
import sys

def run_memory_leak(target_mb: int = 500, hold_seconds: int = 30):
    """Allocates byte arrays to simulate memory pressure."""
    print(f"🔥 Injecting Memory Chaos: Allocating ~{target_mb}MB RAM for {hold_seconds} seconds...")
    byte_chunks = []
    
    chunk_size = 10 * 1024 * 1024  # 10MB per chunk
    num_chunks = max(1, target_mb // 10)
    
    try:
        for i in range(num_chunks):
            byte_chunks.append(bytearray(chunk_size))
            time.sleep(0.1)
        print(f"Allocated {len(byte_chunks) * 10}MB memory. Holding allocation...")
        time.sleep(hold_seconds)
    finally:
        byte_chunks.clear()
        print("✅ Memory Chaos Injection complete. Memory freed.")

if __name__ == "__main__":
    mb = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    run_memory_leak(target_mb=mb, hold_seconds=15)
