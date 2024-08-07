from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.service.url_service import delete_expired_urls


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_expired_urls, 'cron', hour=0)
    scheduler.start()
