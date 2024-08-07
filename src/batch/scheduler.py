import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.service.url_service import delete_expired_urls


def start_scheduler():
    scheduler = AsyncIOScheduler()
    timezone = pytz.timezone('Asia/Seoul')
    scheduler.add_job(delete_expired_urls, 'cron', hour=0, timezone=timezone)
    scheduler.start()
