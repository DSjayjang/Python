import time
from cffi import FFI

ffi = FFI()
ffi.cdef("int add(int, int);")

# C 코드 구현
C = ffi.verify("""
    int add(int a, int b) {
        return a + b;
    }
""")

# Python 함수 정의
def add_py(a, b):
    return a + b

# 반복 횟수
N = 10_000_000

# C 함수 테스트
start = time.time()
s = 0
for i in range(N):
    s += C.add(i, 1)
print("C loop add time:", time.time() - start, "sec")

# Python 함수 테스트
start = time.time()
s = 0
for i in range(N):
    s += add_py(i, 1)
print("Python loop add time:", time.time() - start, "sec")

"""
함수가 너무 간단해서 반복문 안에서 C를 불러오는 것이 오래걸린다.
>> 반복문을 C로 구현하자. (see main_eg3.py)
"""