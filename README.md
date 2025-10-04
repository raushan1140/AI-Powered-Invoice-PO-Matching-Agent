# Invoice-PO Matching Agent

A professional hackathon-ready application that automates invoice validation against purchase orders using AI-powered document processing and natural language query capabilities.

## 🚀 Features

### Core Functionality
- **Invoice Processing**: Upload PDF or image invoices for automatic data extraction
- **OCR & Text Extraction**: Uses pdfplumber for PDFs and Tesseract OCR for images
- **PO Validation**: Intelligent matching against purchase orders with mismatch detection
- **Natural Language Queries**: Ask business questions in plain English, powered by GPT-4
- **Real-time Leaderboard**: Track team performance and hackathon scoring

### AI-Powered Capabilities
- **Document Intelligence**: Extract invoice numbers, vendors, dates, line items, and totals
- **Fuzzy Matching**: Smart vendor and item matching using rapidfuzz
- **SQL Translation**: Convert natural language to SQL queries
- **Validation Engine**: Detect price, quantity, vendor, and item mismatches

### Professional UI
- **Modern React Interface**: Built with Vite + React + Tailwind CSS
- **Interactive Charts**: Plotly.js visualizations for data analysis
- **File Upload**: Drag-and-drop invoice upload with progress tracking
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
invoice-po-matching-agent/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── routes/             # API route handlers
│   │   ├── invoice_routes.py    # Invoice upload & validation
│   │   ├── query_routes.py      # Natural language queries
│   │   └── leaderboard_routes.py # Team scoring
│   ├── services/           # Core business logic
│   │   ├── invoice_parser.py    # PDF/OCR processing
│   │   ├── po_validator.py      # Validation engine
│   │   └── query_engine.py      # NL to SQL translation
│   ├── models/             # Database layer
│   │   └── db_setup.py         # SQLite schema & operations
│   └── requirements.txt    # Python dependencies
├── frontend/               # React web application
│   ├── src/
│   │   ├── pages/          # Main application pages
│   │   │   ├── InvoiceUpload.jsx   # Upload & validation UI
│   │   │   ├── QueryAssistant.jsx  # Natural language interface
│   │   │   └── Leaderboard.jsx     # Team rankings
│   │   ├── components/     # Reusable UI components
│   │   │   ├── FileUploader.jsx    # Drag-drop file upload
│   │   │   ├── ResultsTable.jsx    # Data tables with export
│   │   │   └── ChartDisplay.jsx    # Interactive charts
│   │   └── App.jsx         # Main app with routing
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js     # Vite configuration
└── README.md              # This file
```

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework for REST API
- **SQLite**: Lightweight database for hackathon deployment
- **pdfplumber**: PDF text extraction
- **pytesseract**: OCR for image processing
- **OpenCV**: Image preprocessing
- **rapidfuzz**: Fuzzy string matching
- **OpenAI GPT-4**: Natural language to SQL translation

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Plotly.js**: Interactive data visualizations
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

### Database Schema
```sql
-- Purchase Orders
purchase_orders (po_id, vendor, item, qty, unit_price, total, date)

-- Processed Invoices
invoices (invoice_id, vendor, item, qty, unit_price, total, date, po_id, status, validation_result)

-- Team Leaderboard
leaderboard (team_id, team_name, score, validations_completed, queries_executed)

-- Query History
query_history (natural_language_query, sql_query, execution_time, result_count, team_id)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Tesseract OCR (for image processing)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd invoice-po-matching-agent/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   
   **Windows:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or set TESSDATA_PREFIX environment variable
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```

5. **Set up environment variables (optional)**
   
   **Option 1: Create .env file (Recommended)**
   ```bash
   # Create .env file in backend directory
   echo OPENAI_API_KEY=your_openai_api_key_here > .env
   ```
   
   **Option 2: Set environment variable**
   
   **Windows (PowerShell):**
   ```powershell
   $env:OPENAI_API_KEY="your_openai_api_key_here"
   ```
   
   **macOS/Linux:**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

6. **Initialize database and start server**
   ```bash
   python app.py
   ```
   
   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd invoice-po-matching-agent/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## 🎯 Usage Guide

### 1. Invoice Upload & Validation

1. **Access the Invoice Upload page** (default homepage)
2. **Enter your team ID** (optional, for leaderboard tracking)
3. **Upload an invoice**:
   - Drag and drop a PDF or image file
   - Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP
   - Maximum file size: 16MB
4. **View results**:
   - Extracted invoice data (vendor, amounts, line items)
   - Validation status against purchase orders
   - Detailed mismatch analysis

### 2. Natural Language Queries

1. **Go to Query Assistant page**
2. **Enter your team ID** (optional, for scoring)
3. **Ask questions in plain English**:
   - "Show me total spend per vendor this quarter"
   - "What are the recent invoices?"
   - "Which team has completed the most validations?"
4. **View results**:
   - Automatically generated SQL query
   - Interactive data tables
   - Charts and visualizations

### 3. Leaderboard & Competition

1. **Visit the Leaderboard page**
2. **View rankings by**:
   - Overall score
   - Number of validations completed
   - Number of queries executed
   - Recent activity
3. **Track team performance** with real-time updates

## 🏆 Scoring System

- **Invoice Validation**: 20 points (approved), 10 points (processed)
- **Natural Language Query**: 10 points per successful query
- **SQL Query Execution**: 5 points per direct SQL query

## 🔧 API Endpoints

### Invoice Processing
- `POST /api/invoices/upload` - Upload and process invoice
- `GET /api/invoices/list` - List processed invoices
- `GET /api/invoices/{id}` - Get invoice details
- `POST /api/invoices/validate` - Validate invoice data

### Query Engine
- `POST /api/queries/execute` - Execute natural language query
- `GET /api/queries/suggestions` - Get suggested queries
- `GET /api/queries/history` - Query execution history
- `POST /api/queries/translate` - Translate NL to SQL

### Leaderboard
- `GET /api/leaderboard/` - Get current rankings
- `GET /api/leaderboard/team/{id}` - Get team statistics
- `POST /api/leaderboard/update` - Update team scores
- `POST /api/leaderboard/create-team` - Create new team

## 🤖 AI Integration

### GPT-4 Setup (Optional)
For enhanced natural language processing:

1. **Get OpenAI API key** from https://platform.openai.com/
2. **Set environment variable**:

   **Windows (PowerShell):**
   ```powershell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set OPENAI_API_KEY=your-api-key-here
   ```
   
   **macOS/Linux (Bash/Zsh):**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   **Alternative: Create .env file** (Recommended for development):
   ```bash
   # In the backend directory, create a .env file
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Fallback system**: If no API key, uses pattern matching for common queries

### OCR Configuration
Tesseract OCR is used for image processing:
- **Preprocessing**: Noise reduction, thresholding
- **Text extraction**: Multi-language support
- **Field extraction**: Regex patterns for invoice fields

## 🛡️ Security Features

- **File validation**: Type checking and size limits
- **SQL injection protection**: Parameterized queries only
- **Input sanitization**: XSS prevention
- **CORS configuration**: Restricted to frontend domain

## 🚀 Deployment

### Production Deployment

1. **Backend**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Frontend**:
   ```bash
   npm run build
   # Serve dist/ folder with nginx or similar
   ```

3. **Environment**:
   - Set `FLASK_ENV=production`
   - Configure proper CORS origins
   - Use PostgreSQL for production database

### Docker Deployment (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

## 📊 Sample Data

The application comes with pre-loaded sample data:
- **10 Purchase Orders** from various vendors
- **5 Sample Teams** on the leaderboard
- **Common query patterns** for testing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Hackathon Demo Script

### 5-Minute Demo Flow

1. **Introduction** (30s)
   - "AI-powered invoice validation system"
   - "Natural language business intelligence"

2. **Invoice Upload Demo** (2 min)
   - Upload sample invoice
   - Show extracted data
   - Highlight validation results
   - Explain mismatch detection

3. **Query Assistant Demo** (2 min)
   - Ask "Show me total spend per vendor"
   - Demonstrate SQL generation
   - Show interactive charts
   - Try another query live

4. **Leaderboard & Scoring** (30s)
   - Show real-time rankings
   - Explain scoring system
   - Highlight team competition aspect

### Key Talking Points
- **AI Integration**: OCR, fuzzy matching, GPT-4
- **Business Value**: Automated AP process, data insights
- **Technical Excellence**: Modern stack, scalable architecture
- **User Experience**: Intuitive interface, real-time feedback

## 🔗 Links

- **Live Demo**: [Your deployment URL]
- **GitHub Repository**: [Your GitHub URL]
- **API Documentation**: `http://localhost:5000/api/health`
- **Technical Blog Post**: [Your blog URL]

---

**Built for Hackathon Excellence** 🏆  
*Combining AI, modern web technologies, and intelligent document processing*
