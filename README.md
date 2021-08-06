# Prometheus Cloudflare Exporter

Prometheus exporter powered by Cloudflare GraphQL API.

<p align="left">
<a href="https://github.com/transferwise/cloudflare-exporter/actions"><img alt="Actions Status" src="https://github.com/transferwise/cloudflare-exporter/workflows/Build & Test/badge.svg"></a>
</p>

## Quickstart

Examples:

    $ export CLOUDFLARE_TOKEN='Bearer fbfa1860-410f-45d5-a9d6-c9af96cbd7d2'
    $ mkdir playground
    $ cp example.config.yaml playground/
    # fill in the zones info in playground/example.config.yaml
    $ cfexpose export playground/example.config.yaml

## Example Dashboards
![Grafana 1](static/images/dashboard_1.png?raw=true "Grafana 1")
![Grafana 2](static/images/dashboard_2.png?raw=true "Grafana 2")

# Configuration options

Required environment variables:
* CLOUDFLARE_TOKEN
* CLOUDFLARE_ACCOUNT_TAG

Optional environment variables:
* EXPORTER_PORT

Required permissions for the token:

![Analytics](static/images/APIKey.png?raw=true "Analytics: Read")

# Limits

For up-to-date information, please refer Cloudflare [documentation](https://developers.cloudflare.com/analytics/graphql-api/limits) on APL limits.

GraphQL API access restrictions by license:

    free:
      zones:
        browserPerf1mGroups
        firewallEventsAdaptive
        firewallEventsAdaptiveByTimeGroups
      accounts/zones:
        httpRequests1hGroups
        httpRequests1dGroups
    pro:
      firewallEventsAdaptiveGroups
      healthCheckEvents
      healthCheckEventsGroups
      httpRequests1mGroups
      loadBalancingRequests
      loadBalancingRequestsGroups
    business:
      -
    enterprise:
      firewallRulePreviewGroups
      httpRequests1mByColoGroups
      httpRequests1dByColoGroups
      synAvgPps1mGroups
