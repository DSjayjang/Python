import time
from cffi import FFI

ffi = FFI()
ffi.cdef("long long add_many(int n);")

# C 코드
C = ffi.verify("""
    long long add_many(int n) {
        long long total = 0;
        for (int i = 0; i < n; ++i)
            total += i + 1;
        return total;
    }
""")

# Python 함수 정의
def add_many_py(n):
    total = 0
    for i in range(n):
        total += i + 1
    return total

# C 함수 테스트
start = time.time()
result_c = C.add_many(100_000_000)
print("C total:", result_c)
print("C loop-internal time:", time.time() - start, "sec")

# Python 함수 테스트
start = time.time()
result_py = add_many_py(100_000_000)
print("Python total:", result_py)
print("Python loop-internal time:", time.time() - start, "sec")
