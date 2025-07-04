
# 🧳 AI Travel Planner

## Overview

**AI Travel Planner** is a modern, full-stack web application that helps users plan their trips with the power of AI. It generates personalized travel itineraries, budget analyses, travel tips, and recommendations based on user profiles, preferences, and real-time data. The project leverages advanced prompt engineering, a graph-based traveler profile system, and integrates with external APIs for flights and hotels.

---
## 📚 Table of Contents

- [🧳 Overview](#-overview)
- [✨ Features](#-features)
- [🛠️ Technologies Used](#-technologies-used)
- [📁 Project Structure](#-project-structure)
- [📝 How It Works](#-how-it-works)
- [⚙️ Requirements](#️-requirements)
- [🔐 Environment Variables](#-environment-variables)
- [🚀 How to Run](#-how-to-run)
- [📷 Demo / Screenshots](#-demo--screenshots)
- [🙋‍♂️ Authors & Contributors](#-authors--contributors)
- [📄 License](#-license)
- [💡 Inspiration](#-inspiration)
- [🤝 Contributing](#-contributing)

---


## ✨ Features

- **User Registration & Authentication** (with email verification and password reset)
- **Graph-Based Traveler Profile** (budget, interests, previous trips, visa info, preferences)
- **Personalized AI Itinerary Generation** (using LLaMA model via Groq API)
- **Budget Analysis & Travel Tips** (AI-generated, context-aware)
- **Flight & Hotel Search** (via Tavily and Booking.com APIs)
- **Downloadable Profile & Trip History (CSV)**
- **Modern, Responsive UI** (Tailwind CSS, beautiful templates)
- **Secure Password Hashing**
- **Email Notifications** (verification, password reset)
- **Profile & Plan Management** (edit, delete, clear, download)

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Frontend:** HTML, Tailwind CSS, Jinja2 Templates
- **Database:** SQLite (via SQLAlchemy ORM)
- **AI/ML:** Groq API (LLaMA model), Prompt Engineering
- **Graph Operations:** NetworkX (for in-memory traveler profile graph)
- **APIs:** Tavily (flights), Booking.com (hotels)
- **Email:** Gmail SMTP (for verification and password reset)
- **Other:** dotenv, requests, smtplib, werkzeug.security

---

## 📦 Project Structure

```
Flask project folder/
│
├── traveler_planer.py         # Main Flask app (routes, logic)
├── traveler_profile.py        # Traveler profile graph system
├── prompt_engine.py           # Prompt engineering for AI
├── groq_json_test.py          # (Optional) Test for Groq API
├── test_phase3.py             # (Optional) Test cases
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── templates/                 # HTML templates (Jinja2)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── plan_detail.html
│   ├── plan_edit.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── verify.html
│
├── static/                    # Static files (images, CSS)
│   └── images/
│       └── airport_bg.jpg
│
├── instance/
│   └── travel_planner.db     
│
└── venv/                     
```

---

## 🚀 Why We Developed This Project

- **Personalized Travel Planning:** Most travel apps are generic. We wanted to create a system that truly understands the traveler—budget, interests, history, and preferences.
- **AI-Powered Recommendations:** Harnessing LLaMA's power for real, actionable, and creative travel plans.
- **Modern User Experience:** Clean, beautiful, and responsive UI for all devices.
- **Learning & Innovation:** To explore prompt engineering, graph-based user modeling, and real-world API integrations.

---

## 📝 How It Works

1. ✅ User registers and verifies email via Gmail SMTP.
2. ✍️ User sets travel preferences (budget, visa info, interests, etc.).
3. 🧠 Graph-based profile is created using NetworkX.
4. 💡 Groq (LLaMA model) generates:
   - Itinerary
   - Budget analysis
   - Travel tips & recommendations
5. 🔎 Tavily & Booking.com APIs fetch real-time flights and hotels.
6. 📊 All plans are saved; user can view, edit, delete, or download.
7. 🔐 Forgot password? Reset securely via email.

---

## ⚙️ Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies:
  - Flask
  - Flask-SQLAlchemy
  - python-dotenv
  - requests
  - networkx
  - werkzeug
  - smtplib
  - email
  - etc.

---

## 🔑 Environment Variables

Create a `.env` file in your project root with:

```
SECRET_KEY=your_flask_secret_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
RAPIDAPI_KEY=your_rapidapi_key
GMAIL_USER=your_gmail_address@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
```

**Note:** Use a Gmail App Password, not your main Gmail password.

---

## 🏁 How to Run

1. **Clone the repository:**
   ```
   git clone <your-repo-url>
   cd Flask project folder
   ```

2. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate # On Mac/Linux
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up your `.env` file** (see above).

5. **Run the app:**
   ```
   python traveler_planer.py
   ```

6. **Open in browser:**  
   Visit [http://localhost:5000](http://localhost:5000)

---

## 📤 What Not to Upload to GitHub

- `instance/travel_planner.db` (database)
- `venv/` (virtual environment)
- `.env` (contains secrets)
- Any `.json` files with personal data

Add a `.gitignore` file:

```
venv/
__pycache__/
*.pyc
instance/
.env
*.db
*.sqlite3
*.json
```

---

## 🧠 Technologies & Concepts Explained

- **Flask:** Lightweight Python web framework.
- **Flask-SQLAlchemy:** ORM for database operations.
- **NetworkX:** Graph library for modeling user profiles.
- **Prompt Engineering:** Custom prompts for LLaMA to generate structured, relevant travel plans.
- **Groq API:** Access to LLaMA model for AI text generation.
- **Tavily & Booking.com APIs:** Real-time flight and hotel data.
- **Tailwind CSS:** Utility-first CSS for beautiful, responsive UI.
- **Jinja2:** Templating engine for dynamic HTML.
- **Email (SMTP):** For verification and password reset.

---
📷 Demo / Screenshots
<img width="960" alt="image" src="https://github.com/user-attachments/assets/8b8b296d-5b0d-4f4c-ac6f-6f88c27eaeda" />
<img width="960" alt="image" src="https://github.com/user-attachments/assets/561ce724-5875-47d8-83f6-f5d1b9fa335e" />
<img width="960" alt="image" src="https://github.com/user-attachments/assets/03a10460-1b35-4bb3-87c1-15e2f0482602" />
<img width="960" alt="image" src="https://github.com/user-attachments/assets/9b5abbf7-fd96-4360-9420-004cc9af4d08" />
<img width="931" alt="image" src="https://github.com/user-attachments/assets/935c01f4-3d56-413a-b080-6da2df204e13" />
<img width="905" alt="image" src="https://github.com/user-attachments/assets/54658174-3b46-4bd2-b996-13f7a24565e8" />


## 🙋‍♂️ Authors & Contributors

- [Ahmad gul]
- [Muqaddas Akram]
- [Habiba sidique]
- [usama]

---

## 📄 License

[MIT License] 
MIT License

Copyright (c) 2025 [Ahmad gul]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
THE SOFTWARE.


---

## 💡 Inspiration

This project was inspired by the need for truly personalized, AI-powered travel planning that goes beyond generic recommendations and puts the traveler at the center of the experience.

---
🤝 Contributing
Pull requests are welcome!
1. Fork this repo
2. git checkout -b feature-branch
3. git commit -m "Add your feature"
4. git push origin feature-branch
5. Open a Pull Request
 
