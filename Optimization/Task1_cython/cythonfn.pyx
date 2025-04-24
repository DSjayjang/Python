# 함수
def hpp_function(arr):

    cdef unsigned int i
    cdef double complex a, b

    result = [0.0] * (len(arr) - 1)

    for i in range(len(arr) - 1):
        a = arr[i]
        b = arr[i + 1]
        result[i] = (a * b) / (a + b + 1e-8)
    return result