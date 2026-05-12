from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'veda-secret-key-change-in-production'

# ── Database ──────────────────────────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), 'veda.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # prevents data loss
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name     TEXT NOT NULL,
            last_name      TEXT NOT NULL,
            email          TEXT NOT NULL,
            phone          TEXT,
            dosha          TEXT,
            interest       TEXT,
            message        TEXT,
            preferred_time TEXT,
            status         TEXT DEFAULT 'new',
            created_at     TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        INSERT OR IGNORE INTO admin_users (username, password)
        VALUES ('admin', 'veda123')
    ''')
    conn.commit()
    conn.close()

init_db()

# ── Admin auth decorator ───────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/doshas')
def doshas():
    return render_template('doshas.html')

@app.route('/doshas/vata')
def vata():
    return render_template('dosha_detail.html', dosha={
        'name': 'Vata', 'sanskrit': 'वात', 'elements': 'Space · Air', 'color': '#C4825A',
        'qualities': ['Dry', 'Light', 'Cold', 'Rough', 'Subtle', 'Mobile'],
        'balanced': ['Creative', 'Enthusiastic', 'Adaptable', 'Quick-minded', 'Energetic'],
        'imbalanced': ['Anxious', 'Scattered', 'Insomniac', 'Constipated', 'Fearful'],
        'foods': ['Warm, moist, heavy foods', 'Sweet, sour, salty tastes', 'Sesame oil', 'Warm milk', 'Root vegetables'],
        'avoid': ['Raw foods', 'Cold drinks', 'Bitter & astringent tastes', 'Excessive fasting'],
        'herbs': ['Ashwagandha', 'Shatavari', 'Triphala', 'Ginger', 'Licorice'],
        'desc': 'Vata is the energy of movement and governs all biological activities. It controls breathing, blinking, muscle movement, heart pulsation, and all movement in the cytoplasm and cell membranes.',
        'season': 'Autumn & Early Winter', 'time': 'Dawn (2–6 AM / PM)', 'emoji': '🌬️'
    })

@app.route('/doshas/pitta')
def pitta():
    return render_template('dosha_detail.html', dosha={
        'name': 'Pitta', 'sanskrit': 'पित्त', 'elements': 'Fire · Water', 'color': '#D4A847',
        'qualities': ['Hot', 'Sharp', 'Light', 'Oily', 'Liquid', 'Spreading'],
        'balanced': ['Intelligent', 'Courageous', 'Focused', 'Articulate', 'Joyful'],
        'imbalanced': ['Angry', 'Jealous', 'Critical', 'Inflammatory', 'Controlling'],
        'foods': ['Cool, heavy, slightly dry foods', 'Sweet, bitter, astringent tastes', 'Coconut', 'Coriander', 'Mint'],
        'avoid': ['Spicy foods', 'Alcohol', 'Fermented foods', 'Sour & pungent tastes'],
        'herbs': ['Brahmi', 'Shatavari', 'Amalaki', 'Neem', 'Turmeric'],
        'desc': 'Pitta is the energy of transformation. It governs digestion, absorption, assimilation, nutrition, metabolism, body temperature, skin color, and the luster of the eyes.',
        'season': 'Summer & Early Autumn', 'time': 'Midday (10 AM–2 PM)', 'emoji': '🔥'
    })

@app.route('/doshas/kapha')
def kapha():
    return render_template('dosha_detail.html', dosha={
        'name': 'Kapha', 'sanskrit': 'कफ', 'elements': 'Water · Earth', 'color': '#7A8C6E',
        'qualities': ['Heavy', 'Slow', 'Cool', 'Oily', 'Smooth', 'Dense'],
        'balanced': ['Calm', 'Compassionate', 'Patient', 'Stable', 'Loving'],
        'imbalanced': ['Lethargic', 'Possessive', 'Greedy', 'Congested', 'Resistant'],
        'foods': ['Light, dry, warm foods', 'Pungent, bitter, astringent tastes', 'Honey', 'Ginger', 'Legumes'],
        'avoid': ['Dairy', 'Oily foods', 'Sweet & salty tastes', 'Cold food & drink'],
        'herbs': ['Triphala', 'Trikatu', 'Guggulu', 'Punarnava', 'Tulsi'],
        'desc': "Kapha is the energy of structure and lubrication. It forms the body's structure — bones, muscles, tendons — and provides cohesion that holds cells together.",
        'season': 'Late Winter & Spring', 'time': 'Morning (6–10 AM)', 'emoji': '🌊'
    })

@app.route('/treatments')
def treatments():
    treatments_list = [
        {'name': 'Abhyanga',    'slug': 'abhyanga',    'icon': '🫙', 'tagline': 'Full-body warm oil massage',     'duration': '60 – 90 minutes',      'desc': 'A deeply nourishing massage performed with warm medicated oils, synchronised movements, and rhythmic strokes.'},
        {'name': 'Shirodhara',  'slug': 'shirodhara',  'icon': '🌊', 'tagline': 'Sacred oil stream therapy',      'duration': '45 – 60 minutes',      'desc': 'Warm oil flows in a steady stream over the third eye, inducing profound mental calm and neurological restoration.'},
        {'name': 'Panchakarma', 'slug': 'panchakarma', 'icon': '🌿', 'tagline': 'The ultimate Ayurvedic cleanse', 'duration': '7 – 21 day programme',  'desc': 'A comprehensive 5-action purification programme that detoxifies body and mind at the deepest cellular level.'},
        {'name': 'Nasyam',      'slug': 'nasyam',      'icon': '🔥', 'tagline': 'Nasal pathway therapy',          'duration': '30 – 45 minutes',      'desc': 'Medicated oils and herbal preparations administered through the nasal passages to clear the mind and sharpen senses.'},
        {'name': 'Udvartana',   'slug': 'udvartana',   'icon': '✨', 'tagline': 'Herbal powder scrub',             'duration': '45 – 60 minutes',      'desc': 'A vigorous dry powder massage using aromatic herbal powders to exfoliate, tone, and energise the body.'},
        {'name': 'Kati Basti',  'slug': 'kati-basti',  'icon': '💧', 'tagline': 'Lower back oil therapy',         'duration': '45 minutes',           'desc': 'Warm medicated oil is retained in a dough ring placed on the lower back to relieve chronic pain and stiffness.'},
    ]
    return render_template('treatments.html', treatments=treatments_list)

@app.route('/treatments/<slug>')
def treatment_detail(slug):
    details = {
        'abhyanga':    {'name':'Abhyanga',    'icon':'🫙', 'tagline':'Full-body warm oil massage',     'duration':'60 – 90 minutes',     'price':'From $120',   'desc':'Abhyanga is the Ayurvedic practice of full-body warm oil massage. Performed with specially prepared medicated oils chosen for your dosha, this treatment is one of the most important forms of self-care in Ayurveda.',  'benefits':['Nourishes all body tissues (dhatus)','Calms the nervous system','Improves lymphatic circulation','Softens and smooths skin','Promotes better sleep','Reduces Vata imbalances'],                                              'process':['Consultation and dosha assessment','Oil selection and warming','Synchronized two-therapist massage','Steam therapy (swedana)','Rest and integration'],                                         'ideal_for':'Vata imbalances, stress, dry skin, insomnia, joint stiffness'},
        'shirodhara':  {'name':'Shirodhara',  'icon':'🌊', 'tagline':'Sacred oil stream therapy',      'duration':'45 – 60 minutes',     'price':'From $150',   'desc':'Shirodhara is one of the most divine Ayurvedic treatments. A thin, steady stream of warm medicated oil is poured continuously over the forehead (the third eye), creating a deeply meditative state.',                           'benefits':['Profound mental relaxation','Reduces anxiety and depression','Improves sleep quality','Stimulates the pituitary gland','Balances the nervous system','Heightens intuition'],                        'process':['Head and neck massage preparation','Positioning on the treatment table','Continuous oil stream (30–45 min)','Head massage post-treatment','Guided rest period'],                                   'ideal_for':'Anxiety, insomnia, headaches, Vata & Pitta disorders, burnout'},
        'panchakarma': {'name':'Panchakarma', 'icon':'🌿', 'tagline':'The ultimate Ayurvedic cleanse', 'duration':'7 – 21 day programme','price':'From $2,500', 'desc':"Panchakarma is Ayurveda's most complete healing system — a series of five therapeutic actions designed to cleanse the body of toxins accumulated over years. A complete reset for body, mind, and spirit.",                       'benefits':['Deep cellular detoxification','Reverses chronic disease patterns','Restores dosha balance','Improves digestive fire (agni)','Anti-aging and rejuvenation','Mental and emotional clarity'],           'process':['Initial physician consultation','Preparatory oleation (snehana)','Preparatory sweating (swedana)','Five primary actions (tailored)','Post-cleanse rejuvenation (rasayana)'],                        'ideal_for':'Chronic conditions, weight management, complete rejuvenation, seasonal transitions'},
        'nasyam':      {'name':'Nasyam',      'icon':'🔥', 'tagline':'Nasal pathway therapy',          'duration':'30 – 45 minutes',     'price':'From $80',    'desc':'Nasyam involves the administration of medicated oils through the nasal passages. The nose is considered the gateway to the brain and consciousness in Ayurveda.',                                                                    'benefits':['Clears nasal passages','Improves mental clarity','Relieves headaches and migraines','Strengthens sense organs','Reduces neck and shoulder tension','Balances Vata in the head'],                    'process':['Facial and neck massage','Steam inhalation preparation','Oil/powder instillation','Expectoration guidance','Gargling and rest'],                                                                   'ideal_for':'Sinusitis, migraines, mental fog, speech disorders, anxiety'},
        'udvartana':   {'name':'Udvartana',   'icon':'✨', 'tagline':'Herbal powder scrub',             'duration':'45 – 60 minutes',     'price':'From $100',   'desc':'Udvartana is a unique Ayurvedic treatment using dry herbal powder pastes applied in vigorous upward strokes. Stimulating, warming, and particularly beneficial for Kapha types.',                                                    'benefits':['Exfoliates and tones skin','Reduces Kapha accumulation','Aids weight management','Improves skin texture','Energises the body','Reduces cellulite'],                                                 'process':['Herbal powder blend preparation','Dry application and massage','Steam treatment','Herbal bath','Moisturising finish'],                                                                              'ideal_for':'Kapha imbalances, weight management, poor circulation, sluggishness'},
        'kati-basti':  {'name':'Kati Basti',  'icon':'💧', 'tagline':'Lower back oil therapy',         'duration':'45 minutes',          'price':'From $90',    'desc':'Kati Basti is a specialised treatment where warm medicated oil is held within a dough ring placed on the lumbar region. The heat and medicinal properties penetrate deep into the tissues.',                                              'benefits':['Relieves lower back pain','Reduces disc-related issues','Nourishes spinal nerves','Improves flexibility','Reduces inflammation','Strengthens lumbar muscles'],                                      'process':['Lower back assessment','Dough ring preparation and placement','Warm oil filling and retention (30 min)','Gentle lower back massage','Rest and integration'],                                        'ideal_for':'Lower back pain, sciatica, disc problems, lumbar stiffness'},
    }
    detail = details.get(slug)
    if not detail:
        return render_template('404.html'), 404
    return render_template('treatment_detail.html', t=detail)

@app.route('/herbs')
def herbs():
    herbs_list = [
        {'name':'Ashwagandha', 'latin':'Withania somnifera',  'emoji':'🌱', 'dosha':'Vata',        'benefit':'Adaptogen · Stress Relief · Vitality',   'desc':"Known as Indian ginseng, Ashwagandha calms the nervous system and builds deep resilience to stress."},
        {'name':'Turmeric',    'latin':'Curcuma longa',       'emoji':'🟡', 'dosha':'Pitta',       'benefit':'Anti-inflammatory · Detox · Skin',        'desc':'Haridra — the golden healer. Purifies blood, reduces inflammation, sacred in Ayurvedic medicine.'},
        {'name':'Brahmi',      'latin':'Bacopa monnieri',     'emoji':'🍀', 'dosha':'All',         'benefit':'Cognitive · Memory · Calm',               'desc':'The herb of grace. Brahmi enhances mental performance and reduces anxiety.'},
        {'name':'Triphala',    'latin':'Three-fruit blend',   'emoji':'🫚', 'dosha':'All',         'benefit':'Digestion · Cleanse · Rejuvenation',      'desc':'A gentle daily detox and digestive tonic combining Amalaki, Bibhitaki, and Haritaki.'},
        {'name':'Shatavari',   'latin':'Asparagus racemosus', 'emoji':'🌸', 'dosha':'Vata · Pitta','benefit':'Female Health · Nourishment · Immunity',  'desc':'Queen of herbs — nourishes the reproductive system through all life stages.'},
        {'name':'Tulsi',       'latin':'Ocimum sanctum',      'emoji':'🌿', 'dosha':'Vata · Kapha','benefit':'Immunity · Spirit · Adaptogen',           'desc':'Holy Basil purifies the body and uplifts the spirit simultaneously.'},
        {'name':'Amalaki',     'latin':'Emblica officinalis', 'emoji':'🫐', 'dosha':'All',         'benefit':'Antioxidant · Vitamin C · Longevity',     'desc':'One of the richest natural sources of Vitamin C — cornerstone of Ayurvedic anti-aging.'},
        {'name':'Neem',        'latin':'Azadirachta indica',  'emoji':'🍃', 'dosha':'Pitta · Kapha','benefit':'Purifier · Skin · Blood',                'desc':'Purifies the blood, clears skin conditions, and is a powerful antimicrobial.'},
    ]
    return render_template('herbs.html', herbs=herbs_list)

@app.route('/philosophy')
def philosophy():
    return render_template('philosophy.html')

# ── Consultation — saves every booking permanently ────────────────────────────

@app.route('/consult', methods=['GET', 'POST'])
def consult():
    submitted = False
    if request.method == 'POST':
        conn = get_db()
        try:
            conn.execute('''
                INSERT INTO consultations
                    (first_name, last_name, email, phone, dosha, interest, message, preferred_time, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
            ''', (
                request.form.get('first_name', '').strip(),
                request.form.get('last_name',  '').strip(),
                request.form.get('email',      '').strip(),
                request.form.get('phone',      '').strip(),
                request.form.get('dosha',      ''),
                request.form.get('interest',   ''),
                request.form.get('message',    '').strip(),
                request.form.get('preferred_time', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            submitted = True
        except Exception as e:
            conn.rollback()
            print(f"Error saving booking: {e}")
        finally:
            conn.close()
    return render_template('consult.html', submitted=submitted)

# ═════════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES  →  /admin/login   username: admin   password: veda123
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM admin_users WHERE username=? AND password=?',
            (username, password)
        ).fetchone()
        conn.close()
        if user:
            session['admin_logged_in'] = True
            session['admin_username']  = username
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    total     = conn.execute('SELECT COUNT(*) FROM consultations').fetchone()[0]
    new_count = conn.execute("SELECT COUNT(*) FROM consultations WHERE status='new'").fetchone()[0]
    confirmed = conn.execute("SELECT COUNT(*) FROM consultations WHERE status='confirmed'").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM consultations WHERE status='completed'").fetchone()[0]
    recent    = conn.execute('SELECT * FROM consultations ORDER BY created_at DESC LIMIT 20').fetchall()
    conn.close()
    return render_template('admin/dashboard.html',
        total=total, new_count=new_count,
        confirmed=confirmed, completed=completed, recent=recent)

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    status_filter = request.args.get('status', '')
    search        = request.args.get('search', '')
    conn = get_db()
    query  = 'SELECT * FROM consultations WHERE 1=1'
    params = []
    if status_filter:
        query += ' AND status=?'
        params.append(status_filter)
    if search:
        query += ' AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)'
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    query   += ' ORDER BY created_at DESC'
    bookings = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('admin/bookings.html',
        bookings=bookings, status_filter=status_filter, search=search)

@app.route('/admin/bookings/<int:booking_id>')
@admin_required
def admin_booking_detail(booking_id):
    conn    = get_db()
    booking = conn.execute('SELECT * FROM consultations WHERE id=?', (booking_id,)).fetchone()
    conn.close()
    if not booking:
        return redirect(url_for('admin_bookings'))
    return render_template('admin/booking_detail.html', booking=booking)

@app.route('/admin/bookings/<int:booking_id>/status', methods=['POST'])
@admin_required
def admin_update_status(booking_id):
    new_status = request.form.get('status')
    if new_status in ('new', 'confirmed', 'completed', 'cancelled'):
        conn = get_db()
        conn.execute('UPDATE consultations SET status=? WHERE id=?', (new_status, booking_id))
        conn.commit()
        conn.close()
    return redirect(url_for('admin_booking_detail', booking_id=booking_id))

@app.route('/admin/bookings/<int:booking_id>/delete', methods=['POST'])
@admin_required
def admin_delete_booking(booking_id):
    conn = get_db()
    conn.execute('DELETE FROM consultations WHERE id=?', (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bookings'))

# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
