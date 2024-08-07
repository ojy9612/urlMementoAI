from functools import wraps

from src.config.database import client


def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with await client.start_session() as session:
            async with session.start_transaction():
                try:
                    print("transactional 시작")
                    kwargs['db_session'] = session
                    result = await func(*args, **kwargs)
                    await session.commit_transaction()
                    print("transactional 끝")
                    return result
                except Exception as e:
                    await session.abort_transaction()
                    print("transactional 에러")
                    raise Exception(e)

    return wrapper
