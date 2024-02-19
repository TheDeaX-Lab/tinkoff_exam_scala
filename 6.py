import asyncio
from random import choice, randint
from typing import List
from enum import Enum
from dataclasses import dataclass

@dataclass
class Payload:
    data: str

@dataclass
class Address:
    email: str

@dataclass
class Event:
    recipients: List[Address]
    payload: Payload

class Result(Enum):
    Accepted = 1
    Rejected = 2

async def read_data() -> Event:
    await asyncio.sleep(1)
    return Event(
        recipients=[Address(email=f"user{randint(1, 50)}@example.com") for _ in range(randint(1, 10))],
        payload=Payload(data="Пример данных")
    )

async def send_data(dest: Address, payload: Payload) -> Result:
    await asyncio.sleep(randint(1, 3))
    return choice([Result.Accepted, Result.Rejected])

async def perform_operation() -> None:
    events_performing = []
    while True:
        async def wrapper(event, dest, payload):
            return event, dest, await send_data(dest, payload)
        event = await read_data()
        events_performing = list(filter(lambda x: len(x.recipients) > 0, events_performing + [event]))
        tasks = []
        for event in events_performing:
            for dest in event.recipients:
                tasks.append(wrapper(event, dest, event.payload))
        for coro in asyncio.as_completed(tasks):
            event, dest, rs = await coro
            if rs == Result.Accepted: event.recipients.remove(dest)
        # Отладка по количеству наборов данных и количеству оставшихся непройденных запросов
        # print(len(events_performing), [len(event.recipients) for event in events_performing])

asyncio.run(perform_operation())