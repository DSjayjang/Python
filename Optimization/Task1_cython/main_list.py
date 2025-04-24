# 리스트 기반 main 파일
import time
import cythonfn


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
result = cythonfn.hpp_function(arr)
end = time.time()

print(f"Result: {sum(result):.6f}")
print(f"Execution time: {end - start:.4f} seconds")

