from numba import jit
import numpy as np

"""
파이썬 리스트형태
numba를 사용해도 빠르지 않을 것임.
"""
@jit(nopython=False)
def func1(arr):
    result = []
    for x in arr:
        result.append(x ** 2)
    return result

"""
넘파이 array 사용
"""
@jit(nopython=False)
def func2(arr):
    result = np.empty_like(arr)
    for i in range(arr.size):
        result[i] = arr[i] ** 2
    return result


# func1(np.array([1, 2, 3]))
# print(func1.inspect_types())

func2(np.array([1, 2, 3]))
print(func2.inspect_types())
