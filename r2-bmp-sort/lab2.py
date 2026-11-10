import sys
import struct
import time
import random

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

def shell_sort_sedgewick(keys, pixels, animate_K=None, bmp_info=None):
    N = len(keys)
    gaps = generate_sedgewick_gaps(N)
    
    combined_keys = [(keys[i], i) for i in range(N)]
    
    op_counter = 0
    frame_idx = 0
    
    for gap in gaps:
        for i in range(gap, N):
            key_val = combined_keys[i]
            pixel_val = pixels[i]
            
            j = i
            while j >= gap and combined_keys[j - gap] > key_val:
                combined_keys[j] = combined_keys[j - gap]
                pixels[j] = pixels[j - gap]
                j -= gap
     
                op_counter += 1
                if animate_K and op_counter % animate_K == 0:
                    frame_idx += 1
                    save_animation_frame(frame_idx, pixels, bmp_info)
                    
            combined_keys[j] = key_val
            pixels[j] = pixel_val
            
            op_counter += 1
            if animate_K and op_counter % animate_K == 0:
                frame_idx += 1
                save_animation_frame(frame_idx, pixels, bmp_info)

    for i in range(N):
        keys[i] = combined_keys[i][0]


import os
import cv2 

created_frames = []

def save_animation_frame(frame_idx, pixels, bmp_info):
    if not bmp_info:
        return
    shuffled_path, bfOffBits, width, height, bitCount = bmp_info
    out_path = f"frame_{frame_idx:04d}.bmp"

    write_bmp(shuffled_path, out_path, bfOffBits, width, height, bitCount, pixels, quiet=True)

    created_frames.append(out_path)

def compile_video_from_frames(video_name="sorting_process.mp4", fps=20):
    global created_frames
    if not created_frames:
        return
        
    print(f"\nСортировка завершена! Сборка видео из {len(created_frames)} кадров...")

    first_frame = cv2.imread(created_frames[0])
    height, width, layers = first_frame.shape
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))
    
    for frame_path in created_frames:
        img = cv2.imread(frame_path)
        video.write(img)
    
        try:
            os.remove(frame_path)
        except Exception:
            pass
            
    video.release()
    print(f"[УСПЕХ] Видео успешно сохранено как: {video_name}")
    created_frames = []


def read_keys(keys_path):
    try:
        with open(keys_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        if not lines:
            raise ValueError("Файл ключей пуст")
        
        try:
            N = int(lines[0].strip())
        except ValueError:
            raise ValueError("Первая строка файла ключей должна содержать целое число N (количество элементов)")
        
        # Считываем все непустые строки, идущие после первой
        keys = [int(line.strip()) for line in lines[1:] if line.strip()]
        
        if len(keys) != N:
            raise ValueError(f"Длина файла ключей не совпадает с заявленной: ожидалось {N} ключей, прочитано {len(keys)}")
            
        return N, keys
    except Exception as e:
        print(f"Ошибка при чтении ключей: {e}", file=sys.stderr)
        sys.exit(0)

def read_bmp(bmp_path, expected_N):
    try:
        with open(bmp_path, 'rb') as f:
            file_header = f.read(14)
            if len(file_header) < 14: 
                raise ValueError("Файл поврежден или усечен (размер меньше 14 байт заголовка)")
            
            bfType, bfSize, bfRes1, bfRes2, bfOffBits = struct.unpack('<2s I H H I', file_header)
            
  
            if bfType != b'BM': 
                raise ValueError(f"Неверная сигнатура файла: ожидалось 'BM', получено '{bfType.decode(errors='ignore')}'")
  
            info_header = f.read(40)
            if len(info_header) < 40: 
                raise ValueError("Файл поврежден или усечен (размер инфо-заголовка INFO меньше 40 байт)")
                
            biSize, biWidth, biHeight, biPlanes, biBitCount = struct.unpack('<I i i H H', info_header[:16])
            
            if biBitCount != 24: 
                raise ValueError(f"Неверный формат цвета (biBitCount = {biBitCount}): поддерживаются строго только 24-битные изображения")
                
            total_pixels = abs(biWidth) * abs(biHeight)
            
            if total_pixels != expected_N:
                raise ValueError(f"Несовпадение размеров: количество пикселей в BMP ({total_pixels}) не совпадает с числом ключей в файле ({expected_N})")
        
            bytes_per_pixel = biBitCount // 8
            useful_row_bytes = abs(biWidth) * bytes_per_pixel
            row_size = (useful_row_bytes + 3) // 4 * 4
            padding = row_size - useful_row_bytes
            
            f.seek(bfOffBits)
            pixels = []
            for r in range(abs(biHeight)):
                row_data = f.read(useful_row_bytes)
                if len(row_data) < useful_row_bytes:
                    raise ValueError(f"Файл усечен: невозможно прочитать пиксели на строке {r}")
                    
                for i in range(0, useful_row_bytes, bytes_per_pixel):
                    pixels.append(row_data[i:i+bytes_per_pixel])
                    
                pad_data = f.read(padding)
                if len(pad_data) < padding and r < abs(biHeight) - 1:
                    raise ValueError(f"Файл усечен на байтах выравнивания (padding) строки {r}")
                
            return bfOffBits, biWidth, biHeight, biBitCount, pixels
    except Exception as e:
        print(f"Ошибка при чтении BMP-файла: {e}", file=sys.stderr)
        sys.exit(0)

def write_bmp(shuffled_path, out_path, bfOffBits, biWidth, biHeight, biBitCount, restored_pixels, quiet=False):
    try:
        bytes_per_pixel = biBitCount // 8
        useful_row_bytes = abs(biWidth) * bytes_per_pixel
        padding = ((useful_row_bytes + 3) // 4 * 4) - useful_row_bytes
        
        with open(shuffled_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
            headers = f_in.read(bfOffBits)
            f_out.write(headers)
            
            pixel_idx = 0
            for _ in range(abs(biHeight)):
                row_bytes = b''.join(restored_pixels[pixel_idx:pixel_idx + abs(biWidth)])
                pixel_idx += abs(biWidth)
                f_out.write(row_bytes)
                f_out.write(b'\x00' * padding)
        if not quiet:
            print(f"Файл сохранен: {out_path}")
    except Exception as e:
        if not quiet:
            print(f"Ошибка при записи BMP: {e}", file=sys.stderr)

def main():
    args = sys.argv[1:]
    
    if not args:
        print("Использование: restore --bmp <f> --keys <f> --out <f> [--bench <N>] [--animate <K>]", file=sys.stderr)
        sys.exit(0)

    bmp_path, keys_path, out_path, bench_count, animate_K = None, None, None, None, None
    
    try:
        i = 0
        while i < len(args):
            if args[i] == '--bmp': 
                if i + 1 >= len(args): raise ValueError("После флага --bmp должен идти путь к файлу")
                bmp_path = args[i+1]; i += 2
            elif args[i] == '--keys': 
                if i + 1 >= len(args): raise ValueError("После флага --keys должен идти путь к файлу")
                keys_path = args[i+1]; i += 2
            elif args[i] == '--out': 
                if i + 1 >= len(args): raise ValueError("После флага --out должен идти путь к файлу")
                out_path = args[i+1]; i += 2
            elif args[i] == '--bench': 
                if i + 1 >= len(args): raise ValueError("После флага --bench должно идти целое число проходов")
                try:
                    bench_count = int(args[i+1])
                except ValueError:
                    raise ValueError(f"Параметр флага --bench должен быть целым числом, получено: '{args[i+1]}'")
                i += 2
            elif args[i] == '--animate': 
                if i + 1 >= len(args): raise ValueError("После флага --animate должно идти целое число (шаг кадров)")
                try:
                    animate_K = int(args[i+1])
                except ValueError:
                    raise ValueError(f"Параметр флага --animate должен быть целым числом, получено: '{args[i+1]}'")
                i += 2
            else: 
                raise ValueError(f"Неизвестный параметр: '{args[i]}'")
    except Exception as e:
        print(f"Ошибка параметров: {e}", file=sys.stderr)
        sys.exit(0)

    if not bmp_path or not keys_path or not out_path:
        print("Ошибка: Параметры --bmp, --keys и --out являются обязательными!", file=sys.stderr)
        print("Использование: restore --bmp <f> --keys <f> --out <f> [--bench <N>] [--animate <K>]", file=sys.stderr)
        sys.exit(0)
        
    N, keys = read_keys(keys_path)
    bfOffBits, width, height, bitCount, pixels = read_bmp(bmp_path, N)
    
    bmp_info = (bmp_path, bfOffBits, width, height, bitCount) if animate_K else None
    

    if bench_count and bench_count > 0:
        times = []
        for _ in range(bench_count):
            k_copy, p_copy = list(keys), list(pixels)
            start = time.perf_counter()
            shell_sort_sedgewick(k_copy, p_copy)
            times.append((time.perf_counter() - start) * 1000)
        times.sort()
        print(f"Медиана времени сортировки файла ({bench_count} проходов): {times[len(times)//2]:.2f} мс")
        keys, pixels = k_copy, p_copy
    else:
        shell_sort_sedgewick(keys, pixels, animate_K=animate_K, bmp_info=bmp_info)
        
    write_bmp(bmp_path, out_path, bfOffBits, width, height, bitCount, pixels)

    if animate_K:
        compile_video_from_frames(video_name="sorting_process.mp4", fps=20)

if __name__ == '__main__':
    main()
