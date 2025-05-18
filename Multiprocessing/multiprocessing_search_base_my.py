import os
import multiprocessing
import ctypes
import numpy as np
import time

SIZE = 1_000_000 # 데이터 크기
TARGET = 1000  # 타겟 값
N_PROCESSES = 4  # 프로세스 수 #multiprocessing.cpu_count() 
CHECK_EVERY = 1000 # 플레그 체크 주기

# 플레그
_shared_array = None
_stop_flag = None

# 연산 함수 (고정)
def compute(val):
    if val % 13 != 0:
        return
    x = float(val)
    for _ in range(500):
        x = np.sin(x) + np.log1p(abs(x))

# 전역 공유 변수 초기화
# def init_worker(shared_array_, stop_flag_):
#     global _shared_array
#     global _stop_flag
#     _shared_array = shared_array_
#     _stop_flag = stop_flag_

def worker_fn(start_end):
    global _shared_array, _stop_flag
    start, end = start_end
    for i in range(start, end):
        # 조기 종료 플래그 확인
        if _stop_flag.value:
            return
        val = _shared_array[i]
        compute(val)
        if val == TARGET:
            with _stop_flag.get_lock():
                _stop_flag.value = 1
            return i
        if i % CHECK_EVERY == 0 and _stop_flag.value:
            return
    return

if __name__ == '__main__':
    # 데이터 생성
    arr = np.random.randint(0, 128, size=SIZE, dtype=np.int32)
    target_index = np.random.randint(0, SIZE)
    arr[target_index] = TARGET

    # 공유 배열 / 플레그 생성
    shared_array = multiprocessing.Array(ctypes.c_int, arr, lock = False)
    stop_flag = multiprocessing.Value(ctypes.c_bool, False)

    # 인덱스 나누기
    chunk_size = SIZE // N_PROCESSES
    ranges = [(i * chunk_size, (i + 1) * chunk_size if i != N_PROCESSES - 1 else SIZE)
              for i in range(N_PROCESSES)]

    # 병렬 처리
    t1 = time.time()

    # 프로세스 풀 실행
    pool = multiprocessing.Pool(N_PROCESSES)
    results = pool.map(worker_fn, ranges)

    found_indices = [r for r in results if r is not None]
    t2 = time.time()

    # 결과 확인  
    print(f"연산 시간 {t2 - t1:.2f} 초")
    print(f"타겟 인자: {target_index}")
    print(f"찾은 인자: {found_indices}")
