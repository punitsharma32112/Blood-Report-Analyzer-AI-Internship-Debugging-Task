"""
Celery configuration for Blood Test Analysis System
"""
import os
from celery import Celery
from kombu import Queue

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "blood_test_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["worker_tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "worker_tasks.process_blood_test_analysis": {"queue": "analysis"},
    },
    
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("analysis", routing_key="analysis"),
    ),
    
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task retry configuration
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Task time limits
    task_soft_time_limit=600,  # 10 minutes soft limit
    task_time_limit=900,       # 15 minutes hard limit
    
    # Result backend settings
    result_expires=3600,       # Results expire after 1 hour
    
    # Worker configuration
    worker_log_level="INFO",
    worker_hijack_root_logger=False,
    
    # Beat schedule (for periodic tasks if needed)
    beat_schedule={
        "cleanup-old-results": {
            "task": "worker_tasks.cleanup_old_results",
            "schedule": 3600.0,  # Run every hour
        },
    },
)

# Task autodiscovery
celery_app.autodiscover_tasks() 