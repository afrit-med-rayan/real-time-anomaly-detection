# Real-Time Anomaly Detection System

A full end-to-end machine learning pipeline that detects anomalies in **streaming financial transaction data** and visualizes them through a live monitoring dashboard.

---

## 🏗️ Architecture

```
Data Generator
      ↓  (JSON events)
Apache Kafka  (topic: transactions)
      ↓
Stream Consumer (Python asyncio)
      ↓
Feature Processing
      ↓
Isolation Forest ML Model
      ↓
FastAPI Backend  (REST + WebSocket)
      ↓
React Dashboard  (Recharts, live updates)
```

---

## 📁 Project Structure

```
real-time-anomaly-detection/
├── backend/
│   ├── api/              # FastAPI server + REST routes
│   ├── model/            # Isolation Forest training & inference
│   ├── services/         # In-memory event & anomaly storage
│   └── streaming/        # Kafka producer & consumer
├── data/
│   └── generator.py      # Synthetic transaction stream generator
├── docker/
│   └── docker-compose.yml
├── frontend/             # React + Vite dashboard
└── notebooks/            # Jupyter model experiments
```

---

## 🚀 Quick Start (Docker)

> **Prerequisite:** Docker Desktop must be installed and running.

```bash
# Clone the repo
git clone https://github.com/afrit-med-rayan/real-time-anomaly-detection.git
cd real-time-anomaly-detection

# Build and start all services
docker compose -f docker/docker-compose.yml up --build -d

# Open the dashboard
Open your browser to: http://localhost:5173
```

---

## 🧩 Components

### 1. Data Generator (`data/generator.py`)

Simulates a continuous stream of financial transactions at ~75 events/min.

- **Normal events**: amount $1–$500, frequency 1–10/hr, account age 30–3650 days
- **Injected anomalies (~5%)** — three types:
  | Type | Signal |
  |------|--------|
  | `high_amount` | $5,000–$50,000 transaction |
  | `high_frequency` | 50–200 transactions/hr burst |
  | `new_account` | Account age < 3 days |
  | `combined` | Multiple signals simultaneously |

### 2. Streaming Layer (Apache Kafka)

- **Topic:** `transactions`
- **Producer:** `backend/streaming/kafka_producer.py`
- **Consumer:** `backend/streaming/kafka_consumer.py`

### 3. ML Model (Isolation Forest)

- Trained on 10,000 synthetic normal samples
- Features: `[amount, transaction_frequency, account_age]`
- Contamination rate: 5%
- Exported as `backend/model/anomaly_model.pkl`

### 4. Backend API (FastAPI)

| Endpoint | Description |
|----------|-------------|
| `GET /events` | Last 100 processed events |
| `GET /anomalies` | All detected anomalies |
| `GET /metrics` | Events/sec, anomaly rate, avg score |
| `WS /ws` | WebSocket — real-time event stream |

### 5. Frontend Dashboard (React + Vite)

- **Live event table** — color-coded normal / anomaly rows
- **Anomaly score chart** — time-series line chart (Recharts)
- **Alert panel** — ⚠ badges for detected anomalies
- **Metrics cards** — events/sec, anomaly rate, avg score

---

## ⚙️ Running Locally (No Docker)

```bash
# 1. Start Kafka (still needs Docker for Kafka itself)
docker compose -f docker/docker-compose.yml up zookeeper kafka -d

# 2. Train the model
cd backend
pip install -r requirements.txt
python model/train_model.py

# 3. Start the backend
uvicorn api.server:app --reload

# 4. Start the generator
cd ../data
python generator.py

# 5. Start the frontend
cd ../frontend
npm install && npm run dev
```

---

## 📊 Sample Output

```
[  normal ] id=10001 amount=$    42.30  freq=  3  age= 365d  loc=Paris
[⚠ ANOMALY] id=10002 amount=$12,450.00  freq= 87  age=   1d  loc=Tokyo
[  normal ] id=10003 amount=$   120.00  freq=  7  age= 900d  loc=Berlin
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Streaming | Apache Kafka |
| ML Model | scikit-learn Isolation Forest |
| Backend | Python, FastAPI, uvicorn |
| Frontend | React, Vite, Recharts |
| Containerisation | Docker, Docker Compose |

---

## 📝 License

MIT
