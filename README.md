# Veda — Ayurvedic Wellness Website (Flask)

A full multi-page Flask website for an Ayurvedic wellness centre.

## Pages

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/doshas` | Doshas overview |
| `/doshas/vata` | Vata dosha detail |
| `/doshas/pitta` | Pitta dosha detail |
| `/doshas/kapha` | Kapha dosha detail |
| `/treatments` | All treatments listing |
| `/treatments/abhyanga` | Abhyanga detail |
| `/treatments/shirodhara` | Shirodhara detail |
| `/treatments/panchakarma` | Panchakarma detail |
| `/treatments/nasyam` | Nasyam detail |
| `/treatments/udvartana` | Udvartana detail |
| `/treatments/kati-basti` | Kati Basti detail |
| `/herbs` | Sacred herbs gallery |
| `/philosophy` | Ayurvedic philosophy |
| `/consult` | Consultation booking form |

## Setup

```bash
# 1. Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Project Structure

```
veda_flask/
├── app.py               # Flask routes
├── requirements.txt
├── templates/
│   ├── base.html        # Shared layout (nav + footer)
│   ├── index.html       # Home
│   ├── doshas.html      # Doshas overview
│   ├── dosha_detail.html# Vata / Pitta / Kapha detail
│   ├── treatments.html  # Treatments list
│   ├── treatment_detail.html
│   ├── herbs.html
│   ├── philosophy.html
│   ├── consult.html
│   └── 404.html
└── static/
    ├── css/main.css
    └── js/main.js
```
------------------------------------------------

**Developer**

Build by Aswathy Salikumar
