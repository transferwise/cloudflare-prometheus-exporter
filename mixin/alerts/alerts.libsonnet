{
  local cloudflare = self,
  config+:: {
    selector: error 'must provide selector for alerts',
  },

  prometheusAlerts+:: {
    groups+: [
      {
        name: 'cloudflare.alerts',
        rules: [
          {
            alert: 'CloudflareResponse5XXRate',
            expr: |||
              rate(cloudflare_responses{
                status_code=~"5.*",
                %(selector)s
              }[10m]) > 1
            ||| % cloudflare.config,
            'for': '0s',
            labels+: {
              severity: 'critical',
            },
            annotations: {
              description: |||
                [{{ $labels.zone }}][{{ $labels.status_code }}] High server side error rate for past 10m
              |||,
              dashboard: |||
                %(dashboardURL)s
              ||| % cloudflare.config,
              runbook_url: |||
                %(runbookURL)s#CloudflareResponse5XXRate
              ||| % cloudflare.config,
            },
          },
          {
            alert: 'PrometheusExporterErrors',
            expr: |||
              rate(prometheus_exporter_metric_collection_errors_total{
                %(selector)s
              }[60m]) > 0
            ||| % cloudflare.config,
            'for': '0s',
            labels+: {
              severity: 'warning',
            },
            annotations: {
              description: |||
                [{{ $labels.zone }}] Metric collection errors during last 60m.
              |||,
              dashboard: |||
                %(dashboardURL)s
              ||| % cloudflare.config,
              runbook_url: |||
                %(runbookURL)s#PrometheusExporterErrors
              ||| % cloudflare.config,
            },
          },
        ],
      },
    ],
  },
}
