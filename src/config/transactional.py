from functools import wraps

from pymongo.client_session import ClientSession

from src.config.database import client


async def get_db_session():
    session = await client.start_session()
    session.start_transaction()
    try:
        yield session
    except Exception:
        await session.abort_transaction()
        raise
    else:
        await session.commit_transaction()
    finally:
        session.end_session()


def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print("transactional 시도")
        db_session = kwargs.get('db_session')
        if db_session is None:
            async for session in get_db_session():
                kwargs['db_session'] = session
                break

        try:
            print("transactional 시작")
            result = await func(*args, **kwargs)
            print("transactional 끝")
            return result
        except Exception as e:
            db_session = kwargs['db_session']
            if db_session and isinstance(db_session, ClientSession):
                await db_session.abort_transaction()
            print("transactional 에러")
            raise e

    return wrapper
