"""
Workers package for ApplyForge
"""
from workers.celery_app import celery_app

__all__ = ["celery_app"]
