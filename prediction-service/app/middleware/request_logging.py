# request_logger.py
import time
from fastapi import Request, Response
from loguru import logger

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)

    logger.info(
        f"request path={request.url.path}, request method={request.method}, "
        f"response status code={response.status_code}, request process time={formatted_process_time}ms"
    )

    return response
