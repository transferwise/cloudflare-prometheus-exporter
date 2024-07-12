# -*- coding: utf-8 -*-

"""Main module."""
import os
import time
import datetime
import logging
import prometheus_client
import requests
from pprint import pprint as pp
from .metrics import CloudflareHttpMetrics, ExporterInternalMetrics
from cloudflare_exporter import gql

import threading
import schedule

MONITOR = CloudflareHttpMetrics()
INTERNAL_MONITOR = ExporterInternalMetrics()
LOGGER = logging.getLogger(__name__)

CF_GQL_URL = os.getenv(
    "CLOUDFLARE_GQL_API", "https://api.cloudflare.com/client/v4/graphql"
)
CF_HEADERS = {
    "content-type": "application/json",
    "Authorization": "Bearer %s" % os.getenv("CLOUDFLARE_TOKEN"),
}
CF_ACCOUNT_TAG = os.getenv("CLOUDFLARE_ACCOUNT_TAG")
EXPORTER_PORT = os.getenv("EXPORTER_PORT", 5000)


class CloudflareExporter:
    def get_metrics(self, query, variables):
        request = requests.post(
            CF_GQL_URL,
            json={"query": query, "variables": variables},
            headers=CF_HEADERS,
        )
        if not request.status_code == 200:
            LOGGER.warning("Bad request.", extra={"status_code": request.status_code})
        return request

    def set_metric_values(self, metrics, zone, timerange):

        MONITOR._requests.labels(zone, timerange).set(metrics["requests"])
        MONITOR._cachedBytes.labels(zone, timerange).set(metrics["cachedBytes"])
        MONITOR._cachedRequests.labels(zone, timerange).set(metrics["cachedRequests"])
        MONITOR._bytes.labels(zone, timerange).set(metrics["bytes"])
        MONITOR._encryptedBytes.labels(zone, timerange).set(metrics["encryptedBytes"])
        MONITOR._encryptedRequests.labels(zone, timerange).set(
            metrics["encryptedRequests"]
        )
        MONITOR._pageViews.labels(zone, timerange).set(metrics["pageViews"])
        MONITOR._threats.labels(zone, timerange).set(metrics["threats"])
        # Explore Maps
        for country, data in metrics["countryMap"].items():
            MONITOR._requests_new.labels(zone, country, timerange).set(data["requests"])
            MONITOR._bytes_new.labels(zone, country, timerange).set(data["bytes"])
            MONITOR._threats_new.labels(zone, country, timerange).set(data["threats"])
        for status_code, count in metrics["responseStatusMap"].items():
            MONITOR._responseCodes.labels(zone, status_code, timerange).set(count)


EXPORTER = CloudflareExporter()


def parser_httpRequests1hGroups(
    raw_data,
    endpoint="zones",
    zone="",
    query_key="httpRequests1hGroups",
    timerange=86400,
):
    if raw_data.get("data"):
        data = raw_data["data"]["viewer"][endpoint][0]
        profile = {
            "clientHTTPVersionMap": [],
            "responseStatusMap": [],
            "threatPathingMap": [],
            "contentTypeMap": [],
            "ipClassMap": [],
            "countryMap": [],
            "browserMap": [],
            "bytes": 0,
            "cachedBytes": 0,
            "encryptedBytes": 0,
            "requests": 0,
            "cachedRequests": 0,
            "encryptedRequests": 0,
            "pageViews": 0,
            "threats": 0,
        }
        if len(data) > 1:
            # ZONE!
            INTERNAL_MONITOR._metric_collection_errors.labels(zone, timerange).inc()
            LOGGER.warning(
                f"more than 1 {endpoint} in API response, monitoring only the first in list"
            )

        response_histogram = data[query_key]
        if response_histogram:
            for element in response_histogram:
                # asigning metrics to correct histogram buckets
                #  feels like too much work for now.
                metrics = element["sum"]
                for key, value in metrics.items():
                    profile[key] += value
            profile = parse_maps(profile)
            return profile
        else:
            return []  # Not to modify httpRequests1hGroups type
    else:
        INTERNAL_MONITOR._metric_collection_errors.labels(zone, timerange).inc()
        LOGGER.error(f"Failed to parse response", extra={"zone": zone})


def parse_responseStatusMap(responseStatusMap):
    responses = {_["edgeResponseStatus"]: 0 for _ in responseStatusMap}
    for item in responseStatusMap:
        responses[item["edgeResponseStatus"]] += item["requests"]
    return responses


def parse_countryMap(countryMap):
    countries = {
        _["clientCountryName"]: {
            "bytes": 0,
            "requests": 0,
            "threats": 0,
        }
        for _ in countryMap
    }
    for item in countryMap:
        countries[item["clientCountryName"]]["bytes"] += item["bytes"]
        countries[item["clientCountryName"]]["threats"] += item["threats"]
        countries[item["clientCountryName"]]["requests"] += item["requests"]
    return countries


def parse_maps(profile):
    profile["responseStatusMap"] = parse_responseStatusMap(profile["responseStatusMap"])
    profile["countryMap"] = parse_countryMap(profile["countryMap"])
    return profile


def job(
    gql_api=None, zone=None, zone_id=None, timerange=86400, scrape_shift_seconds=60
):
    # LOGGER.debug(gql_api, timerange)
    # LOGGER.debug(f"Scraping metrics for {gql_api}", extra={"thread": threading.current_thread()})
    query = gql.query.zones.get(gql_api)
    scrape_shift = datetime.timedelta(seconds=scrape_shift_seconds)
    timerange_end = (
        datetime.datetime.utcnow() - scrape_shift
    )  # Create artificial delay, because CF metrics have a delay.
    timerange_start = timerange_end - datetime.timedelta(seconds=timerange)
    DATETIME_LT = timerange_end.strftime("%Y-%m-%dT%H:%M:%SZ")
    DATETIME_GT = timerange_start.strftime("%Y-%m-%dT%H:%M:%SZ")
    variables = {
        # "accountTag": CF_ACCOUNT_TAG,
        "zoneTag": zone_id,
        "datetime_gt": DATETIME_GT,
        "datetime_lt": DATETIME_LT,
    }

    LOGGER.debug(f"calling cloudflare with variables: {variables}")
    raw_data = EXPORTER.get_metrics(
        query, variables
    ).json()  # What if, when it's not json.
    errors = raw_data.get("errors")
    if errors:
        LOGGER.error(errors, extra=variables)

    LOGGER.debug(raw_data)
    metrics = parser_httpRequests1hGroups(
        raw_data, endpoint="zones", zone=zone, query_key=gql_api, timerange=timerange
    )

    if metrics:
        EXPORTER.set_metric_values(metrics, zone, timerange)
    else:
        LOGGER.info(f"No metrics for given variables.", extra=variables)


def run_threaded(job_func, **kwargs):
    job_thread = threading.Thread(target=job_func(**kwargs))
    job_thread.start()


def run_exporter(config):

    #  https://schedule.readthedocs.io/en/stable/faq.html#how-to-execute-jobs-in-parallel
    prometheus_client.start_http_server(int(EXPORTER_PORT))
    monitored_zones = config["zones"]

    # Sane default values to work with free tier
    query_key = config.get("api", "httpRequests1hGroups")
    timerange_seconds = config.get("timerange_seconds", int(86400))
    scrape_interval_seconds = config.get("scrape_interval_secondss", int(86400))
    scrape_shift_seconds = config.get("scrape_shift_seconds", int(60))

    for zone, settings in monitored_zones.items():

        zone_id = config["zones"][zone]["zone_id"]
        # Zone specific monitoring overrides
        query_key = config["zones"][zone].get("api", query_key)
        timerange_seconds = config["zones"][zone].get(
            "timerange_seconds", timerange_seconds
        )
        scrape_interval_seconds = config["zones"][zone].get(
            "scrape_interval_seconds", scrape_interval_seconds
        )
        scrape_shift_seconds = config["zones"][zone].get(
            "scrape_shift_seconds", scrape_shift_seconds
        )

        # Initialize error counter
        INTERNAL_MONITOR._metric_collection_errors.labels(zone, timerange_seconds).inc(
            0
        )
        schedule.every(scrape_interval_seconds).seconds.do(
            run_threaded,
            job,
            gql_api=query_key,
            timerange=timerange_seconds,
            scrape_shift_seconds=scrape_shift_seconds,
            zone=zone,
            zone_id=zone_id,
        )
    while True:
        schedule.run_pending()
        time.sleep(1)
