{
  config+:: {
    selector: 'zone=~"$zone", namespace="$namespace"',
    alertSelector: '',
    runbookURL: 'https://127.0.0.1/Cloudflare+Runbook',
    grafana: {
      url: 'https://127.0.0.1',
      refresh: '10m',
      dashboard: '/d/12bda154-05a7-4939-b124-5b692f290866/cloudflare-metrics',
      dashboardID: '12bda154-05a7-4939-b124-5b692f290866',
      dashboardTags: [],
      dashboardNamePrefix: '',
    },
  },
}
