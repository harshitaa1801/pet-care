# 🐾 PetCare AI Assistant

An AI-powered assistant built with Django + Django REST Framework that helps pet owners diagnose common pet health concerns by asking relevant follow-up questions and generating tailored remedies using Gemini AI.

---

## 🚀 Features

- 🔍 Analyze user queries about pet health
- 🤖 AI-powered follow-up questions
- 💊 Remedy generation based on Q&A
- 🔄 Chat-like flow using a single smart API
- 🧠 Session-aware without needing manual session IDs
- 📦 DRF browsable UI for quick interaction

---

## 🛠️ Tech Stack

- **Backend**: Django + DRF (Django REST Framework)
- **AI Service**: Gemini (Google's LLM API)
- **Database**: PostgreSQL
- **Session Management**: Django session framework
- **API UI**: DRF browsable interface

---

## 📦 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/harshitaa1801/pet-care.git
   cd pet-care
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
