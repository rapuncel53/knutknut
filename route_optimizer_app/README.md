# Knut Knut Transport AS - Best Route Optimizer Web App

An intelligent route optimization Flask web application developed for **Knut Knut Transport AS**. The application predicts trip durations across all 4 delivery routes, selects the fastest route for any departure time between **07:00 and 17:00**, and calculates the exact travel time saved compared to other routes.

---

## The 4 Routes & Exact Mathematical Equations

Operational window: **07:00 to 17:00** ($7.0 \le \text{time} \le 17.0$). Time is expressed in decimal hours:
$$\text{time} = \text{hour} + \frac{\text{minute}}{60.0}$$

### 1. Route B &rarr; C &rarr; D (Piecewise Linear Model)
| Departure Interval | Mathematical Formula |
| :--- | :--- |
| **07:00 - 07:15** | $\text{duration} = -36.30 \cdot \text{time} + 367.10$ |
| **07:16 - 08:15** | $\text{duration} = -67.64 \cdot \text{time} + 651.50$ |
| **08:16 - 09:15** | $\text{duration} = -80.06 \cdot \text{time} + 811.65$ |
| **09:16 - 10:15** | $\text{duration} = -79.88 \cdot \text{time} + 872.11$ |
| **10:16 - 11:15** | $\text{duration} = -60.12 \cdot \text{time} + 728.30$ |
| **11:16 - 12:15** | $\text{duration} = -59.07 \cdot \text{time} + 776.71$ |
| **12:16 - 13:15** | $\text{duration} = -63.92 \cdot \text{time} + 897.85$ |
| **13:16 - 14:15** | $\text{duration} = -47.59 \cdot \text{time} + 738.65$ |
| **14:16 - 15:15** | $\text{duration} = -34.79 \cdot \text{time} + 614.78$ |
| **15:16 - 16:15** | $\text{duration} = -43.84 \cdot \text{time} + 812.27$ |
| **16:16 - 17:15** | $\text{duration} = -63.60 \cdot \text{time} + 1194.87$ |

### 2. Route B &rarr; C &rarr; E (Piecewise Linear Model)
| Departure Interval | Mathematical Formula |
| :--- | :--- |
| **07:00 - 07:15** | $\text{duration} = -64.84 \cdot \text{time} + 543.20$ |
| **07:16 - 08:15** | $\text{duration} = -57.99 \cdot \text{time} + 552.48$ |
| **08:16 - 09:15** | $\text{duration} = -60.24 \cdot \text{time} + 630.26$ |
| **09:16 - 10:15** | $\text{duration} = -59.41 \cdot \text{time} + 682.54$ |
| **10:16 - 11:15** | $\text{duration} = -58.36 \cdot \text{time} + 731.04$ |
| **11:16 - 12:15** | $\text{duration} = -63.81 \cdot \text{time} + 852.59$ |
| **12:16 - 13:15** | $\text{duration} = -60.75 \cdot \text{time} + 876.87$ |
| **13:16 - 14:15** | $\text{duration} = -59.25 \cdot \text{time} + 916.35$ |
| **14:16 - 15:15** | $\text{duration} = -57.37 \cdot \text{time} + 949.71$ |
| **15:16 - 16:15** | $\text{duration} = -58.66 \cdot \text{time} + 1027.28$ |
| **16:16 - 17:15** | $\text{duration} = -58.89 \cdot \text{time} + 1090.40$ |

### 3. Route A &rarr; C &rarr; D (2-Sigmoid Non-Linear Model)
$$f(x) = 141.208171028210 - 1.857763594676 \cdot x - \frac{44.149088388722}{1 + e^{-2.038913183625(x - 8.861364625860)}} + \frac{63.050602349853}{1 + e^{-1.672620676169(x - 14.980186722198)}}$$

### 4. Route A &rarr; C &rarr; E (Constant Travel Time Model)
$$f(x) = 98.00\text{ min}$$

---

## How Time Saved is Calculated

For any given departure time:
1. **Best Route**: $T_{\text{best}} = \min(T_{\text{A}\to\text{C}\to\text{D}}, T_{\text{A}\to\text{C}\to\text{E}}, T_{\text{B}\to\text{C}\to\text{D}}, T_{\text{B}\to\text{C}\to\text{E}})$
2. **Time Saved vs Route $i$**:
   $$\Delta T_i = T_i - T_{\text{best}} \quad (\text{minutes saved by choosing best instead of } i)$$
   $$\%\text{ Saved} = \frac{\Delta T_i}{T_i} \times 100\%$$
3. **Time Saved vs Worst Route**:
   $$\Delta T_{\text{max}} = \max(T) - T_{\text{best}}$$
4. **Time Saved vs Random Selection Baseline**:
   Knut Knut Transport drivers historically picked a route at random. The expected gain from using the app is:
   $$\text{Gain}_{\text{random}} = \frac{1}{4}\sum_{i=1}^4 T_i - T_{\text{best}}$$

---

## How to Run

### Option 1: Using the created virtual environment (Recommended)

1. Open PowerShell or Command Prompt in the `route_optimizer_app` directory:
   ```powershell
   cd "route_optimizer_app"
   ```
2. Activate the virtual environment:
   - **In PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **In Command Prompt (cmd)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   *(Or simply double-click `run.bat`)*

3. Run the app:
   ```powershell
   python app.py
   ```
4. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

### Option 2: Run directly using the virtual environment's Python executable
```powershell
.\venv\Scripts\python.exe app.py
```

---

## Application Endpoints

- **`GET /`**: Main interactive dashboard (time picker, best route recommendation, savings cards, side-by-side comparison table, interactive charts).
- **`GET /get_best_route?hour=09&mins=15`**: Backward-compatible endpoint matching the original Knut Knut assignment specification, returning the informative response and time saved.
- **`GET /api/predict?hour=09&minute=15`**: JSON REST API returning full evaluation, duration for all 4 routes, best route, and savings breakdown.
- **`GET /api/profile?step=15`**: JSON REST API returning operating day trend data (07:00 to 17:00) for charts.
