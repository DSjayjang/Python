from cffi import FFI

# ffi 객체 생성
ffi = FFI() 

# C 함수 시그니처 선언
ffi.cdef("int add(int, int);")

# C 코드 구현 
C = ffi.verify("""
    int add(int a, int b) {
        return a + b;
    }
""")

# 사용
print("3 + 5 =", C.add(3, 5))
