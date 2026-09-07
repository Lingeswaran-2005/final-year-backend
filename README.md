# FastAPI Docker Project

A Python FastAPI application running inside Docker using Docker Compose.

## Prerequisites

Make sure you have the following installed:

* Docker
* Docker Compose

## Running the Project

To build the Docker image and start the containers:

```bash
docker compose up -d --build
```

This will:

* Build the Docker image.
* Start the FastAPI application.
* Run the container in detached mode (`-d`).

### Check Running Containers

```bash
docker compose ps
```

### View Logs

```bash
docker compose logs -f
```

To stop the containers:

```bash
docker compose down
```

## Making Changes

If you make changes to the Python dependencies, update `requirements.txt`:

```bash
pip freeze > requirements.txt
```

Then rebuild and restart the containers:

```bash
docker compose up -d --build
```

This ensures the updated dependencies are installed into the Docker image.

## Development Workflow

A typical workflow after making changes is:

```bash
# Make changes to the project

# Update dependencies if required
pip freeze > requirements.txt

# Rebuild and restart
docker compose up -d --build
```

> **Note:** If you only modify application source code and your Docker Compose setup uses a volume mount for the source code, rebuilding may not be necessary. Otherwise, use `docker compose up -d --build` to ensure the changes are included in the image.

## Stopping the Project

To stop and remove the running containers:

```bash
docker compose down
```

To rebuild the project from scratch:

```bash
docker compose down
docker compose up -d --build
```

## Project Structure

```text
project/
├── src/
│   └── ...
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
