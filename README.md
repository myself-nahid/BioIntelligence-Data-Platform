# ChalkBio Data Intelligence Platform — Backend

This repository contains the backend services for the **ChalkBio** platform. It is a full-stack data intelligence application designed to capture user behavior, ingest external biomedical data, and serve AI-powered predictions for clinical trial success.

The entire system is containerized with **Docker** and orchestrated via **Docker Compose**.

---

## Core Features

The backend supports six core data intelligence capabilities:

1. **User Event Tracking**
   Captures user interactions via an API endpoint and runs a daily data quality validation job.

2. **Watchlists & "Most Watched"**
   Enables users to follow entities, manage watchlists via APIs, and compute trending entities through scheduled background jobs.

3. **Mechanism Crowding Index**
   Periodic background job calculates competitive density for drug mechanisms and exposes results through an API.

4. **Smart Alerts**
   Background jobs generate user alerts based on watchlist activity and predefined triggers.

5. **Investigator Database**
   Scraper stubs and APIs to build and serve a proprietary database of clinical investigators.

6. **Trial Success Prediction**
   End-to-end machine learning pipeline using **PubMedBERT** and internal data to predict clinical trial outcomes. Models are retrained automatically on a weekly schedule.

---

## Tech Stack

* **Backend Framework:** FastAPI
* **Database:** PostgreSQL
* **Background Jobs:** Celery
* **Message Broker / Cache:** Redis
* **Machine Learning:** Scikit-learn, PyTorch, Hugging Face Transformers
* **Containerization:** Docker & Docker Compose

---

## Getting Started: Local Development Setup

Follow this guide to run a complete instance of the backend locally.

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* A terminal or command line (PowerShell, WSL, or macOS/Linux Terminal)
* A database GUI tool such as [DBeaver](https://dbeaver.io/download/) (recommended)

---

## 1. Configure Your Environment

The project uses `.env` files for configuration.

### 1.1 Database Configuration

Create a file named `.env` in the project root:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=chalkbio
```

This file is consumed by Docker Compose and the PostgreSQL container.

---

### 1.2 Application Configuration

Create a file named `.env.app` in the project root:

```env
# Application Settings
DATABASE_URL=postgresql://user:pass@db:5432/chalkbio
REDIS_URL=redis://redis:6379

# API Settings & Keys
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/URL"
PUBMED_API_KEY="your_optional_pubmed_api_key_here"
```

This file is used by the Python application containers (`api`, `worker`, `scheduler`).

---

## 2. Build and Run the Application

Build the Docker images and start all services:

```bash
docker-compose up --build
```

**First run notice:**
The initial startup may take several minutes as Docker downloads base images and Python dependencies, including the ~500MB PubMedBERT model. Subsequent startups will be much faster.

Wait until you see a log entry similar to:

```
INFO: Application startup complete.
```

---

## 3. Set Up the Database

The containers are running, but the database schema must be initialized manually.

1. **Connect to the Database**
   Use DBeaver or another SQL client with:

   * Host: `localhost`
   * Port: `5432`
   * Database: `chalkbio`
   * User / Password: from `.env`

2. **Run the Schema Script**
   Open the `reset_db.sql` file in the repository. Copy its entire contents, paste it into a SQL editor in DBeaver, and execute it as a script.

3. **Verify**
   Refresh the database schema. You should see all application tables and the `mechanism_crowding` materialized view.

---

## 4. Train the AI Model

Run the initial model training step.

1. Open a **new terminal window** (leave Docker running).
2. Navigate to the project root.
3. Execute the training script inside the API container:

```bash
docker-compose exec api python -m chalkbio.models.train
```

This process saves trained model artifacts into the `models_volume` directory.

---

## 5. Restart and Final Verification

1. Stop the application:

   ```bash
   Ctrl + C
   ```

2. Start it again:

   ```bash
   ```

docker-compose up

```

3. Open your browser and visit:
```

[http://localhost:8000/docs](http://localhost:8000/docs)

```

If the Swagger UI loads correctly, your local environment is fully configured.

---

## How to Work with the System

### API Documentation

The interactive Swagger UI at:

```

[http://localhost:8000/docs](http://localhost:8000/docs)

````

is the single source of truth for all API endpoints. Use it to explore request/response schemas and test endpoints directly.

---

### Running Background Jobs Manually

You can trigger Celery tasks manually for testing:

```bash
# Format:
# docker-compose exec <service> celery -A <celery_app_path> call <task_path> --args "[<args>]"

# Example:
docker-compose exec worker celery \
  -A chalkbio.core.celery_app.celery_app call \
  chalkbio.jobs.triggers.fda_alerts.trigger_fda_alert \
  --args "['DRUG-ABC', 'This is a test message.']"
````

---

### Running Tests

Run the full Pytest suite with:

```bash
docker-compose exec api pytest
```

---

### Stopping the Application

To stop all services:

```bash
Ctrl + C
```

To remove all containers:

```bash
docker-compose down
```

To remove containers **and** delete database volumes:

```bash
docker-compose down -v
```

---