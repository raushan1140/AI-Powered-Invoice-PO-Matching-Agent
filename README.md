# 🧾 Invoice-PO Matching Agent

An AI-powered invoice validation system that automates invoice processing and purchase order matching using intelligent document processing, OCR, and natural language query capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

The Invoice-PO Matching Agent is a comprehensive solution for automating accounts payable workflows. It leverages AI and OCR technology to extract data from invoice documents, validate them against purchase orders, and provide intelligent business insights through natural language queries.

### Key Highlights

- **Automated Invoice Processing**: Extract data from PDF and image invoices automatically
- **Intelligent Validation**: Match invoices against purchase orders with mismatch detection
- **Natural Language Queries**: Ask business questions in plain English, get SQL-powered answers
- **Real-time Analytics**: Interactive dashboards and leaderboard tracking
- **Modern Tech Stack**: Built with Flask, React, and OpenAI GPT-4

---

## ✨ Features

### 🔍 Document Intelligence
- **Multi-format Support**: Process PDF, PNG, JPG, JPEG, TIFF, and BMP files
- **OCR Processing**: Tesseract OCR with image preprocessing for optimal text extraction
- **Smart Extraction**: Automatically identify invoice numbers, vendors, dates, line items, and totals
- **Data Validation**: Comprehensive validation against purchase order database

### 🤖 AI-Powered Capabilities
- **Fuzzy Matching**: Intelligent vendor and item matching using advanced algorithms
- **GPT-4 Integration**: Natural language to SQL query translation
- **Mismatch Detection**: Identify discrepancies in prices, quantities, vendors, and items
- **Query Suggestions**: Get intelligent query recommendations based on your data

### 💼 Business Features
- **Invoice Validation**: Approve/reject invoices with detailed mismatch reports
- **Query Assistant**: Ask questions like "Show me total spend per vendor this quarter"
- **Team Leaderboard**: Track performance metrics and competition scoring
- **Export Capabilities**: Download results as CSV or Excel files

### 🎨 User Experience
- **Modern React UI**: Clean, responsive interface built with Tailwind CSS
- **Drag-and-Drop Upload**: Easy file upload with progress tracking
- **Interactive Charts**: Plotly.js visualizations for data analysis
- **Real-time Updates**: Live feedback and validation results

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Invoice    │  │    Query     │  │  Leaderboard │      │
│  │   Upload     │  │  Assistant   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    REST API (HTTP/JSON)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask API)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Invoice    │  │      PO      │  │    Query     │      │
│  │   Parser     │  │  Validator   │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  pdfplumber  │  │  rapidfuzz   │  │  OpenAI GPT  │      │
│  │  pytesseract │  │   matching   │  │  (optional)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  SQLite        │
                    │  Database      │
                    │  - Invoices    │
                    │  - POs         │
                    │  - Teams       │
                    └────────────────┘
```

### Workflow

1. **Invoice Upload** → User uploads invoice (PDF/Image)
2. **Processing** → OCR extraction + data parsing
3. **Validation** → Match against purchase orders
4. **Results** → Display validation results with mismatch details
5. **Query** → Natural language questions converted to SQL
6. **Analytics** → Generate charts and reports

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Flask | REST API framework |
| SQLite | Lightweight database |
| pdfplumber | PDF text extraction |
| pytesseract | OCR for images |
| OpenCV | Image preprocessing |
| rapidfuzz | Fuzzy string matching |
| OpenAI API | Natural language processing (optional) |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool & dev server |
| Tailwind CSS | Styling |
| Plotly.js | Data visualization |
| React Router | Client-side routing |
| Axios | HTTP requests |

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
- **Node.js 16 or higher** ([Download](https://nodejs.org/))
- **npm or yarn** (comes with Node.js)
- **Tesseract OCR** (for image processing)
- **OpenAI API Key** (optional, for enhanced NL queries)

### Installing Tesseract OCR

**Windows:**
1. Download installer from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer and note installation path
3. Add to PATH or set `TESSDATA_PREFIX` environment variable

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Verify installation:**
```bash
tesseract --version
```

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/raushan1140/invoice-po-matching-agent.git
cd invoice-po-matching-agent
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

---

## ⚙️ Configuration

### Backend Configuration

#### Option 1: Environment Variables (Recommended)

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
DATABASE_PATH=./data/invoice_po.db
UPLOAD_FOLDER=./uploads
```

#### Option 2: System Environment Variables

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Frontend Configuration

Update API endpoint in `frontend/src/config.js` if needed:

```javascript
export const API_BASE_URL = 'http://localhost:5000/api';
```

### Getting OpenAI API Key (Optional)

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy and save it securely

**Note:** The application works without OpenAI API key but with limited natural language query capabilities.

---

## 🎮 Usage

### Starting the Application

#### Terminal 1 - Backend Server

```bash
cd backend
# Activate virtual environment first
python app.py
```

Backend will run at: `http://localhost:5000`

#### Terminal 2 - Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will run at: `http://localhost:5173`

### Using the Application

#### 1. Invoice Upload & Validation

1. Open browser and go to `http://localhost:5173`
2. Click on "Invoice Upload" (or use homepage)
3. Enter your Team ID (optional)
4. Drag and drop an invoice file or click to browse
5. Wait for processing (OCR + validation)
6. Review results:
   - Extracted invoice data
   - Validation status
   - Detailed mismatch analysis

#### 2. Natural Language Queries

1. Navigate to "Query Assistant"
2. Enter your Team ID (optional)
3. Type a question in plain English:
   - "Show me total spend per vendor"
   - "List all invoices from last month"
   - "Which items have the highest quantity?"
4. View:
   - Auto-generated SQL query
   - Results table
   - Interactive charts

#### 3. Team Leaderboard

1. Go to "Leaderboard" page
2. View team rankings by:
   - Total score
   - Validations completed
   - Queries executed
3. Track real-time updates

---

## 📡 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Invoice Endpoints

#### Upload Invoice
```http
POST /api/invoices/upload
Content-Type: multipart/form-data

Parameters:
- file: Invoice file (PDF/Image)
- team_id: Team identifier (optional)

Response:
{
  "invoice_id": "INV001",
  "extracted_data": {...},
  "validation_result": {...},
  "status": "approved|rejected|pending"
}
```

#### List Invoices
```http
GET /api/invoices/list?team_id=TEAM001

Response:
{
  "invoices": [
    {
      "invoice_id": "INV001",
      "vendor": "ABC Corp",
      "total": 1500.00,
      "status": "approved"
    }
  ]
}
```

### Query Endpoints

#### Execute Natural Language Query
```http
POST /api/queries/execute
Content-Type: application/json

Body:
{
  "query": "Show me total spend per vendor",
  "team_id": "TEAM001"
}

Response:
{
  "sql_query": "SELECT vendor, SUM(total) FROM invoices GROUP BY vendor",
  "results": [...],
  "chart_data": {...}
}
```

### Leaderboard Endpoints

#### Get Rankings
```http
GET /api/leaderboard/

Response:
{
  "teams": [
    {
      "team_id": "TEAM001",
      "team_name": "Alpha Team",
      "score": 150,
      "validations_completed": 5,
      "queries_executed": 10
    }
  ]
}
```

For complete API documentation, visit `/api/health` when server is running.

---

## 📁 Project Structure

```
invoice-po-matching-agent/
│
├── backend/
│   ├── app.py                    # Flask application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (create this)
│   │
│   ├── routes/
│   │   ├── invoice_routes.py     # Invoice endpoints
│   │   ├── query_routes.py       # Query endpoints
│   │   └── leaderboard_routes.py # Leaderboard endpoints
│   │
│   ├── services/
│   │   ├── invoice_parser.py     # PDF/OCR processing
│   │   ├── po_validator.py       # Validation logic
│   │   └── query_engine.py       # NL to SQL translation
│   │
│   ├── models/
│   │   └── db_setup.py           # Database schema & operations
│   │
│   ├── uploads/                  # Uploaded files (auto-created)
│   └── data/
│       └── invoice_po.db         # SQLite database (auto-created)
│
├── frontend/
│   ├── package.json              # Node.js dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── tailwind.config.js       # Tailwind CSS config
│   │
│   ├── src/
│   │   ├── App.jsx               # Main application component
│   │   ├── main.jsx              # Entry point
│   │   │
│   │   ├── pages/
│   │   │   ├── InvoiceUpload.jsx
│   │   │   ├── QueryAssistant.jsx
│   │   │   └── Leaderboard.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── FileUploader.jsx
│   │   │   ├── ResultsTable.jsx
│   │   │   └── ChartDisplay.jsx
│   │   │
│   │   └── styles/
│   │       └── index.css
│   │
│   └── public/                   # Static assets
│
├── README.md                     # This file
├── LICENSE                       # MIT License
└── .gitignore                   # Git ignore rules
```

---


## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 raushan1140

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 📞 Contact

**Raushan Raj** - raj.raushan9101@gmail.com

**Project Link:** [https://github.com/raushan1140/AI-Powered-Invoice-PO-Matching-Agent](https://github.com/raushan1140/AI-Powered-Invoice-PO-Matching-Agent)

**LinkedIn:** https://www.linkedin.com/in/raushan1140/


### Get in Touch

- 🐛 Found a bug? [Open an issue](https://github.com/raushan1140/AI-Powered-Invoice-PO-Matching-Agent/issues)
- 💡 Have a feature request? [Start a discussion](https://github.com/raushan1140/AI-Powered-Invoice-PO-Matching-Agent/discussions)
- 📧 General inquiries: raj.raushan9101@gmail.com

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4 API
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- [Flask](https://flask.palletsprojects.com/) community
- [React](https://reactjs.org/) team
- All contributors and supporters

---

## 🔮 Future Enhancements

- [ ] Multi-currency support
- [ ] Email notification system
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Docker containerization
- [ ] Cloud deployment guides (AWS, Azure, GCP)
- [ ] Webhook integrations
- [ ] Bulk invoice processing
- [ ] Multi-language OCR support
- [ ] API rate limiting

---

---

<div align="center">

**Built with ❤️ using AI and Modern Web Technologies**

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/raushan1140/invoice-po-matching-agent/issues) · [Request Feature](https://github.com/raushan1140/invoice-po-matching-agent/issues) · [Documentation](https://github.com/raushan1140/invoice-po-matching-agent/wiki)

</div>
