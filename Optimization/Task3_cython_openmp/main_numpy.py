# 넘파이 기반 main 파일
import time
import numpy as np
import cythonfn



###################데이터 생성 코드#####################
# NumPy 배열 생성
size = 20**6
arr = np.linspace(1.0, 100.0, size).astype(np.float64)
######################################################

# 실행
start = time.time()
result = cythonfn.hpp_function(arr)
end = time.time()

print(f"Result: {sum(result):.6f}")
print(f"Execution time: {end - start:.4f} seconds")

