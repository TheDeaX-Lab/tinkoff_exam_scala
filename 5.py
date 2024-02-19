# Тесты проводились на версии python 3.11
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import asyncio

timeout_seconds = timedelta(seconds=15).total_seconds()

class Response(Enum):
    Success = 1
    RetryAfter = 2
    Failure = 3

class ApplicationStatusResponse(Enum):
    Success = 1
    Failure = 2

@dataclass
class ApplicationResponse:
    application_id: str
    status: ApplicationStatusResponse
    description: str
    last_request_time: datetime
    retriesCount: Optional[int]

async def send_request(url, params):
    try:
        async with asyncio.timeout(timeout_seconds):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    return Response.Success
    except asyncio.TimeoutError:
        return Response.RetryAfter
    except:
        return Response.Failure

async def get_application_status1(identifier: str) -> Response:
    return await send_request("https://httpbin.org/get", {'identifier': identifier})

async def get_application_status2(identifier: str) -> Response:
    return await send_request("https://httpbin.org/get", {'identifier': identifier})

async def perform_operation(identifier: str) -> ApplicationResponse:
    async def worker_checker(f):
        count_retries = 0
        while True:
            lst_datetime = datetime.now()
            rs = await f()
            if rs in [Response.Success, Response.Failure]:
                break
            count_retries += 1
        return rs, count_retries, lst_datetime
    
    for coro in asyncio.as_completed([
        worker_checker(lambda: get_application_status1(identifier)),
        worker_checker(lambda: get_application_status2(identifier))
    ]):
        rs, count_retries, lst_datetime = await coro
        if rs == Response.Success: break
    if rs == Response.Success:
        return ApplicationResponse(
            application_id=identifier,
            status=ApplicationStatusResponse.Success,
            description="Не описано что нужно передавать",
            last_request_time=lst_datetime,
            retriesCount=count_retries
        )
    else:
        return ApplicationResponse(
            application_id=identifier,
            status=ApplicationStatusResponse.Failure,
            description="Не описано что нужно передавать",
            last_request_time=None,
            retriesCount=None
        )