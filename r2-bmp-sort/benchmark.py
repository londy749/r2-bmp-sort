import time
import random
import math

def generate_sedgewick_gaps(N):
    gaps = []
    k = 0
    while True:
        if k % 2 == 0:
            gap = int(9 * (2**k) - 9 * (2**(k // 2)) + 1)
        else:
            gap = int(8 * (2**k) - 6 * (2**((k + 1) // 2)) + 1)
        if gap >= N:
            break
        gaps.append(gap)
        k += 1
    return gaps[::-1]

def shell_sort_sedgewick(keys, pixels):
    N = len(keys)
    gaps = generate_sedgewick_gaps(N)

    combined_keys = [(keys[i], i) for i in range(N)]
    
    for gap in gaps:
        for i in range(gap, N):
            key_val = combined_keys[i]
            pixel_val = pixels[i]
            j = i
            

            while j >= gap and combined_keys[j - gap] > key_val:
                combined_keys[j] = combined_keys[j - gap]
                pixels[j] = pixels[j - gap]
                j -= gap
                
            combined_keys[j] = key_val
            pixels[j] = pixel_val
            

    for i in range(N):
        keys[i] = combined_keys[i][0]

def run_benchmarks():
    sizes = [1000, 5000, 10000, 20000, 30000, 50000]
    repeats = 7
    
    table_4_2 = []
    table_4_4 = []
    
    print("Запуск тестов производительности чистого алгоритма...")
    
    for n in sizes:
        times = []
        for _ in range(repeats):
            keys = [random.randint(0, 100000) for _ in range(n)]
            pixels = [b'\x00\x00\x00'] * n
            
            start = time.perf_counter()
            shell_sort_sedgewick(keys, pixels)
            end = time.perf_counter()
            
            times.append((end - start) * 1000)
            
        times.sort()
        t_min = times[0]
        t_max = times[-1]
        t_med = times[len(times) // 2]
        
        fn = n ** 1.167
        ratio = t_med / fn if fn > 0 else 0
        
        table_4_2.append((n, t_med, t_min, t_max))
        table_4_4.append((n, t_med, fn, ratio))
        
    print(f"\n{'n':<10}{'Медиана, мс':<15}{'Мин, мс':<12}{'Макс, мс':<12}")
    for row in table_4_2:
        print(f"{row[0]:<10}{row[1]:<15.2f}{row[2]:<12.2f}{row[3]:<12.2f}")
        
    print(f"\n{'n':<10}{'t(n), мс':<15}{'f(n)':<15}{'t(n)/f(n)':<12}")
    for row in table_4_4:
        print(f"{row[0]:<10}{row[1]:<15.2f}{row[2]:<15.2f}{row[3]:<12.6f}")

if __name__ == '__main__':
    run_benchmarks()
