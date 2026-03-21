# Money Tracker

A personal expense and income tracking web application built with Python and FastAPI.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Transaction Management** -- Add, edit, delete, and search income/expense transactions
- **Categories** -- Organize transactions with customizable categories (icons, colors)
- **Budgets** -- Set monthly/yearly budgets per category with progress tracking
- **Recurring Transactions** -- Automate repeating income/expenses (daily, weekly, monthly, yearly)
- **Reports & Charts** -- Interactive charts (pie, bar, line) for spending insights
- **CSV Import/Export** -- Bulk import via drag-and-drop, export to CSV
- **Multi-Currency** -- Per-currency tracking with support for 35+ currencies and live exchange rates
- **AI Financial Assistant** -- Chat with an AI analyst powered by Claude to query your data, analyze spending, and get insights
- **Cutesy Lavender Aesthetic** -- Soft pastel color scheme with rounded cards, Nunito + Patrick Hand fonts, and an animated pixel-art penguin mascot
- **Dark/Light Mode** -- Toggle between themes (lavender palette adapts to both)
- **Responsive** -- Works on desktop, tablet, and mobile

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | SQLite + SQLAlchemy ORM |
| Migrations | Alembic |
| Frontend | Jinja2, Vanilla JS, Chart.js |
| CSS | Pico CSS + custom lavender theme |
| Fonts | Nunito (body), Patrick Hand (headings/nav) |
| AI | Anthropic Claude API (claude-opus-4-6) |
| Currency Rates | frankfurter.app (free, no API key) |

## Quick Start

### Prerequisites

- Python 3.12+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/money-tracker.git
cd money-tracker

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Seed default categories
python seed_data.py

# Run the app
python run.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser, or use `start.bat` for Tailscale access.

### Configuration

Copy `.env.example` to `.env` and customize:

```
DATABASE_URL=sqlite:///./money_tracker.db
BASE_CURRENCY=USD

# AI Chat - Option 1: Standard Anthropic API key
ANTHROPIC_API_KEY=sk-ant-...

# AI Chat - Option 2: Custom proxy (e.g. corporate endpoint)
ANTHROPIC_BASE_URL=https://api.example.com/
ANTHROPIC_AUTH_TOKEN=your-token-here
ANTHROPIC_MODEL=claude-opus-4-6
```

The AI assistant is optional -- the app works fully without it. If no API key is configured, the AI Chat page shows a "Not Configured" status.

## Remote Access (Tailscale)

Access the app securely from your phone or other devices using [Tailscale](https://tailscale.com):

1. Install Tailscale on your PC and mobile devices
2. Sign in on all devices with the same account
3. Run the app using `start.bat` (binds to your Tailscale IP)
4. Access from any device: `http://<your-tailscale-ip>:8000`

All traffic is end-to-end encrypted via WireGuard — no ports to open, no public exposure.

To run on localhost only (default):

```bash
python run.py
```

To specify a custom host:

```bash
set HOST=0.0.0.0
python run.py
```

## AI Financial Assistant

The built-in AI assistant lets you chat with your financial data using natural language. Powered by Claude, it can:

- Summarize monthly spending and income
- Identify top expense categories
- Check budget status and alerts
- Analyze trends across months
- Search for specific transactions
- Track category spending over time

Ask questions like:
- *"How much did I spend this month?"*
- *"Am I over budget on anything?"*
- *"Compare my spending this month vs last month"*
- *"What's my average monthly spending on food?"*

The assistant uses tool-based data retrieval to query your actual database -- no data leaves your machine except the chat messages sent to the Claude API.

## Security

- Security headers (X-Frame-Options, X-Content-Type-Options, XSS-Protection, Referrer-Policy, Permissions-Policy)
- Input validation via Pydantic schemas with regex patterns
- XSS prevention with `escapeHtml()` on all user-rendered content
- CSV injection protection on export
- File size limits on CSV upload (5 MB)
- API docs disabled in production
- Server binds to localhost by default

## Project Structure

```
money-tracker/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # App settings
│   ├── database.py           # Database engine & session
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic validation schemas
│   ├── routers/              # API route handlers
│   ├── services/             # Business logic
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JavaScript & images
│       ├── css/style.css     # Custom lavender theme overrides
│       ├── js/               # app.js, charts.js, utils.js
│       └── img/              # Penguin sprite sheet (SVG)
├── alembic/                  # Database migrations
├── seed_data.py              # Default category seeder
├── run.py                    # Uvicorn launcher
├── start.bat                 # Quick launcher (activates venv + Tailscale IP)
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Dev/test dependencies
```

### API Endpoints

| Resource | Endpoints |
|----------|-----------|
| Transactions | `GET/POST /api/v1/transactions`, `GET/PUT/DELETE /api/v1/transactions/{id}` |
| Categories | `GET/POST /api/v1/categories`, `GET/PUT/DELETE /api/v1/categories/{id}` |
| Budgets | `GET/POST /api/v1/budgets`, `GET/PUT/DELETE /api/v1/budgets/{id}`, `GET /api/v1/budgets/summary` |
| Recurring | `GET/POST /api/v1/recurring`, `GET/PUT/DELETE /api/v1/recurring/{id}`, `POST /api/v1/recurring/generate` |
| Reports | `GET /api/v1/reports/monthly-summary`, `GET /api/v1/reports/yearly-summary`, `GET /api/v1/reports/category-breakdown`, `GET /api/v1/reports/trend` |
| CSV | `POST /api/v1/csv/import`, `GET /api/v1/csv/export`, `GET /api/v1/csv/template` |
| Currency | `GET /api/v1/currencies`, `GET /api/v1/currencies/rates`, `POST /api/v1/currencies/refresh`, `GET /api/v1/currencies/convert` |
| AI Chat | `POST /api/v1/ai/chat`, `GET /api/v1/ai/status` |

## Screenshots

| Dashboard | Transactions | Reports | AI Chat |
|-----------|-------------|---------|---------|
| Summary cards, charts, budget alerts | Filterable table with CRUD modals | Pie, bar, and line charts | Chat-based financial analysis |

## License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.
