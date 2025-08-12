#  <img width="150" height="150" alt="ResumeParser_AI-removebg-preview" src="https://github.com/user-attachments/assets/39796a03-8ba9-4bd9-b503-8775f05ad7c4" align='center'/> ResumeParser AI

A web-based application that parses resumes (PDF/DOCX/TXT) and extracts key candidate information like name, contact details, skills, education, and experience. It supports Google OAuth login, secure file uploads, and downloads parsed data in JSON, CSV, or Excel formats.

---

## 🚀 Preview
<img width="1896" height="866" alt="Screenshot 2025-07-25 122534" src="https://github.com/user-attachments/assets/3c83af8d-6835-426c-9c06-f28f162e1fab" />
<img width="1897" height="868" alt="Screenshot 2025-07-25 122559" src="https://github.com/user-attachments/assets/e9b27022-2895-4abe-bcb0-179047c36758" />
<img width="1897" height="865" alt="Screenshot 2025-07-25 122352" src="https://github.com/user-attachments/assets/275247b8-8acc-450a-ad4a-10aeda96fc4e" />
<img width="1895" height="866" alt="Screenshot 2025-07-25 122655" src="https://github.com/user-attachments/assets/714df115-f793-4279-94a1-a5e41fd96bd5" />

---

## 🔗 Quick Links

| Resource        | URL                                                                 |
|-----------------|----------------------------------------------------------------------|
| 🌐 Live Website | [resumeparserai.up.railway.app](https://resumeparserai.up.railway.app/) |
| 🧪 API Endpoint | `/parsing`                                                           |
| 🎨 Figma Design | [View Figma UI](https://www.figma.com/design/6rskr0FavJcplTdbOKtLyY/ResumeParser.ai?node-id=0-1&t=TvwWS3h9CsNmeZGu-1) |
| 📄 Terms Page   | [/terms-and-conditions](https://resumeparserai.up.railway.app/terms-and-conditions) |
| 🔒 Privacy Page | [/privacy-policy](https://resumeparserai.up.railway.app/privacy-policy) |

---

## ✨ Features

- 🔐 Google OAuth 2.0 Authentication
- 📄 Upload & Parse PDF/DOCX/TXT resumes
- 📊 Download structured data (JSON/CSV/Excel)
- 💾 MongoDB integration for resume storage
- 🌐 Hosted on [Railway](https://railway.app)
- 🔍 Resume section identification using NLP
- 📁 Beautiful frontend built with HTML/CSS/JS

---

## 🛠️ Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **OAuth**: Google OAuth 2.0 via Flask-Dance
- **Database**: MongoDB
- **Hosting**: Railway.app
- **Design**: Figma

---

## 🧩 Installation & Setup (For Local Development)

```bash
git clone https://github.com/TAK-PRAVEEN/ResumeParser.ai.git
cd resume-parser-ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file and add your credentials:
```.env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```
Then run the server:
```bash
python app.py
```

---

## 📂 Project Structure
```vbnet
resume-parser-ai/
│
├── frontend/
│   ├── templates/
│   └── static/
├── resume_parser.py
├── app.py
├── database/
│   └── user_ops.py, resume_ops.py
├── uploads/
├── requirements.txt
└── .env
```

---

## 📬 Contact
Have questions or want to contribute?

📧 Email: praveentak715@gmail.com

---

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
