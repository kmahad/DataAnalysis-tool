# DataPurify — Intelligent Data Analysis & Purification Platform

DataPurify is a modern, full-stack, deployment-ready web application designed for data analysts. It automates data quality scanning, profiles data structures, suggests fixes, applies comprehensive data purification operations with a full undo/redo stack, builds interactive charts, and exports clean datasets and audit reports.

---

## ✨ Features

- **🌐 Browser-Based Data Ingestion**:
  - Drag-and-drop file upload for **CSV** and **Excel (.xlsx, .xls)**.
  - Connect to **PostgreSQL**, **MySQL**, and **SQLite** databases using connection strings (e.g., Supabase, PlanetScale, AWS RDS).
- **📊 Automated Health Profiling & Data Quality Score**:
  - Calculates a **0–100 quality score** based on completeness (40%), uniqueness (20%), consistency (20%), and validity (20%).
  - Profiles each column automatically (data types, missing percentages, outliers, stats).
  - Offers a **Missing Values Heatmap** and instant **purification recommendations**.
- **🧼 6 Powerful Purification Tools**:
  - **Missing Values**: Fill with mean/median/mode, forward fill, backward fill, linear interpolation, custom value, or drop rows/columns.
  - **Deduplication**: Remove exact or column-subset duplicate rows.
  - **Outlier Filtering**: Detect outliers using IQR or Z-score methods and remove, cap/winsorize, or set them to NaN.
  - **String Sanitation**: Trim whitespace, convert casing (lower/upper/title), and remove special characters.
  - **Column Operations**: Rename, drop, or reorder columns.
- **↩️ Full Undo/Redo & History Audit Stack**:
  - Keeps track of all performed operations.
  - Undo/redo steps or jump to any previous clean state with a single click.
- **📈 Interactive Plotly Chart Builder**:
  - Custom visualization wizard for Bar Charts, Line Charts, Scatter Plots, Pie Charts, Histograms, Box Plots, and Correlation Heatmaps.
- **📥 Export Options**:
  - Download cleaned datasets in CSV or Excel format.
  - Generate an interactive standalone **HTML Audit Report** detailing all operations performed.

---

## 🛠️ Architecture

```
DataPurify (Monorepo)
├── backend/          # FastAPI (Python) backend API service
│   ├── app/
│   │   ├── main.py        # App entry point & middleware
│   │   ├── routers/       # API endpoints (auth, upload, scan, clean, visualize, export)
│   │   ├── services/      # Analytical engines (scanner, purifier, visualizer, db_connector)
│   │   └── models/        # Schemas & session managers
│   └── run.py             # Backend local server startup script
└── frontend/         # Vite + React (TypeScript) frontend application
    ├── src/
    │   ├── api/           # API fetch client wrapper
    │   ├── context/       # Auth and Data global state managers
    │   ├── components/    # Reusable modular UI components
    │   └── index.css      # Custom premium dark theme design system
    └── vite.config.ts     # Dev server configuration and api proxies
```

---

## 🚀 Running the App Locally

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & **npm**

### Step 1: Start the Backend API

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python run.py
   ```
   *The backend starts at `http://localhost:8000`. You can inspect the interactive Swagger API documentation at `http://localhost:8000/docs`.*

### Step 2: Start the Frontend Application

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser to access the app.*

---

## 🔐 Credentials & Authentication

Since the application includes JWT-based login, you can register a new account on the login page or sign in using the default user credentials:

- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Testing with Sample Data

We have included a mock dataset containing common data quality issues (whitespace, missing values, duplicates, and outliers) for testing:
📄 **`sample_data.csv`**

1. Upload **`sample_data.csv`** to the dashboard.
2. Note the initial **Data Quality Score** and missing value counts.
3. Apply string sanitation to the `name` column to trim whitespace.
4. Fill missing values in `salary` using the `fill_mean` strategy.
5. Remove duplicate rows.
6. Cap outliers in the `age` column.
7. Verify all steps in the **Audit History** log, build a bar chart in the **Visualizer**, and export your clean file!
