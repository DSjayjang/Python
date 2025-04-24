#cython: boundscheck=False
from cython.parallel import prange, parallel
import numpy as np
cimport numpy as np

# 함수
def hpp_function(np.ndarray[np.float64_t, ndim=1] arr):

    cdef unsigned int i, n
    cdef double a, b
    n = len(arr) - 1
    cdef np.ndarray[np.float64_t, ndim = 1] result = np.empty(n, dtype = np.float64)

    with nogil:
        for i in prange(n, schedule = 'guided', chunksize = 10):
            a = arr[i]
            b = arr[i + 1]
            result[i] = (a * b) / (a + b + 1e-8)
    return result
