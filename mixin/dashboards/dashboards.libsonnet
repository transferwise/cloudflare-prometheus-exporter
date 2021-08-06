local grafana = import 'github.com/grafana/grafonnet-lib/grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local row = grafana.row;
local prometheus = grafana.prometheus;
local template = grafana.template;
local graphPanel = grafana.graphPanel;


{
  grafanaDashboards+:: {
    'overview.json':
      local cloudflareRequests =
        graphPanel.new(
          'Cloudflare Requests',
          datasource='$datasource',
          span=5,
          format='ops',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=true,
        )
        .addTarget(prometheus.target('cloudflare_exporter_requests{%(selector)s}' % $.config))
        .addTarget(prometheus.target('cloudflare_exporter_requests{%(selector)s}' % $.config))
        .addTarget(prometheus.target('cloudflare_exporter_requests{%(selector)s}' % $.config));

      dashboard.new(
        '%(dashboardNamePrefix)sCloudflare Metrics' % $.config.grafana,
        time_from='now-1h',
        uid=($.config.grafana.dashboardID),
        tags=($.config.grafana.dashboardTags),
      ).addTemplate(
        {
          current: {
            text: 'default',
            value: 'default',
          },
          hide: 0,
          label: null,
          name: 'datasource',
          options: [],
          query: 'prometheus',
          refresh: 1,
          regex: '',
          type: 'datasource',
        },
      )
      .addTemplate(
        template.new(
          'zone',
          '$datasource',
          'label_values(cloudflare_expoeter_status{%(selector)s}, zone)' % $.config,
          refresh='time',
          includeAll=true,
          sort=1,
        )
      )
      .addRow(
        row.new()
        .addPanel(cloudflareRequests)
      ).addRow(
        row.new()
        .addPanel(cloudflareRequests)
      ).addRow(
        row.new()
        .addPanel(cloudflareRequests)
      ).addRow(
        row.new()
        .addPanel(cloudflareRequests)
      ) + { refresh: $.config.grafana.refresh },
  },
}
