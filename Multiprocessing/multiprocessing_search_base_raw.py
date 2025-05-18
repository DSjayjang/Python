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

def worker_fn(start_end):
    # 각 프로세스가 이 함수를 통해 배열의 일부 탐색
    # 목표값(TARGET)을 찾으면 플래그를 설정하고 인덱스 반환
    # compute()는 모든 값에 대해 호출되며, 내부에서 13의 배수인지 확인해 연산을 수행
    return None

if __name__ == '__main__':
    # 데이터 생성
    arr = np.random.randint(0, 128, size=SIZE, dtype=np.int32)
    target_index = np.random.randint(0, SIZE)
    arr[target_index] = TARGET

    # 병렬 처리
    t1 = time.time()
    # 
    #found_indices
    t2 = time.time()

    # 결과 확인    
    print(f"연산 시간 {t2 - t1:.2f} 초")
    print(f"타겟 인자: {target_index}")
    print(f"찾은 인자: {found_indices}")

