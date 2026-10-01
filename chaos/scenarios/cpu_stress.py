import multiprocessing
import time
import sys

def cpu_burn_target():
    """Generates 100% CPU load on a single core."""
    while True:
        pass

def run_cpu_stress(duration_seconds: int = 30, num_cores: int = None):
    """Spawns worker processes to stress host CPU."""
    if num_cores is None:
        num_cores = multiprocessing.cpu_count()
        
    print(f"🔥 Injecting CPU Chaos: Stressing {num_cores} cores for {duration_seconds} seconds...")
    processes = []
    
    for _ in range(num_cores):
        p = multiprocessing.Process(target=cpu_burn_target)
        p.daemon = True
        p.start()
        processes.append(p)
        
    time.sleep(duration_seconds)
    
    for p in processes:
        p.terminate()
        p.join()
        
    print("✅ CPU Chaos Injection complete. Workers terminated.")

if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    run_cpu_stress(duration_seconds=dur)
