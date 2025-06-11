# 일반 함수
def greet():
    return "Hello"
print(greet())

# 코루틴 함수
async def async_greet():
    return 'hello'

# 객체를 반환함
# 함수 안에 있는 코드는 실행하지 않는다.
print(async_greet())


# await 테스트
import asyncio

async def say_hello():
    await asyncio.sleep(1)
    print('hello')

async def main():
    await say_hello()

asyncio.run(main())


import asyncio

async def task(name, delay):
    print(f"{name} 시작")
    await asyncio.sleep(delay)
    print(f"{name} 종료")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1)
        )

asyncio.run(main())


# .gather() 테스트
import asyncio

async def say_hello(delay):
    await asyncio.sleep(delay)
    return f"Hello after {delay} seconds"

async def main():
    # 3개의 코루틴을 동시에 실행하도록 이벤트 루프에 등록
    # 한 스레드가 하나씩 번갈아 실행행
    results = await asyncio.gather(
        say_hello(1),
        say_hello(2),
        say_hello(3)
        )
    print(results)

asyncio.run(main())


# 동기 vs. 비동기 비교
## 동기
import time

def task(name, delay):
    print(f"{name} 시작")
    time.sleep(delay)
    print(f"{name} 종료")

def main():
    task("A", 2)
    task("B", 1)

main()

## 비동기
import asyncio

async def task(name, delay):
    print(f"{name} 시작")
    await asyncio.sleep(delay) # 잠시 멈춤
    print(f"{name} 종료")

async def main():
		# ready queue에 넣음
    await asyncio.gather(
    task("A", 2),
    task("B", 1)
    )

asyncio.run(main())


# .create_task() 테스트
import asyncio

async def hello(name):
    await asyncio.sleep(1)
    print(f"Hello, {name}")

async def main():
    task = asyncio.create_task(hello("Alice")) # ready queue에 넣음
    print("1")
    await asyncio.sleep(2) # wait에 넣음음
    print("2")

asyncio.run(main())