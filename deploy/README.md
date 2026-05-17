# Deployment

Production deployment for Landolfio runs as a Docker Compose stack on the
`landolfio.vofdoesburg.nl` AWS EC2 VM, orchestrated by
`.github/workflows/deploy.yaml`. It fires after the `Build and push` workflow
publishes a fresh `:latest` image to GHCR on `master`.

The deploy runs on a **self-hosted GitHub Actions runner installed on the VM
itself**. The runner polls GitHub over outbound HTTPS; GitHub never connects
inbound. This avoids needing inbound SSH from GitHub-hosted runners.

## Contents of this directory

| File | Purpose |
| --- | --- |
| `docker-compose.yml` | Service definitions: `caddy`, `database`, `web`, `task-worker`, `task-scheduler`. All tuneable values come from `.env`. |
| `Caddyfile` | Caddy reverse proxy config for `landolfio.vofdoesburg.nl`. |
| `.env.example` | Template for the `.env` file the workflow writes on the VM. Never commit a real `.env`. |

## VM prerequisites (one-time setup)

These commands run as `ubuntu` (the EC2 functional user) with sudo.

```bash
# Docker Engine + Compose plugin (skip if already installed).
curl -fsSL https://get.docker.com | sudo sh

# System users.
sudo useradd --system --create-home --shell /bin/bash deploy-landolfio
sudo useradd --system --create-home --shell /bin/bash --groups docker github-runner
sudo usermod -aG deploy-landolfio github-runner

# Deploy directory owned by deploy-landolfio, group-writable so the runner can write.
sudo mkdir -p /opt/landolfio
sudo chown deploy-landolfio:deploy-landolfio /opt/landolfio
sudo chmod 770 /opt/landolfio
```

The compose stack lives in `/opt/landolfio` and Postgres data persists in the
named volume `landolfio_pg-data` (managed by Docker).

### Installing the self-hosted runner

Follow [GitHub's self-hosted runner instructions](https://github.com/jobdoesburg/landolfio/settings/actions/runners/new)
— they show the exact `curl` + `./config.sh` commands for the current runner
version. Run them as the `github-runner` user (`sudo -iu github-runner`).
Use these settings:

- **Runner name**: `landolfio-vm`.
- **Labels**: `landolfio-vm,production`. `landolfio-vm` identifies the
  machine; `production` is the tier that `deploy.yaml`'s `runs-on:` filters on.
- **Install as a service**: `sudo ./svc.sh install github-runner && sudo ./svc.sh start`.

## GitHub Environment

The workflow runs against a GitHub Environment named
**`landolfio.vofdoesburg.nl`**. Scope secrets to this Environment
(Settings → Environments) so workflows on other branches cannot exfiltrate
them. Add required reviewers for extra safety — every deploy then waits for
human approval.

### Environment secrets

| Secret | Purpose |
| --- | --- |
| `LANDOLFIO_SECRET_KEY` | Django secret key. |
| `POSTGRES_PASSWORD` | Postgres password. |
| `SENTRY_DSN` | Sentry DSN for error reporting. |
| `MONEYBIRD_API_KEY` | Moneybird API token. |
| `MONEYBIRD_WEBHOOK_TOKEN` | Moneybird webhook signing token. |
| `NINOX_API_TOKEN` | Ninox API token. |
| `AWS_ACCESS_KEY_ID` | AWS access key for S3 media bucket. |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key. |
| `SMTP_PASSWORD` | Outgoing SMTP password. |

### Environment variables (not secret)

| Variable | Example | Purpose |
| --- | --- | --- |
| `DEPLOY_DIR` | `/opt/landolfio` | Where the compose stack lives on the VM. |
| `DJANGO_HOSTNAME` | `landolfio.vofdoesburg.nl` | The single hostname Caddy terminates TLS for and serves directly on this VM. Also used as the `Host:` header for the web healthcheck. |
| `DJANGO_ALLOWED_HOSTS` | `landolfio.vofdoesburg.nl,landolfio.jobdoesburg.dev` | Django's allowlist (comma-separated). Include `DJANGO_HOSTNAME` plus any hostname that reaches Django via an upstream reverse proxy. |
| `DJANGO_LOG_LEVEL` | `INFO` | Django log level. |
| `MONEYBIRD_ADMINISTRATION_ID` | `123456789` | Moneybird administration ID. |
| `MONEYBIRD_WEBHOOK_ID` | `…` | Moneybird webhook ID. |
| `MONEYBIRD_MARGIN_ASSETS_LEDGER_ACCOUNT_ID` | `…` | Ledger account for margin assets. |
| `MONEYBIRD_NOT_MARGIN_ASSETS_LEDGER_ACCOUNT_ID` | `…` | Ledger account for non-margin assets. |
| `NINOX_TEAM_ID` | `…` | Ninox team ID. |
| `NINOX_DATABASE_ID` | `…` | Ninox database ID. |
| `AWS_STORAGE_BUCKET_NAME` | `landolfio-media` | S3 bucket for media uploads. |
| `AWS_S3_REGION_NAME` | `eu-west-1` | S3 region. |
| `SMTP_HOST` | `smtp.example.com` | Outgoing SMTP server. |
| `SMTP_PORT` | `587` | SMTP port. |
| `SMTP_USE_TLS` | `True` | Use STARTTLS. |
| `SMTP_USE_SSL` | `False` | Use implicit TLS. |
| `SMTP_USER` | `notifications@…` | SMTP username. |
| `SMTP_FROM` | `notifications@…` | Envelope sender. |
| `SMTP_FROM_EMAIL` | `Landolfio <notifications@…>` | RFC From: header. |
| `NOTIFICATION_EMAIL` | `contact@vofdoesburg.nl` | Where Django sends internal notifications. |
| `PUBLIC_CONTACT_EMAIL` | `contact@vofdoesburg.nl` | Public contact address shown in the UI. |

## What the workflow does

Runs directly on the VM via the self-hosted runner:

1. Checks out the commit that produced the freshly pushed image.
2. Copies `docker-compose.yml` and `Caddyfile` from the repo into `$DEPLOY_DIR/`.
3. Writes `$DEPLOY_DIR/.env` (mode 600) from the Environment's secrets and vars.
4. Runs `docker compose pull && docker compose up -d --remove-orphans`.
5. Polls `docker inspect` until the `web` container reports `healthy`; fails
   the job if it doesn't within ~5 minutes.

## Image tags

| Source | Tags applied |
| --- | --- |
| Push to `master` | `sha-<40-char-sha>`, `latest` |
| Published release `v1.2.3` | `sha-<40-char-sha>`, `1.2.3`, `1.2`, `1`, `latest` (unless pre-release) |

To cut a release: on GitHub → Releases → "Draft a new release" → create a new
tag `vX.Y.Z` targeting `master` → "Generate release notes" → publish. The
`Build and push` workflow runs on the `release: published` event and pushes
the image with the semver tags.

## Rollback

Every build is published with an immutable `sha-<commit-sha>` tag, and every
release adds semver tags. To roll back:

```bash
ssh ubuntu@landolfio.vofdoesburg.nl
sudo -iu deploy-landolfio
cd /opt/landolfio
# Edit docker-compose.yml to pin a previous image. Prefer a semver tag:
#   image: ghcr.io/jobdoesburg/landolfio:1.2.3
# Or an exact commit:
#   image: ghcr.io/jobdoesburg/landolfio:sha-abc123...
docker compose up -d
```

## Security notes

- The runner executes any code that lands on `master`. Branch protection on
  `master` + required reviewers on the `landolfio.vofdoesburg.nl` Environment
  are the main defenses.
- The `github-runner` user should not have sudo. If it needs elevated
  privileges for something specific, use a tightly scoped sudoers rule.
- Never enable "Run workflows from fork pull requests" without approval — a
  malicious PR could exfiltrate secrets or run commands on the VM.
