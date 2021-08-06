# -*- coding: utf-8 -*-

from prometheus_client import Gauge, Enum, Histogram, Counter
import logging

LOGGER = logging.getLogger(__name__)


class CloudflareHttpMetrics:
    _requests = Gauge("cloudflare_requests", "", ["zone", "timerange_seconds"])
    _cachedBytes = Gauge("cloudflare_cachedBytes", "", ["zone", "timerange_seconds"])
    _cachedRequests = Gauge(
        "cloudflare_cachedRequests", "", ["zone", "timerange_seconds"]
    )
    _bytes = Gauge("cloudflare_bytes", "", ["zone", "timerange_seconds"])
    _encryptedBytes = Gauge(
        "cloudflare_encryptedBytes", "", ["zone", "timerange_seconds"]
    )
    _encryptedRequests = Gauge(
        "cloudflare_encryptedRequests", "", ["zone", "timerange_seconds"]
    )
    _pageViews = Gauge("cloudflare_pageViews", "", ["zone", "timerange_seconds"])
    _threats = Gauge("cloudflare_threats", "", ["zone", "timerange_seconds"])

    # Buckets/Maps
    _responseCodes = Gauge(
        "cloudflare_responses", "", ["zone", "status_code", "timerange_seconds"]
    )
    _requests_new = Gauge(
        "cloudflare_requests_detailed", "", ["zone", "country", "timerange_seconds"]
    )
    _bytes_new = Gauge(
        "cloudflare_bytes_detailed", "", ["zone", "country", "timerange_seconds"]
    )
    _threats_new = Gauge(
        "cloudflare_threats_detailed", "", ["zone", "country", "timerange_seconds"]
    )

    CLOUDFLARE_1H_BUCKETS = [
        # datetime.time 24x hour buckets
        #  can I have datetime buckets?
        0.1,
        1.0,
        float("inf"),
    ]
    # potential metric explosion?
    _responseStatusMap = Histogram(
        "cloudflare_responseStatusMap", "", buckets=CLOUDFLARE_1H_BUCKETS
    )


class ExporterInternalMetrics:
    _metric_collection_errors = Counter(
        "prometheus_exporter_metric_collection_errors_total",
        "",
        ["zone", "timerange_seconds"],
    )
