import os
import multiprocessing
import ctypes
import numpy as np
import time

SIZE = 1_000_000  # 데이터 크기
TARGET = 1000     # 타겟 값
N_PROCESSES = 4   # 프로세스 수
CHECK_EVERY = 1000  # 플래그 확인 주기

# 전역 공유 변수
_shared_array = None
_stop_flag = None

def compute(val):
    """고정된 계산 함수: 13의 배수인 경우에만 연산 수행"""
    if val % 13 != 0:
        return
    x = float(val)
    for _ in range(500):
        x = np.sin(x) + np.log1p(abs(x))

def worker_fn(start_end):
    """각 프로세스가 맡은 구간을 탐색하는 함수"""
    global _shared_array, _stop_flag
    start, end = start_end
    for i in range(start, end):
        # 조기 종료 플래그 확인
        if _stop_flag.value:
            return None

        val = _shared_array[i]
        compute(val)

        if val == TARGET:
            # 타겟 발견 시 플래그 설정
            _stop_flag.value = True
            return i

        # 주기적으로 플래그 확인
        if i % CHECK_EVERY == 0 and _stop_flag.value:
            return None
    return None

if __name__ == '__main__':
    # 데이터 생성
    arr = np.random.randint(0, 128, size=SIZE, dtype=np.int32)
    target_index = np.random.randint(0, SIZE)
    arr[target_index] = TARGET  # 랜덤한 위치에 타겟 삽입

    # 공유 메모리 배열 및 종료 플래그 설정
    _shared_array = multiprocessing.Array(ctypes.c_int32, arr)
    _stop_flag = multiprocessing.Value(ctypes.c_bool, False)

    # 프로세스별 탐색 구간 설정
    chunk_size = SIZE // N_PROCESSES
    ranges = [(i * chunk_size, (i + 1) * chunk_size if i < N_PROCESSES - 1 else SIZE) for i in range(N_PROCESSES)]

    # 병렬 탐색 시작
    t1 = time.time()
    with multiprocessing.Pool(N_PROCESSES, initializer=lambda: None) as pool:
        results = pool.map(worker_fn, ranges)
    t2 = time.time()

    # 결과 처리
    found_indices = [r for r in results if r is not None]
    found_index = found_indices[0] if found_indices else None



    # 결과 확인    
    print(f"연산 시간 {t2 - t1:.2f} 초")
    print(f"타겟 인자: {target_index}")
    print(f"찾은 인자: {found_indices}")

