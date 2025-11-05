# 📊 Grafana Monitoring

## Access

- **URL**: http://localhost:3000
- **Login**: admin
- **Password**: admin (configured via docker-compose)

## Features

- **Datasource**: Postgres database is automatically provisioned
- **Dashboard**: LoFi Pipeline dashboard showing recent events
- **Real-time Monitoring**: Track video generation pipeline execution

## Dashboard Panels

- **Derniers events**: Table view of the 100 most recent events with:
  - Event ID
  - Timestamp
  - Event kind
  - Status (ok/error)

## Customization

You can customize dashboards by:
1. Accessing the Grafana UI
2. Editing existing panels
3. Adding new panels with custom SQL queries
4. Saving your changes

The dashboard configuration is stored in `provisioning/dashboards/dashboard.json`.
