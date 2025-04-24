# 리스트 기반 main 파일
import time

# 함수
def hpp_function(arr):
    result = [0.0] * (len(arr) - 1)
    for i in range(len(arr) - 1):
        a = arr[i]
        b = arr[i + 1]
        result[i] = (a * b) / (a + b + 1e-8)
    return result


###################데이터 생성 코드#####################
# 순수 파이썬용 데이터 생성 (리스트)
def generate_input(start, stop, num):
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]

size = 20**6
arr = generate_input(1.0, 100.0, size)
######################################################

# 실행
start = time.time()
result = hpp_function(arr)
end = time.time()

print(f"Result: {sum(result):.6f}")
print(f"Execution time: {end - start:.4f} seconds")

