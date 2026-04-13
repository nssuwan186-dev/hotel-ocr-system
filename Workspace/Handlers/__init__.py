# Handlers/__init__.py
"""
Handlers - จัดการแต่ละประเภทงาน
"""

from .slip_handler import SlipHandler
from .query_handler import QueryHandler
from .booking_handler import BookingHandler
from .report_handler import ReportHandler

__all__ = ["SlipHandler", "QueryHandler", "BookingHandler", "ReportHandler"]
