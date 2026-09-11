# AWS Demo Deployment

The public demo runs as an AWS Lightsail container. It serves the compiled React dashboard and Flask API from the same HTTPS URL, and starts with deterministic synthetic SQLite data. It does not use Trading212 credentials, Redis, Celery, or an external database.

## Prerequisites

- An authenticated AWS CLI identity with Lightsail permissions
- Docker Desktop running
- The Lightsail upload plugin: `brew install aws/tap/lightsailctl`
- A configured AWS region, or `AWS_REGION` set for the deploy command

## Deploy

From the repository root, run:

```bash
./scripts/deploy-aws-lightsail-demo.sh
```

The command builds the demo container, creates a `dividend-tracker-demo` Lightsail Container Service when required, deploys it, and prints its HTTPS URL. The first deployment can take several minutes to become active.

To use a different service name or region:

```bash
SERVICE_NAME=my-dividend-demo AWS_REGION=eu-west-2 ./scripts/deploy-aws-lightsail-demo.sh
```

## Verify

```bash
curl https://YOUR-LIGHTSAIL-URL/health
curl -I https://YOUR-LIGHTSAIL-URL/
curl -i "https://YOUR-LIGHTSAIL-URL/download?year=2026"
```

The health endpoint returns `{"status":"healthy"}`. The root path serves the dashboard, and the download endpoint returns `404` because the demo does not expose the Trading212 sync operation.

## README Link

After deployment, replace the placeholder demo URL in [README.md](../README.md) with the HTTPS URL printed by the script. A Lightsail service URL remains stable across deployments of that service.

## Cost and Scope

Lightsail Container Services are billable AWS resources. Use the `nano` power setting only for this portfolio demonstration and delete the service when it is no longer needed:

```bash
aws lightsail delete-container-service --service-name dividend-tracker-demo --region YOUR_REGION
```

This deployment is intentionally not the private Trading212 ETL environment. The real pipeline requires separate secure infrastructure for PostgreSQL, Redis, Celery, and Trading212 credentials.