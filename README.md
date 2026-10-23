# Dockerized Web App

A minimal, dependency-free Python web app packaged as a Docker image. This project demonstrates core delivery fundamentals: a small container, a non-root runtime, an HTTP health endpoint, automated tests, dependency/secret scanning, and a CI smoke test.

[![Docker Web App CI](https://github.com/nagateja-2002/dockerwebapp/actions/workflows/ci.yml/badge.svg)](https://github.com/nagateja-2002/dockerwebapp/actions/workflows/ci.yml)

## Features

- Responsive static landing page served by Python's standard-library HTTP server
- `GET /` serves the application UI
- `GET /health` returns JSON for container/orchestrator health checks
- Security response headers for common browser protections
- Docker image runs as non-root UID/GID `10001:10001`
- Image includes a Docker `HEALTHCHECK`
- Unit tests use Python's standard library (no application test dependencies)
- GitHub Actions runs tests, a Trivy filesystem/secret scan, a Docker build, and an HTTP smoke test

## Architecture

```text
Browser / curl
      |
      v
Docker port mapping :8080
      |
      v
Python ThreadingHTTPServer
      |
      +--> /            Static landing page (HTML/CSS)
      +--> /health      JSON status for health checks
```

## Repository layout

| Path | Purpose |
|---|---|
| `app/server.py` | HTTP server, static-file handler, and health endpoint |
| `app/static/index.html` | Landing page |
| `app/static/styles.css` | Responsive dark theme |
| `tests/test_server.py` | HTTP and response-header tests |
| `Dockerfile` | Non-root Docker image and health check |
| `.dockerignore` | Keeps local files out of the Docker build context |
| `.github/workflows/ci.yml` | Test, security scan, image build, and container smoke test |

## Prerequisites

- Python 3.13+ for local tests
- Docker Desktop or Docker Engine for the container workflow
- Git and a shell

## Run locally

From the repository root:

```bash
python app/server.py
```

Open http://localhost:8080. The health endpoint is at http://localhost:8080/health.

To use a different local port, set the `PORT` environment variable:

**PowerShell**
```powershell
$env:PORT = "8090"
python app/server.py
```

**macOS/Linux**
```bash
PORT=8090 python app/server.py
```

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -v
python -m compileall -q app tests
```

The tests start a temporary local HTTP server and verify the landing page, health JSON, security headers, and a 404 for an unknown route.

## Build and run with Docker

Build the image:

```bash
docker build -t dockerwebapp:local .
```

Run it with a host-local port mapping:

```bash
docker run --detach --name dockerwebapp \
  --publish 127.0.0.1:8080:8080 \
  dockerwebapp:local
```

Verify health and the landing page:

```bash
curl --fail http://127.0.0.1:8080/health
curl --fail http://127.0.0.1:8080/
docker inspect --format '{{.State.Health.Status}}' dockerwebapp
docker inspect --format '{{.Config.User}}' dockerwebapp
```

The expected health JSON is:

```json
{"status":"UP","service":"dockerwebapp"}
```

Expected container user: `10001:10001`. The sample binds to loopback for local development; change the host binding only when you deliberately intend to make the service reachable from other machines and have appropriate network controls.

Stop and remove the container:

```bash
docker rm --force dockerwebapp
```

## CI validation

The GitHub Actions workflow runs on pushes and pull requests targeting `main`, plus manual dispatch. It:

1. Runs the standard-library unit tests and byte-compilation checks.
2. Scans the repository for known HIGH/CRITICAL vulnerabilities and secrets with Trivy (configured to fail on findings with available fixes).
3. Builds the Docker image.
4. Starts the container on a loopback-bound port and verifies the health JSON and landing page.
5. Checks that the container is configured to run as the non-root user.

See the [latest workflow runs](https://github.com/nagateja-2002/dockerwebapp/actions).

## Security and scope

- This is a portfolio learning project, not a hardened production web server.
- The app uses Python's simple HTTP server; it does not implement authentication, sessions, or application APIs beyond the health route.
- The container is configured to run as a non-root user and the local Docker example binds only to host loopback.
- Do not deploy publicly without reviewing the server's operational limits, TLS/reverse proxy, access controls, logging, rate limiting, resource limits, and security update strategy.
- CI builds and smoke-tests the image but does not publish it to a registry or deploy to a cloud environment.

## License

No license is currently declared. Add a license before accepting external contributions or redistributing this project.
