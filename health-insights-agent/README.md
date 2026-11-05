# 🩺 HealthMate AI

**AI-Powered Health Report Assistant**

HealthMate AI is a Python-based application that helps users understand the information in their medical reports through AI-assisted explanations and conversational question answering.

The project builds on an existing open-source health-report analysis application and is being customized and improved with a new interface, configuration, documentation, and additional development.

> **Important:** HealthMate AI is an informational tool, not a medical diagnostic system. Its responses may be inaccurate or incomplete. Always consult a qualified healthcare professional for medical decisions.

## 🌟 Features

- **AI-powered report analysis:** Generate explanations of information extracted from uploaded reports.
- **Conversational assistance:** Ask follow-up questions about report contents.
- **PDF support:** Upload medical reports for text extraction and analysis.
- **Sample report:** Explore the application using sample data.
- **Multiple AI models:** Use a model fallback mechanism through Groq.
- **Session management:** Organize report analysis and conversations into sessions.
- **User authentication:** Supabase-based authentication.
- **Modern interface:** Built using Streamlit and Python.

_Feature availability and implementation details will be verified and documented as development progresses._

## 🛠️ Technology Stack

| Category                 | Technology            |
| ------------------------ | --------------------- |
| Programming Language     | Python                |
| Frontend                 | Streamlit             |
| AI Models                | Groq API              |
| Language Model Framework | LangChain             |
| Embeddings               | Hugging Face          |
| Vector Database          | FAISS                 |
| Backend Database         | Supabase / PostgreSQL |
| Authentication           | Supabase Auth         |
| PDF Processing           | PDFPlumber            |

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or later
- Git
- Groq API key
- Supabase account and project

### 1. Clone the repository

```bash
git clone https://github.com/rajadityapal05/AI.git
cd AI/health-insights-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment secrets

Create `.streamlit/secrets.toml` and add your own credentials:

```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
GROQ_API_KEY = "your-groq-api-key"
```

Never commit real API keys, passwords, or private credentials to GitHub.

### 5. Configure the database

Review the SQL setup script:

`public/db/script.sql`

Run the appropriate SQL statements in your Supabase project's SQL editor.

### 6. Run the application

```bash
streamlit run src/main.py
```

## 📁 Project Structure

```text
health-insights-agent/
├── requirements.txt
├── README.md
├── src/
│   ├── main.py
│   ├── auth/
│   ├── components/
│   ├── config/
│   ├── services/
│   ├── agents/
│   └── utils/
└── public/
    └── db/
```

## 🔐 Security and Privacy

- Keep API keys and database credentials private.
- Do not upload real patient records when testing or demonstrating the application.
- Use synthetic or sample data for development.
- Review database access policies before deploying the application.

## 🗺️ Development Roadmap

- [ ] Complete application rebranding.
- [ ] Improve dashboard and user experience.
- [ ] Review and improve PDF processing.
- [ ] Test AI analysis and conversational responses.
- [ ] Review authentication and session handling.
- [ ] Improve error handling and validation.
- [ ] Add testing and deployment documentation.

## 📄 License

This project retains the original project's MIT License. See the repository's `LICENSE` file for details.

## 🙏 Acknowledgements

This project builds upon the open-source **Health Insights Agent (HIA)** created by [Harsh Gajjar](https://github.com/harshhh28) and its contributors.

The original implementation is available at:

[github.com/harshhh28/hia](https://github.com/harshhh28/hia)

## 👨‍💻 Project Maintainer

**Raj Aditya Pal**

GitHub: [@rajadityapal05](https://github.com/rajadityapal05)
