# List
import timeit

l1 = list(range(10))
timeit.timeit('l1', number = 10000, globals = globals())

l2 = list(range(10_000_000))
timeit.timeit('l2', number = 10000, globals = globals())

# 리스트에서 특정 항목 찾기
def linear_search(needle, array):
    for i, item in enumerate(array):
        if item == needle:
            return i
        return -1
    
# append
numbers = [5, 8, 1, 3, 2, 6]
len(numbers)

numbers.append(42)
numbers
len(numbers)


######################################################
# tuple
t = (1, 2, 3, 4)
t[0] = 5


######################################################
# 리스트 & 튜플 생성 속도 비교
import timeit

list_time = timeit.timeit(stmt = 'list(range(10_000_000))', number = 10)
tuple_time = timeit.timeit(stmt = 'tuple(range(10_000_000))', number = 10)

print(f'List 생성 속도:, {list_time:.6f}초')
print(f'Tuple 생성 속도:, {tuple_time:.6f}초')

# 리스트 & 튜플 메모리 사용량 비교
import sys

list_data = list(range(10_000_000))
tuple_data = tuple(list_data)

print(f'List 메모리 사용량: {sys.getsizeof(list_data)} bytes')
print(f'Tuple 메모리 사용량: {sys.getsizeof(tuple_data)} bytes')

# 리스트 & 튜플 Sum 연산 비교
setup_list = """
list_data = list(range(10_000_000))
"""

setup_tuple = """
tuple_data = tuple(range(10_000_000))
"""

list_time = timeit.timeit('sum(list_data)', setup = setup_list, number = 10)
tuple_time = timeit.timeit('sum(tuple_data)', setup = setup_tuple, number = 10)

print(f'List sum() 실행 시간:, {list_time:.6f}초')
print(f'Tuple sum() 실행 시간:, {tuple_time:.6f}초')


# 리스트 & 튜플 반복문 실행 속도 비교
setup_list = """
list_data = [i for i in range(10_000_000)]
"""

setup_tuple = """
tuple_data = tuple(range(10_000_000))
"""

list_time = timeit.timeit('for x in list_data: pass', setup = setup_list, number = 10)
tuple_time = timeit.timeit('for x in tuple_data: pass', setup = setup_tuple, number = 10)

print(f'List 반복문 속도:, {list_time:.6f}초')
print(f'Tuple 반복문 속도:, {tuple_time:.6f}초')

# 리스트 & 튜플 인덱스 접근 속도 비교
setup_list = """
import random
list_data = [i for i in range(10_000_000)]
indices = [random.randint(0, 10_000_000 -1) for _ in range(1_000_000)]
"""

setup_tuple = """
import random
tuple_data = tuple(range(10_000_000))
indices = [random.randint(0, 10_000_000 -1) for _ in range(1_000_000)]
"""

list_time = timeit.timeit('for i in indices: x = list_data[i]', setup = setup_list, number = 10)
tuple_time = timeit.timeit('for i in indices: x = tuple_data[i]', setup = setup_tuple, number = 10)

print(f'List 인덱스 접근 속도:, {list_time:.6f}초')
print(f'Tuple 인덱스 접근 속도:, {tuple_time:.6f}초')
