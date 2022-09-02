local grafana = import 'github.com/grafana/grafonnet-lib/grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local row = grafana.row;
local prometheus = grafana.prometheus;
local template = grafana.template;
local graphPanel = grafana.graphPanel;


{
  grafanaDashboards+:: {
    'overview.json':
      local errorTimeline =
        graphPanel.new(
          'Errors',
          datasource='$datasource',
          span=12,
          format='errors',
          min=0,
          legend_show=false,
          legend_values=false,
          legend_current=false,
          legend_alignAsTable=false,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone, service, cluster) (prometheus_exporter_metric_collection_errors_total{%(selector)s})' % $.config));

      local cloudflareRequests =
        graphPanel.new(
          'Requests',
          datasource='$datasource',
          span=12,
          format='ops',
          min=0,
          legend_show=true,
          legend_sideWidth=400,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=true,
        )
        .addTarget(prometheus.target('sum by (zone, country) (cloudflare_requests_detailed{%(selector)s})' % $.config));

      local cloudflareBytes =
        graphPanel.new(
          'Bytes',
          datasource='$datasource',
          span=12,
          format='bps',
          min=0,
          legend_show=true,
          legend_sideWidth=400,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=true,
        )
        .addTarget(prometheus.target('sum by (zone, country) (cloudflare_bytes_detailed{%(selector)s})' % $.config));

      local cloudflareThreats =
        graphPanel.new(
          'Threats',
          datasource='$datasource',
          span=12,
          format='tps',
          min=0,
          legend_show=true,
          legend_sideWidth=400,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=true,
        )
        .addTarget(prometheus.target('sum by (zone, country) (cloudflare_threats_detailed{%(selector)s})' % $.config));

      local cloudflareAvgRequestSizeBytes =
        graphPanel.new(
          'Average Bytes per Request',
          datasource='$datasource',
          span=12,
          format='bps',
          min=0,
          legend_show=true,
          legend_sideWidth=400,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=true,
        )
        .addTarget(
          prometheus.target(
            |||
              sum by (zone, country) (
                cloudflare_bytes_detailed{%(selector)s}
              ) /
              sum by (zone, country) (
                cloudflare_requests_detailed{%(selector)s}
              )
            ||| % $.config
          )
        );

      local cloudflareThreatsByZone =
        graphPanel.new(
          'Threats',
          datasource='$datasource',
          span=6,
          format='tps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_threats{%(selector)s})' % $.config));

      local cloudflarePageViewsByZone =
        graphPanel.new(
          'Page Views',
          datasource='$datasource',
          span=6,
          format='tps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_pageViews{%(selector)s})' % $.config));

      local cloudflareRequestsByZone =
        graphPanel.new(
          'Requests',
          datasource='$datasource',
          span=4,
          format='rps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_requests{%(selector)s})' % $.config));

      local cloudflareCachedRequestsByZone =
        graphPanel.new(
          'Cached Requests',
          datasource='$datasource',
          span=4,
          format='rps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_cachedRequests{%(selector)s})' % $.config));

      local cloudflareEncryptedRequestsByone =
        graphPanel.new(
          'Encrypted Requests',
          datasource='$datasource',
          span=4,
          format='rps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_encryptedRequests{%(selector)s})' % $.config));

      local cloudflareBytesByZone =
        graphPanel.new(
          'Traffic in bytes',
          datasource='$datasource',
          span=4,
          format='bps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_bytes{%(selector)s}) / 60' % $.config));

      local cloudflareCachedBytesByZone =
        graphPanel.new(
          'Traffic in bytes (cached)',
          datasource='$datasource',
          span=4,
          format='bps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_cachedBytes{%(selector)s}) / 60' % $.config));

      local cloudflareEncryptedBytesByone =
        graphPanel.new(
          'Traffic in bytes (encrypted)',
          datasource='$datasource',
          span=4,
          format='bps',
          min=0,
          legend_show=true,
          legend_values=true,
          legend_current=true,
          legend_alignAsTable=true,
          legend_rightSide=false,
        )
        .addTarget(prometheus.target('sum by (zone) (cloudflare_encryptedBytes{%(selector)s}) / 60' % $.config));

      dashboard.new(
        '%(dashboardNamePrefix)sCloudflare Metrics' % $.config.grafana,
        time_from='now-1h',
        graphTooltip='shared_crosshair',
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
        {
          hide: 0,
          label: null,
          name: 'logs',
          options: [],
          query: 'loki',
          refresh: 1,
          regex: '',
          type: 'datasource',
        },
      )

      .addTemplate(
        template.new(
          'namespace',
          '$datasource',
          'label_values(prometheus_exporter_metric_collection_errors_total, namespace)',
          refresh='time',
          includeAll=true,
          sort=1,
        )
      )
      .addTemplate(
        template.new(
          'zone',
          '$datasource',
          'label_values(prometheus_exporter_metric_collection_errors_total{namespace="$namespace"}, zone)' % $.config,
          refresh='time',
          includeAll=true,
          sort=1,
        )
      )
      .addRow(
        row.new(collapse=true, title='Exporter health')
        .addPanel(errorTimeline)
        .addPanel(
          (import 'logs.json')
        )
      ).addRow(
        row.new(title='Requests on map')
        .addPanel(
          (import 'requestMap.json')
        )
        .addPanel(
          (import 'threatMap.json')
        )
      )
      .addRow(
        row.new(collapse=true, title='Overview')
        .addPanel(cloudflareRequests)
        .addPanel(cloudflareThreats)
        .addPanel(cloudflareBytes)
      ).addRow(
        row.new(collapse=true, title='Average Request')
        .addPanel(cloudflareAvgRequestSizeBytes)
      ).addRow(
        row.new(collapse=true, title='Top Level Overview')
        .addPanels(
          [
            cloudflarePageViewsByZone,
            cloudflareThreatsByZone,
          ]
        )
        .addPanels(
          [
            cloudflareRequestsByZone,
            cloudflareCachedRequestsByZone,
            cloudflareEncryptedRequestsByone,
          ]
        )
        .addPanels(
          [
            cloudflareBytesByZone,
            cloudflareCachedBytesByZone,
            cloudflareEncryptedBytesByone,
          ]
        )
      )
      + { refresh: $.config.grafana.refresh },
  },
}
