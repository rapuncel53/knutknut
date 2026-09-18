# Knut Knut Transport AS - Route Optimization & AI Architecture

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Hosting](https://img.shields.io/badge/Demo-GitHub%20Pages-brightgreen.svg)](https://rapuncel53.github.io/knutknut/)

An intelligent transport route optimization system developed for **Knut Knut Transport AS** as part of the *Artificial Architecture* course. The system combines non-linear regression, piecewise linear models, stochastic search (Fortuna algorithm), and a responsive web application to eliminate random route selection and maximize fleet efficiency.

---

## 🚀 Live Demo

Experience the interactive web app directly on **GitHub Pages**:
🔗 **[https://rapuncel53.github.io/knutknut/](https://rapuncel53.github.io/knutknut/)**

---

## 📌 Executive Summary & Business Impact

Knut Knut Transport AS delivers cargo from **Source** to **Destination** across a 5-node highway network offering 4 possible routes:
1. `A -> C -> D`
2. `A -> C -> E`
3. `B -> C -> D`
4. `B -> C -> E`

### The Problem
Previously, drivers chose routes purely at random, resulting in:
- **Baseline Average Travel Time**: **99.6 minutes** per trip.
- Travel time variability between **50.0** and **163.0 minutes** depending on the time of day and congestion patterns.

### The AI Solution
By selecting the mathematically optimal route for the driver's exact departure time (07:00 to 17:00):
- **Optimized Average Travel Time**: **67.8 minutes** per trip.
- **Average Time Saved**: **31.8 minutes saved per delivery** (~**31.9% reduction** in travel duration).
- **Peak Time Savings**: Up to **80+ minutes saved** during severe morning and afternoon traffic spikes on suboptimal roads.

---

## 📐 Mathematical Models for Route Durations

Given departure time $t = \text{hour} + \frac{\text{minute}}{60.0}$ ($7.0 \le t \le 17.0$):

### 1. Route A &rarr; C &rarr; D (2-Sigmoid Non-Linear Model)
Captures complex morning and afternoon traffic waves:
$$f(t) = 141.21 - 1.86 \cdot t - \frac{44.15}{1 + e^{-2.04(t - 8.86)}} + \frac{63.05}{1 + e^{-1.67(t - 14.98)}}$$

### 2. Route A &rarr; C &rarr; E (Constant Model)
Traffic flow remains unaffected by peak hours:
$$f(t) = 98.00\text{ minutes}$$

### 3. Route B &rarr; C &rarr; D (Piecewise Linear Model)
Split into 1-hour hourly intervals from 07:00 to 17:00:
- **07:00 - 07:15**: $\text{duration} = -36.30 \cdot t + 367.10$
- **07:16 - 08:15**: $\text{duration} = -67.64 \cdot t + 651.50$
- **08:16 - 09:15**: $\text{duration} = -80.06 \cdot t + 811.65$
- **09:16 - 10:15**: $\text{duration} = -79.88 \cdot t + 872.11$
- **10:16 - 11:15**: $\text{duration} = -60.12 \cdot t + 728.30$
- **11:16 - 12:15**: $\text{duration} = -59.07 \cdot t + 776.71$
- **12:16 - 13:15**: $\text{duration} = -63.92 \cdot t + 897.85$
- **13:16 - 14:15**: $\text{duration} = -47.59 \cdot t + 738.65$
- **14:16 - 15:15**: $\text{duration} = -34.79 \cdot t + 614.78$
- **15:16 - 16:15**: $\text{duration} = -43.84 \cdot t + 812.27$
- **16:16 - 17:15**: $\text{duration} = -63.60 \cdot t + 1194.87$

### 4. Route B &rarr; C &rarr; E (Piecewise Linear Model)
- **07:00 - 07:15**: $\text{duration} = -64.84 \cdot t + 543.20$
- **07:16 - 08:15**: $\text{duration} = -57.99 \cdot t + 552.48$
- **08:16 - 09:15**: $\text{duration} = -60.24 \cdot t + 630.26$
- **09:16 - 10:15**: $\text{duration} = -59.41 \cdot t + 682.54$
- **10:16 - 11:15**: $\text{duration} = -58.36 \cdot t + 731.04$
- **11:16 - 12:15**: $\text{duration} = -63.81 \cdot t + 852.59$
- **12:16 - 13:15**: $\text{duration} = -60.75 \cdot t + 876.87$
- **13:16 - 14:15**: $\text{duration} = -59.25 \cdot t + 916.35$
- **14:16 - 15:15**: $\text{duration} = -57.37 \cdot t + 949.71$
- **15:16 - 16:15**: $\text{duration} = -58.66 \cdot t + 1027.28$
- **16:16 - 17:15**: $\text{duration} = -58.89 \cdot t + 1090.40$

---

## 📂 Repository Structure

```text
├── docs/                               # GitHub Pages static interactive web preview
│   └── index.html                      # Standalone client-side application with Chart.js
├── handin1/
│   └── handin1_export/
│       ├── Pitch_knutknut_transport.pdf # Executive slide deck for CEO Knut
│       ├── best_route_model.pkl        # Serialized trained model
│       ├── fortuna_multiprocessing.py  # Parallel implementation of Fortuna stochastic search
│       ├── handin1.ipynb               # Original handin template
│       ├── handin1_final.ipynb         # Fully solved & verified notebook
│       ├── handin1_task completed.ipynb# Task-completed checkpoint
│       ├── knut_knut_app.py            # Assignment-spec Flask server
│       ├── route_duration_trends.png   # Visualization of traffic trends
│       └── traffic.jsonl               # 1,031 historical transport data records
├── route_optimizer_app/                # Production-grade Flask web application
│   ├── app.py                          # Flask backend with HTML UI and REST APIs
│   ├── route_models.py                 # Mathematical model definitions and evaluation logic
│   ├── requirements.txt                # Python dependencies
│   ├── run.bat                         # One-click Windows launch script
│   ├── test_app.py                     # Integration & endpoint unit tests
│   ├── test_models.py                  # Mathematical accuracy unit tests
│   ├── static/                         # CSS styling and JavaScript frontend
│   └── templates/                      # Jinja2 HTML templates
├── How we created the knut knut model.docx # Comprehensive written academic/technical report
├── traffic.jsonl                       # Root copy of the historical dataset
├── .gitignore                          # Clean repository filtering (excludes virtual environments)
└── README.md                           # Master repository documentation
```

---

## 💻 Running the Application Locally

### Method 1: Flask Web App (Recommended)

1. Navigate to the web application directory:
   ```bash
   cd route_optimizer_app
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python app.py
   ```
   *(Or double-click `run.bat` on Windows)*.
5. Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Method 2: Jupyter Notebooks

Open and run the notebooks in VS Code or JupyterLab:
```bash
jupyter lab handin1/handin1_export/handin1_final.ipynb
```

### Method 3: Running Unit Tests

To verify mathematical predictions and web endpoints:
```bash
cd route_optimizer_app
python -m unittest discover
```

---

## 🌐 Application API Endpoints

- **`GET /`**: Full interactive dashboard with time selector, best route badge, savings breakdown, and comparison table.
- **`GET /get_best_route?hour=09&mins=30`**: Assignment-compatible text endpoint returning estimated travel time and time saved.
- **`GET /api/predict?hour=09&minute=30`**: JSON endpoint returning detailed predictions for all 4 routes, best route, and savings.
- **`GET /api/profile?step=15`**: Operating day profile from 07:00 to 17:00 for graphing.

---

## 👥 Authors & Academic Context

Developed for the **Artificial Architecture** coursework (Erasmus program) by **Julia**.
