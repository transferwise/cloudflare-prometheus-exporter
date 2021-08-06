# -*- coding: utf-8 -*-

"""Structured logging module."""

from pythonjsonlogger import jsonlogger
from datetime import datetime
import logging

# TODO:
# level_value
# thread_name
# @version


class CustomJsonFormatter(jsonlogger.JsonFormatter):

    """
    @timestamp - strict_date_optional_time_nanos
      A generic ISO datetime parser, where the date must include the year at a minimum,
      and the time (separated by T), is optional. The fraction of a second part has a nanosecond
      resolution. Examples: yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ or yyyy-MM-dd. ISO 8601
    """

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        log_record["@timestamp"] = now
        # this will always be this file. Which logger should we get?
        log_record["logger_name"] = logging.getLogger(__name__)

        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
