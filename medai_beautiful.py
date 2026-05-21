import streamlit as st
from groq import Groq
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64
from PIL import Image
from io import BytesIO
import json
import os
import bcrypt
from datetime import datetime
import PyPDF2
import speech_recognition as sr
import io

st.set_page_config(
    page_title="MedAI — Medical Super Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme state ──
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Dynamic CSS based on theme ──
if st.session_state.dark_mode:
    BG = "#0A0F0D"; CARD = "#111916"; BORDER = "#1D9E75"
    TEXT = "#F0F7F4"; TEXT2 = "#8BA89E"; ACCENT = "#1D9E75"
    SIDEBAR = "#0D1411"; INPUT = "#1A2420"
else:
    BG = "#F0F7F4"; CARD = "#FFFFFF"; BORDER = "#C8E6D8"
    TEXT = "#1A3D2E"; TEXT2 = "#6B9E8A"; ACCENT = "#1D9E75"
    SIDEBAR = "#FFFFFF"; INPUT = "#FFFFFF"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    font-family: 'Inter', sans-serif !important;
    color: {TEXT} !important;
}}
#MainMenu, footer, header, [data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stSidebar"] {{
    background: {SIDEBAR} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
.stButton > button {{
    background: {CARD} !important;
    border: 1.5px solid {BORDER} !important;
    color: {TEXT2} !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    transition: all 0.2s !important;
}}
.stButton > button:hover {{
    background: rgba(29,158,117,0.1) !important;
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
}}
.stButton > button[kind="primary"] {{
    background: {ACCENT} !important;
    border-color: {ACCENT} !important;
    color: white !important;
    font-weight: 600 !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: #178A64 !important;
    box-shadow: 0 6px 20px rgba(29,158,117,0.35) !important;
}}
.stTextInput > div > div > input {{
    background: {INPUT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stChatInputContainer"] {{
    background: {INPUT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 16px !important;
}}
[data-testid="stChatMessage"] {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin: 8px 0 !important;
}}
[data-testid="stChatMessage"] p {{ color: {TEXT} !important; font-size: 14px !important; line-height: 1.7 !important; }}
.stSelectbox > div > div {{ background: {INPUT} !important; border: 1.5px solid {BORDER} !important; border-radius: 10px !important; color: {TEXT} !important; }}
[data-testid="stFileUploader"] {{ background: {INPUT} !important; border: 2px dashed {BORDER} !important; border-radius: 14px !important; }}
.streamlit-expanderHeader {{ background: {CARD} !important; border: 1px solid {BORDER} !important; border-radius: 10px !important; color: {TEXT2} !important; }}
.streamlit-expanderContent {{ background: {BG} !important; border: 1px solid {BORDER} !important; }}
.stTabs [data-baseweb="tab-list"] {{ background: {INPUT} !important; border-radius: 12px !important; padding: 4px !important; }}
.stTabs [data-baseweb="tab"] {{ background: transparent !important; border-radius: 8px !important; color: {TEXT2} !important; font-weight: 500 !important; }}
.stTabs [aria-selected="true"] {{ background: {ACCENT} !important; color: white !important; }}
.stSuccess {{ background: rgba(29,158,117,0.1) !important; border: 1.5px solid {ACCENT} !important; border-radius: 10px !important; color: {TEXT} !important; }}
.stWarning {{ background: rgba(245,158,11,0.1) !important; border: 1.5px solid #F59E0B !important; border-radius: 10px !important; }}
.stError {{ background: rgba(239,68,68,0.1) !important; border: 1.5px solid #EF4444 !important; border-radius: 10px !important; }}
.stInfo {{ background: rgba(59,130,246,0.1) !important; border: 1.5px solid #3B82F6 !important; border-radius: 10px !important; }}
[data-testid="stMetric"] {{ background: {CARD} !important; border: 1px solid {BORDER} !important; border-radius: 14px !important; padding: 16px 20px !important; }}
[data-testid="stMetricLabel"] {{ color: {TEXT2} !important; }}
[data-testid="stMetricValue"] {{ color: {ACCENT} !important; font-weight: 700 !important; }}
hr {{ border-color: {BORDER} !important; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {ACCENT}; border-radius: 3px; }}

.medai-hero {{
    background: linear-gradient(135deg, #1D9E75 0%, #0D6E4E 100%);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 16px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(29,158,117,0.3);
}}
.medai-hero h1 {{
    font-family: 'Sora', sans-serif !important;
    font-size: 32px !important;
    font-weight: 700 !important;
    color: white !important;
    margin: 0 0 6px 0 !important;
}}
.medai-hero p {{ font-size: 14px !important; color: rgba(255,255,255,0.85) !important; margin: 0 !important; }}
.medai-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px; padding: 4px 14px; font-size: 12px; color: white; font-weight: 500; margin-top: 10px;
}}
.stat-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
    padding: 16px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
.stat-number {{ font-family: 'Sora', sans-serif; font-size: 26px; color: {ACCENT}; font-weight: 700; }}
.stat-label {{ font-size: 11px; color: {TEXT2}; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; font-weight: 500; }}
.sidebar-brand {{ text-align: center; padding: 16px 0 12px; }}
.sidebar-brand .icon {{ font-size: 38px; display: block; margin-bottom: 6px; }}
.sidebar-brand h2 {{ font-family: 'Sora', sans-serif !important; font-size: 20px !important; font-weight: 700 !important; color: {ACCENT} !important; margin: 0 0 2px !important; }}
.sidebar-brand p {{ font-size: 10px !important; color: {TEXT2} !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin: 0 !important; }}
.user-card {{ background: rgba(29,158,117,0.1); border: 1.5px solid rgba(29,158,117,0.3); border-radius: 12px; padding: 10px 14px; margin-bottom: 8px; }}
.user-card .label {{ font-size: 10px; color: {TEXT2}; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; }}
.user-card .name {{ font-size: 14px; font-weight: 600; color: {ACCENT}; margin-top: 2px; }}
.nav-label {{ font-size: 10px; color: {TEXT2}; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin: 10px 0 5px; }}
.source-item {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px; padding: 7px 11px; margin: 3px 0; font-size: 12px; }}
.source-item a {{ color: {ACCENT} !important; text-decoration: none; font-weight: 500; }}
.page-header {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; padding: 20px 24px; margin-bottom: 16px; }}
.page-header h2 {{ font-family: 'Sora', sans-serif !important; font-size: 22px !important; font-weight: 700 !important; color: {ACCENT} !important; margin: 0 0 4px !important; }}
.page-header p {{ font-size: 13px !important; color: {TEXT2} !important; margin: 0 !important; }}
.footer-credit {{ text-align: center; padding: 12px 0 6px; border-top: 1px solid {BORDER}; margin-top: 12px; }}
.footer-credit p {{ font-size: 10px !important; color: {TEXT2} !important; margin: 2px 0 !important; }}
.sos-btn {{
    background: #EF4444 !important; color: white !important; border: none !important;
    border-radius: 50px !important; padding: 12px 24px !important;
    font-size: 16px !important; font-weight: 700 !important; cursor: pointer !important;
    width: 100% !important; margin: 8px 0 !important;
    box-shadow: 0 4px 20px rgba(239,68,68,0.4) !important;
    animation: pulse-red 2s infinite !important;
}}
@keyframes pulse-red {{ 0%,100% {{ box-shadow: 0 4px 20px rgba(239,68,68,0.4); }} 50% {{ box-shadow: 0 4px 30px rgba(239,68,68,0.7); }} }}
.drug-card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 14px; margin: 8px 0; }}
.drug-safe {{ border-left: 4px solid #1D9E75 !important; }}
.drug-danger {{ border-left: 4px solid #EF4444 !important; }}
.drug-warning {{ border-left: 4px solid #F59E0B !important; }}
.wizard-step {{
    background: {CARD}; border: 1.5px solid {BORDER}; border-radius: 16px;
    padding: 20px; margin: 10px 0;
}}
.wizard-progress {{
    background: {INPUT}; border-radius: 50px; height: 8px; margin: 12px 0;
    overflow: hidden;
}}
.wizard-bar {{
    background: {ACCENT}; height: 100%; border-radius: 50px;
    transition: width 0.3s ease;
}}
.health-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
    padding: 16px; margin: 8px 0;
}}
.reminder-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 12px 16px; margin: 6px 0;
    display: flex; align-items: center; gap: 12px;
}}
</style>
""", unsafe_allow_html=True)

# ── Groq Client ──
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
except:
    GROQ_KEY = os.environ.get("GROQ_KEY", "")

if not GROQ_KEY:
    st.error("⚠️ Groq API key not found! Add GROQ_KEY to Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_KEY)
MODEL = "llama-3.1-8b-instant"

# ── Database ──
USERS_DB = "medai_users.json"
HISTORY_DB = "medai_history.json"
HEALTH_DB = "medai_health.json"
REMINDERS_DB = "medai_reminders.json"

def load_db(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_db(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ── Session State ──
defaults = {
    "current_user": None, "chat_history": [], "page": "chat",
    "auto_question": "", "voice_processed": None, "dark_mode": False,
    "wizard_step": 0, "wizard_answers": {}, "wizard_active": False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Core Functions ──
def search_everywhere(query):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmax=3&format=json", timeout=8)
        for pmid in r.json()["esearchresult"]["idlist"][:3]:
            results.append({"source": "PubMed", "title": f"Research paper", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
    except: pass
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}", timeout=8)
        if r.status_code == 200:
            d = r.json()
            results.append({"source": "Wikipedia", "title": d.get("title",""), "url": d.get("content_urls",{}).get("desktop",{}).get("page","")})
    except: pass
    try:
        r = requests.get(f"https://api.fda.gov/drug/label.json?search={urllib.parse.quote(query)}&limit=2", timeout=8)
        if r.status_code == 200:
            for d in r.json().get("results",[])[:2]:
                name = d.get("openfda",{}).get("brand_name",["Unknown"])[0]
                results.append({"source": "OpenFDA", "title": f"Drug: {name}", "url": "https://open.fda.gov"})
    except: pass
    try:
        r = requests.get(f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query+' medical')}", timeout=8, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for l in soup.find_all("a", {"class": "result__a"})[:4]:
            results.append({"source": "Web", "title": l.get_text(strip=True)[:80], "url": l.get("href","")})
    except: pass
    return results

def ask_medai(question, username=None, system_extra=""):
    system_prompt = f"""You are MedAI — Medical Super Intelligence — the world's most helpful medical AI.

CRITICAL RULES — NEVER BREAK THESE:
1. ALWAYS give a direct, complete answer — NEVER say "I cannot provide" or "I am unable to"
2. If someone asks for books — give real free download links (archive.org, NCBI, OpenStax, etc.)
3. If someone asks math — solve it step by step with full working
4. If someone asks for study materials — provide them directly with URLs
5. If someone asks exam questions — generate them with full answers and explanations
6. If someone asks anything medical — answer it completely, no limits
7. ALWAYS provide step by step process when explaining anything
8. ALWAYS include free resource links when mentioning books/resources
9. NEVER be vague — be specific, exact, complete
10. Format answers clearly with sections, bullet points, numbered steps

You cover EVERYTHING medical:
- All diseases, conditions, symptoms, treatments
- All medical subjects — anatomy, physiology, pathology, pharmacology, surgery
- Drug interactions, dosages, mechanisms
- Medical calculations and formulas
- Exam preparation — MCQs, mock tests, study plans
- Free medical books and resources with direct links
- Mental health, nutrition, emergency medicine
- Ayurveda, alternative medicine, research papers
- Everything from patient care to PhD research

Always remind to consult a real doctor for personal medical decisions.
{system_extra}"""
    if username:
        users = load_db(USERS_DB)
        if username in users:
            profile = users[username]["profile"]
            profile_text = ", ".join([f"{k}: {v}" for k,v in profile.items() if v])
            if profile_text:
                system_prompt += f"\n\nPatient profile: {profile_text}\nPersonalize answer."
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": question}],
        max_tokens=2048, temperature=0.7
    )
    return response.choices[0].message.content

def analyze_image(img, question):
    buffer = BytesIO()
    img.thumbnail((800, 800))
    img.save(buffer, format="JPEG", quality=85)
    img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}},
            {"type": "text", "text": f"You are MedAI. Analyze this image as a medical expert. Question: {question}. Provide: what you see, medical analysis, body part, normal vs abnormal, possible conditions, next steps, when to see doctor."}
        ]}],
        max_tokens=1024
    )
    return response.choices[0].message.content

def analyze_pdf(pdf_file, question):
    reader = PyPDF2.PdfReader(pdf_file)
    text = "".join([p.extract_text() or "" for p in reader.pages])
    if len(text) > 6000:
        text = text[:6000]
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MedAI — expert at analyzing medical documents. Give complete analysis, explain medical terms simply, highlight important values, flag concerns, suggest next steps."},
            {"role": "user", "content": f"Question: {question}\n\nDocument:\n{text}"}
        ],
        max_tokens=2048
    )
    return response.choices[0].message.content

def save_history(username, question, answer):
    history = load_db(HISTORY_DB)
    if username not in history:
        history[username] = []
    history[username].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "question": question, "answer": answer[:500]
    })
    save_db(HISTORY_DB, history)

def process_voice(audio):
    recognizer = sr.Recognizer()
    audio_bytes = audio.read()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        languages = ["en-US","hi-IN","te-IN","ta-IN","ar-SA","zh-CN","es-ES","fr-FR","de-DE","ja-JP","ko-KR","ru-RU","pt-BR"]
        for lang in languages:
            try:
                text = recognizer.recognize_google(audio_data, language=lang)
                if text:
                    return text
            except: continue
    except: pass
    return None

def generate_pdf_report(title, content, username=None):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"MedAI Medical Report", styles['Title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    if username:
        story.append(Paragraph(f"Patient: {username}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(title, styles['Heading1']))
    story.append(Spacer(1, 6))
    for line in content.split('\n'):
        if line.strip():
            try:
                story.append(Paragraph(line, styles['Normal']))
            except: pass
    doc.build(story)
    buffer.seek(0)
    return buffer

# ══════════════════════════════
# SIDEBAR
# ══════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        <svg width="80" height="80" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:0 auto 8px;">
            <circle cx="256" cy="256" r="256" fill="#0D6E4E"/>
            <circle cx="256" cy="256" r="232" fill="#1D9E75"/>
            <rect x="218" y="140" width="76" height="232" rx="16" fill="white"/>
            <rect x="140" y="218" width="232" height="76" rx="16" fill="white"/>
            <circle cx="256" cy="256" r="28" fill="#0D6E4E"/>
            <circle cx="245" cy="250" r="5" fill="white"/>
            <circle cx="267" cy="250" r="5" fill="white"/>
            <circle cx="256" cy="265" r="5" fill="white"/>
            <polyline points="60,256 100,256 120,210 140,302 160,240 180,256 210,256" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>
            <polyline points="302,256 330,256 350,210 370,302 390,240 410,256 452,256" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>
        </svg>
        <h2 style="font-family:Georgia,serif !important;font-size:22px !important;font-weight:700 !important;margin:0 !important;">
            <span style="color:#0D6E4E;">Med</span><span style="color:#1D9E75;">AI</span>
        </h2>
        <p style="font-size:10px !important;color:{TEXT2} !important;text-transform:uppercase !important;letter-spacing:0.12em !important;margin:4px 0 0 !important;">Medical Super Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # Dark mode toggle
    col_a, col_b = st.columns([3,1])
    with col_a:
        st.markdown(f'<div style="font-size:13px;color:{TEXT2};padding-top:6px;">{"🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"}</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("Switch", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.divider()

    if st.session_state.current_user:
        st.markdown(f"""
        <div class="user-card">
            <div class="label">Logged in as</div>
            <div class="name">👤 {st.session_state.current_user}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()
    else:
        if st.button("🔐 Login / Register", use_container_width=True, type="primary"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown(f'<div class="nav-label">Navigate</div>', unsafe_allow_html=True)
    pages = [
        ("💬", "Chat", "chat"),
        ("🔍", "Symptom Checker", "symptom"),
        ("💊", "Drug Checker", "drug"),
        ("📊", "Health Dashboard", "dashboard"),
        ("⏰", "Medicine Reminders", "reminders"),
        ("🗺️", "Hospital Finder", "hospital"),
        ("🚨", "Emergency SOS", "emergency"),
        ("📸", "Image Analysis", "image"),
        ("🫀", "Medical Diagrams", "diagrams"),
        ("📄", "PDF Analysis", "pdf"),
        ("🎓", "Medical Education", "education"),
        ("🔬", "Medical Search", "search"),
        ("📚", "History", "history"),
        ("👤", "My Profile", "profile"),
    ]
    for icon, label, page_id in pages:
        if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{page_id}"):
            st.session_state.page = page_id
            st.rerun()

    st.markdown(f"""
    <div class="footer-credit">
        <p>Built by Manish Reddy Chamakuri</p>
        <p>SUNY Polytechnic Institute · 2026</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════
# PAGES
# ══════════════════════════════

# ── CHAT PAGE ──
if st.session_state.page == "chat":
    st.markdown(f"""
    <div class="medai-hero">
        <div style="display:flex;align-items:center;gap:20px;">
            <svg width="64" height="64" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
                <circle cx="256" cy="256" r="256" fill="rgba(255,255,255,0.2)"/>
                <circle cx="256" cy="256" r="232" fill="rgba(255,255,255,0.15)"/>
                <rect x="218" y="140" width="76" height="232" rx="16" fill="white"/>
                <rect x="140" y="218" width="232" height="76" rx="16" fill="white"/>
                <circle cx="256" cy="256" r="28" fill="rgba(13,110,78,0.8)"/>
                <circle cx="245" cy="250" r="5" fill="white"/>
                <circle cx="267" cy="250" r="5" fill="white"/>
                <circle cx="256" cy="265" r="5" fill="white"/>
                <polyline points="60,256 110,256 130,210 150,302 170,240 190,256 218,256" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
                <polyline points="294,256 322,256 342,210 362,302 382,240 402,256 452,256" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
            </svg>
            <div>
                <h1 style="font-family:Georgia,serif !important;font-size:36px !important;font-weight:700 !important;color:white !important;margin:0 0 4px !important;">
                    Med<span style="opacity:0.85;">AI</span>
                </h1>
                <p style="font-size:14px !important;color:rgba(255,255,255,0.85) !important;margin:0 !important;">Medical Super Intelligence — Ask anything, get expert answers instantly</p>
                <div class="medai-badge" style="margin-top:10px;">🌍 50+ languages · 15+ sources · 110+ features · Free Forever</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="stat-card"><div class="stat-number">110+</div><div class="stat-label">Features</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="stat-card"><div class="stat-number">50+</div><div class="stat-label">Sources</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-number">50+</div><div class="stat-label">Languages</div></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="stat-card"><div class="stat-number">∞</div><div class="stat-label">Questions</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history — oldest top, newest bottom
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:40px 20px;color:{TEXT2};">
            <div style="font-size:48px;margin-bottom:12px;">🏥</div>
            <div style="font-size:18px;font-weight:600;color:{ACCENT};margin-bottom:6px;">Welcome to MedAI!</div>
            <div style="font-size:14px;">Ask any medical question, upload a photo, PDF or use voice</div>
        </div>
        """, unsafe_allow_html=True)

    # Auto question handler
    if st.session_state.auto_question:
        auto_q = st.session_state.auto_question
        st.session_state.auto_question = ""
        st.session_state.chat_history.append({"role": "user", "content": auto_q})
        with st.spinner("🔍 Searching + thinking..."):
            answer = ask_medai(auto_q, st.session_state.current_user)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        if st.session_state.current_user:
            save_history(st.session_state.current_user, auto_q, answer)
        st.rerun()

    # Quick questions
    with st.expander("💡 Quick Questions — tap to open"):
        c1, c2 = st.columns(2)
        qs = ["What causes chest pain?","Symptoms of diabetes?","How does cancer develop?",
              "Signs of heart attack?","How to boost immunity?","What causes headache?",
              "How to treat depression?","Signs of stroke?","What is Alzheimer's?","How does chemotherapy work?"]
        for i, q in enumerate(qs):
            with c1 if i % 2 == 0 else c2:
                if st.button(q, key=f"q_{i}", use_container_width=True):
                    st.session_state.auto_question = q
                    st.rerun()

    # Attach options — Camera, Photo, PDF
    with st.expander("📎 Attach — Camera · Photo · PDF"):
        t1, t2, t3 = st.tabs(["📷 Camera", "🖼️ Upload Photo", "📄 Upload PDF"])

        with t1:
            st.caption("Point camera at body part, skin, food, X-ray, prescription")
            cam_img = st.camera_input("Take photo", key="camera_input", label_visibility="collapsed")
            cam_q = st.text_input("What to analyze?", "Give full medical analysis", key="cam_q")
            if cam_img and st.button("🔍 Analyze Camera Photo", type="primary", use_container_width=True, key="btn_cam"):
                img = Image.open(cam_img).convert("RGB")
                col1, col2 = st.columns(2)
                with col1: st.image(img, caption="Your photo", use_container_width=True)
                with col2:
                    with st.spinner("🔍 Analyzing..."): result = analyze_image(img, cam_q)
                    st.markdown(result)
                st.session_state.chat_history.append({"role": "user", "content": "📷 [Sent a camera photo]"})
                st.session_state.chat_history.append({"role": "assistant", "content": f"📷 **Camera Analysis:**\n{result}"})
                if st.session_state.current_user:
                    save_history(st.session_state.current_user, "Camera photo analysis", result)
                st.success("✅ Added to chat!")

        with t2:
            st.caption("Upload any medical image from your device")
            img_file = st.file_uploader("Choose image", type=["jpg","jpeg","png","webp"], key="chat_img", label_visibility="collapsed")
            img_q = st.text_input("What to analyze?", "Give full medical analysis", key="img_q")
            if img_file and st.button("🔍 Analyze Image", type="primary", use_container_width=True, key="btn_img"):
                img = Image.open(img_file).convert("RGB")
                col1, col2 = st.columns(2)
                with col1: st.image(img, caption="Uploaded image", use_container_width=True)
                with col2:
                    with st.spinner("🔍 Analyzing..."): result = analyze_image(img, img_q)
                    st.markdown(result)
                st.session_state.chat_history.append({"role": "user", "content": "🖼️ [Uploaded an image]"})
                st.session_state.chat_history.append({"role": "assistant", "content": f"🖼️ **Image Analysis:**\n{result}"})
                if st.session_state.current_user:
                    save_history(st.session_state.current_user, "Image analysis", result)
                st.success("✅ Added to chat!")

        with t3:
            st.caption("Upload any medical PDF — blood test, prescription, research paper")
            pdf_file = st.file_uploader("Choose PDF", type=["pdf"], key="chat_pdf", label_visibility="collapsed")
            pdf_q = st.text_input("What to analyze?", "Give complete medical analysis", key="pdf_q")
            if pdf_file and st.button("🔍 Analyze PDF", type="primary", use_container_width=True, key="btn_pdf"):
                with st.spinner("📄 Reading PDF..."): result = analyze_pdf(pdf_file, pdf_q)
                st.markdown(result)
                st.session_state.chat_history.append({"role": "user", "content": f"📄 [Uploaded {pdf_file.name}]"})
                st.session_state.chat_history.append({"role": "assistant", "content": f"📄 **PDF Analysis:**\n{result}"})
                if st.session_state.current_user:
                    save_history(st.session_state.current_user, f"PDF: {pdf_file.name}", result)
                # Download report
                report = generate_pdf_report(f"PDF Analysis: {pdf_file.name}", result, st.session_state.current_user)
                st.download_button("📥 Download Report as PDF", report, "MedAI_Report.pdf", "application/pdf")
                st.success("✅ Added to chat!")

    # Voice input
    st.markdown(f"""
    <div style="background:{CARD};border:1.5px solid {BORDER};border-radius:16px;
    padding:10px 18px;margin:8px 0;">
        <div style="font-size:13px;font-weight:600;color:{ACCENT};margin-bottom:2px;">🎤 Voice Input</div>
        <div style="font-size:11px;color:{TEXT2};">Tap mic → speak in ANY language → AI answers instantly</div>
    </div>
    """, unsafe_allow_html=True)
    audio = st.audio_input("", key="voice_input", label_visibility="collapsed")
    if audio and audio != st.session_state.voice_processed:
        st.session_state.voice_processed = audio
        with st.spinner("🎤 Understanding..."):
            voice_text = process_voice(audio)
        if voice_text:
            st.success(f"🎤 You said: **{voice_text}**")
            st.session_state.chat_history.append({"role": "user", "content": voice_text})
            with st.spinner("🔍 MedAI thinking..."):
                answer = ask_medai(voice_text, st.session_state.current_user)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            if st.session_state.current_user:
                save_history(st.session_state.current_user, voice_text, answer)
            st.rerun()
        else:
            st.warning("⚠️ Could not understand. Speak clearly!")

    # Text chat input
    if question := st.chat_input("Type any medical question in any language..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("🔍 Searching + thinking..."):
            answer = ask_medai(question, st.session_state.current_user)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        if st.session_state.current_user:
            save_history(st.session_state.current_user, question, answer)
        with st.expander("📚 Sources"):
            for s in search_everywhere(question):
                if s.get("url"):
                    st.markdown(f'<div class="source-item">🔗 <a href="{s["url"]}" target="_blank">[{s["source"]}] {s.get("title","")[:50]}</a></div>', unsafe_allow_html=True)
        st.rerun()

# ── SYMPTOM CHECKER WIZARD ──
elif st.session_state.page == "symptom":
    st.markdown('<div class="page-header"><h2>🔍 Symptom Checker</h2><p>Step by step — AI narrows down your condition like a doctor would</p></div>', unsafe_allow_html=True)

    wizard_questions = [
        {"q": "What is your main symptom?", "options": ["Chest pain","Headache","Fever","Stomach pain","Breathing difficulty","Back pain","Skin problem","Fatigue","Dizziness","Other"]},
        {"q": "How long have you had this symptom?", "options": ["Less than 24 hours","1-3 days","4-7 days","1-2 weeks","More than 2 weeks","More than a month"]},
        {"q": "How severe is it?", "options": ["Mild — I can manage","Moderate — affecting daily life","Severe — very painful","Extreme — emergency level"]},
        {"q": "Do you have any of these also?", "options": ["Fever","Nausea/vomiting","Shortness of breath","Sweating","None of these","Multiple of these"]},
        {"q": "Any existing medical conditions?", "options": ["None","Diabetes","High blood pressure","Heart disease","Asthma","Cancer","Other"]},
    ]

    step = st.session_state.wizard_step
    total = len(wizard_questions)

    # Progress bar
    progress = int((step / total) * 100)
    st.markdown(f"""
    <div class="wizard-progress">
        <div class="wizard-bar" style="width:{progress}%"></div>
    </div>
    <div style="font-size:12px;color:{TEXT2};margin-bottom:12px;">Step {min(step+1, total)} of {total}</div>
    """, unsafe_allow_html=True)

    if step < total:
        q_data = wizard_questions[step]
        st.markdown(f'<div class="wizard-step"><div style="font-size:18px;font-weight:600;color:{ACCENT};margin-bottom:16px;">{q_data["q"]}</div></div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, opt in enumerate(q_data["options"]):
            with cols[i % 2]:
                if st.button(opt, key=f"wiz_{step}_{i}", use_container_width=True):
                    st.session_state.wizard_answers[q_data["q"]] = opt
                    st.session_state.wizard_step += 1
                    st.rerun()
    else:
        # All answered — get AI diagnosis
        st.success("✅ Analysis complete!")
        answers_text = "\n".join([f"{k}: {v}" for k,v in st.session_state.wizard_answers.items()])
        with st.spinner("🔍 MedAI analyzing your symptoms..."):
            result = ask_medai(
                f"Patient symptom assessment:\n{answers_text}\n\nProvide: possible conditions (most to least likely), urgency level, recommended next steps, warning signs to watch for, when to go to emergency.",
                st.session_state.current_user
            )
        st.markdown("### 🏥 MedAI Assessment")
        st.markdown(result)

        # Download report
        report = generate_pdf_report("Symptom Assessment Report", f"Symptoms:\n{answers_text}\n\nAssessment:\n{result}", st.session_state.current_user)
        st.download_button("📥 Download Report as PDF", report, "MedAI_Symptom_Report.pdf", "application/pdf")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.wizard_step = 0
                st.session_state.wizard_answers = {}
                st.rerun()
        with col2:
            if st.button("💬 Ask More Questions", use_container_width=True, type="primary"):
                st.session_state.page = "chat"
                st.rerun()

# ── DRUG INTERACTION CHECKER ──
elif st.session_state.page == "drug":
    st.markdown('<div class="page-header"><h2>💊 Drug Interaction Checker</h2><p>Check if your medicines are safe to take together — potentially life saving</p></div>', unsafe_allow_html=True)

    st.markdown("#### Enter your medicines:")
    drug1 = st.text_input("Medicine 1", placeholder="e.g. Aspirin, Metformin, Lisinopril", key="drug1")
    drug2 = st.text_input("Medicine 2", placeholder="e.g. Warfarin, Ibuprofen, Atorvastatin", key="drug2")
    drug3 = st.text_input("Medicine 3 (optional)", placeholder="e.g. Omeprazole", key="drug3")
    drug4 = st.text_input("Medicine 4 (optional)", placeholder="e.g. Amlodipine", key="drug4")

    if st.button("🔍 Check Drug Interactions", type="primary", use_container_width=True):
        drugs = [d for d in [drug1, drug2, drug3, drug4] if d.strip()]
        if len(drugs) < 2:
            st.warning("⚠️ Please enter at least 2 medicines!")
        else:
            drug_list = ", ".join(drugs)
            with st.spinner("🔍 Checking interactions..."):
                result = ask_medai(
                    f"Drug interaction check for: {drug_list}\n\nProvide:\n1. Safety rating (Safe/Caution/Dangerous)\n2. Each drug pair interaction explained\n3. Side effects to watch\n4. Timing recommendations\n5. What to tell your doctor\n6. Alternative medicines if dangerous",
                    system_extra="You are an expert pharmacist. Be specific and clear about drug interactions."
                )
            st.markdown("### 💊 Interaction Analysis")
            st.markdown(result)
            report = generate_pdf_report(f"Drug Interaction Report: {drug_list}", result, st.session_state.current_user)
            st.download_button("📥 Download Report", report, "MedAI_Drug_Report.pdf", "application/pdf")

    st.divider()
    st.markdown("#### Common interactions to check:")
    common = ["Aspirin + Warfarin","Metformin + Alcohol","Ibuprofen + Blood pressure medicine","Statins + Grapefruit","SSRIs + Tramadol"]
    for c in common:
        if st.button(c, key=f"common_{c}"):
            parts = c.split(" + ")
            st.session_state.auto_question = f"Check drug interaction between {parts[0]} and {parts[1]}"
            st.session_state.page = "chat"
            st.rerun()

# ── HEALTH DASHBOARD ──
elif st.session_state.page == "dashboard":
    st.markdown('<div class="page-header"><h2>📊 Health Dashboard</h2><p>Track your health metrics over time — BP, sugar, weight and more</p></div>', unsafe_allow_html=True)

    if not st.session_state.current_user:
        st.warning("⚠️ Please login to track your health!")
        if st.button("Login", type="primary"): st.session_state.page = "login"; st.rerun()
    else:
        health_data = load_db(HEALTH_DB)
        user_health = health_data.get(st.session_state.current_user, {"bp": [], "sugar": [], "weight": [], "oxygen": []})

        # Add new reading
        st.markdown("#### Add Today's Reading:")
        c1, c2, c3, c4 = st.columns(4)
        with c1: bp = st.text_input("Blood Pressure", placeholder="120/80", key="bp_input")
        with c2: sugar = st.text_input("Blood Sugar (mg/dL)", placeholder="100", key="sugar_input")
        with c3: weight = st.text_input("Weight (kg)", placeholder="70", key="weight_input")
        with c4: oxygen = st.text_input("Oxygen (%)", placeholder="98", key="oxygen_input")

        if st.button("➕ Save Reading", type="primary", use_container_width=True):
            today = datetime.now().strftime("%Y-%m-%d %H:%M")
            if bp: user_health["bp"].append({"date": today, "value": bp})
            if sugar: user_health["sugar"].append({"date": today, "value": sugar})
            if weight: user_health["weight"].append({"date": today, "value": weight})
            if oxygen: user_health["oxygen"].append({"date": today, "value": oxygen})
            health_data[st.session_state.current_user] = user_health
            save_db(HEALTH_DB, health_data)
            st.success("✅ Reading saved!")
            st.rerun()

        st.divider()

        # Show latest readings
        st.markdown("#### Your Latest Readings:")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("🫀 Blood Pressure", user_health["bp"][-1]["value"] if user_health["bp"] else "No data", help="Normal: 120/80")
        with m2: st.metric("🩸 Blood Sugar", user_health["sugar"][-1]["value"] if user_health["sugar"] else "No data", help="Normal: 70-100 mg/dL")
        with m3: st.metric("⚖️ Weight", user_health["weight"][-1]["value"] if user_health["weight"] else "No data")
        with m4: st.metric("💨 Oxygen", user_health["oxygen"][-1]["value"] if user_health["oxygen"] else "No data", help="Normal: 95-100%")

        # History table
        if any(user_health[k] for k in ["bp","sugar","weight","oxygen"]):
            st.divider()
            st.markdown("#### Reading History:")
            all_readings = []
            for key in ["bp","sugar","weight","oxygen"]:
                for r in user_health[key][-5:]:
                    all_readings.append({"Date": r["date"], "Type": key.upper(), "Value": r["value"]})
            if all_readings:
                import pandas as pd
                df = pd.DataFrame(all_readings)
                st.dataframe(df, use_container_width=True)

            # AI analysis
            if st.button("🤖 Get MedAI Health Analysis", type="primary", use_container_width=True):
                readings_text = f"Latest readings: BP={user_health['bp'][-1]['value'] if user_health['bp'] else 'N/A'}, Sugar={user_health['sugar'][-1]['value'] if user_health['sugar'] else 'N/A'}, Weight={user_health['weight'][-1]['value'] if user_health['weight'] else 'N/A'}, Oxygen={user_health['oxygen'][-1]['value'] if user_health['oxygen'] else 'N/A'}"
                with st.spinner("🔍 Analyzing your health data..."):
                    analysis = ask_medai(f"{readings_text}\n\nAnalyze these health readings. Are they normal? Any concerns? What should this person do?", st.session_state.current_user)
                st.markdown("### 🏥 MedAI Health Analysis")
                st.markdown(analysis)

# ── MEDICINE REMINDERS ──
elif st.session_state.page == "reminders":
    st.markdown('<div class="page-header"><h2>⏰ Medicine Reminders</h2><p>Never miss a dose — set your medicine schedule here</p></div>', unsafe_allow_html=True)

    if not st.session_state.current_user:
        st.warning("⚠️ Please login to set reminders!")
        if st.button("Login", type="primary"): st.session_state.page = "login"; st.rerun()
    else:
        reminders = load_db(REMINDERS_DB)
        user_reminders = reminders.get(st.session_state.current_user, [])

        # Add reminder
        st.markdown("#### Add New Medicine Reminder:")
        c1, c2, c3 = st.columns(3)
        with c1: med_name = st.text_input("Medicine Name", placeholder="e.g. Metformin 500mg")
        with c2: med_time = st.text_input("Time", placeholder="e.g. 8:00 AM, After lunch")
        with c3: med_freq = st.selectbox("Frequency", ["Once daily","Twice daily","Three times daily","Every 8 hours","Weekly","As needed"])

        med_notes = st.text_input("Notes", placeholder="e.g. Take with food, Avoid alcohol")

        if st.button("➕ Add Reminder", type="primary", use_container_width=True):
            if med_name and med_time:
                user_reminders.append({
                    "medicine": med_name,
                    "time": med_time,
                    "frequency": med_freq,
                    "notes": med_notes,
                    "added": datetime.now().strftime("%Y-%m-%d")
                })
                reminders[st.session_state.current_user] = user_reminders
                save_db(REMINDERS_DB, reminders)
                st.success(f"✅ Reminder added for {med_name}!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter medicine name and time!")

        st.divider()

        # Show reminders
        if user_reminders:
            st.markdown(f"#### Your Medicine Schedule — {len(user_reminders)} medicines:")
            for i, r in enumerate(user_reminders):
                col1, col2 = st.columns([4,1])
                with col1:
                    st.markdown(f"""
                    <div class="reminder-card">
                        <div style="font-size:24px;">💊</div>
                        <div>
                            <div style="font-size:15px;font-weight:600;color:{ACCENT};">{r['medicine']}</div>
                            <div style="font-size:13px;color:{TEXT2};">⏰ {r['time']} · {r['frequency']}</div>
                            {f'<div style="font-size:12px;color:{TEXT2};">📝 {r["notes"]}</div>' if r.get('notes') else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️ Delete", key=f"del_rem_{i}", use_container_width=True):
                        user_reminders.pop(i)
                        reminders[st.session_state.current_user] = user_reminders
                        save_db(REMINDERS_DB, reminders)
                        st.rerun()

            # Check interactions of all medicines
            if st.button("🔍 Check All Medicine Interactions", type="primary", use_container_width=True):
                med_list = ", ".join([r["medicine"] for r in user_reminders])
                with st.spinner("🔍 Checking interactions..."):
                    result = ask_medai(f"Check interactions between all these medicines: {med_list}\n\nAre there any dangerous combinations? What should the patient know?")
                st.markdown("### 💊 Interaction Check")
                st.markdown(result)
        else:
            st.info("No reminders yet — add your medicines above!")

# ── SMART HOSPITAL FINDER ──
elif st.session_state.page == "hospital":
    st.markdown('<div class="page-header"><h2>🗺️ Smart Hospital Finder</h2><p>Find best hospitals · Top doctors · Ratings · Prices · Treatment costs · Open now</p></div>', unsafe_allow_html=True)

    hosp_tab1, hosp_tab2, hosp_tab3, hosp_tab4 = st.tabs(["🏥 Find Hospital", "👨‍⚕️ Find Doctor", "💰 Cost Estimator", "🗺️ Open Maps"])

    with hosp_tab1:
        st.markdown("#### 🏥 Find Best Hospital Near You")
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Your location / address", placeholder="e.g. Utica, NY or 123 Main St, New York")
            condition = st.text_input("Your condition / symptom", placeholder="e.g. chest pain, broken leg, diabetes")
        with col2:
            speciality = st.selectbox("Speciality needed", [
                "General / Emergency", "Cardiology", "Dermatology", "Orthopedics",
                "Neurology", "Gynecology", "Pediatrics", "Psychiatry", "Oncology",
                "Ophthalmology", "Dentistry", "Urology", "Gastroenterology",
                "Pulmonology", "Endocrinology", "Pharmacy", "ICU / Critical Care"
            ])
            urgency = st.selectbox("Urgency", ["Emergency — need help now", "Urgent — within today", "Semi-urgent — within week", "Routine — can wait"])

        if location and st.button("🔍 Find Best Hospitals", type="primary", use_container_width=True, key="find_hosp"):
            with st.spinner("🔍 Searching and ranking hospitals..."):
                result = ask_medai(
                    f"""Find the BEST hospitals near: {location}
Condition: {condition or 'General'}
Speciality: {speciality}
Urgency: {urgency}

Provide for TOP 5 hospitals:
## Hospital [Number]: [Name]
⭐ Rating: [X/5 stars — based on public reviews]
📍 Address: [Full address]
📞 Phone: [Number]
🕐 Hours: [Open hours / 24hrs emergency]
🏆 Speciality: [What they are best at]
💰 Approximate Cost: [Consultation fee range]
✅ Why recommended: [2-3 specific reasons]
🔗 Google Maps: https://www.google.com/maps/search/[hospital+name+location]

After listing hospitals:
## What to do right now:
- Step by step instructions based on urgency level
- What to bring / documents needed
- Insurance tips
- What to say when you arrive""",
                    system_extra="You have knowledge of real hospitals worldwide. Provide specific, accurate information. Always include Google Maps search links. Base ratings on publicly known reputation."
                )

            st.markdown("### 🏥 Best Hospitals For You")
            st.markdown(result)

            # Quick map buttons
            st.markdown("#### 🗺️ Open in Maps:")
            c1, c2, c3 = st.columns(3)
            query = urllib.parse.quote(f"{speciality} hospital near {location}")
            with c1:
                st.markdown(f'<a href="https://www.google.com/maps/search/{query}" target="_blank" style="background:#1D9E75;color:white;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:600;font-size:13px;display:block;text-align:center;">🗺️ Google Maps</a>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<a href="https://maps.apple.com/?q={query}" target="_blank" style="background:#333;color:white;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:600;font-size:13px;display:block;text-align:center;">🍎 Apple Maps</a>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<a href="https://www.bing.com/maps?q={query}" target="_blank" style="background:#0078D4;color:white;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:600;font-size:13px;display:block;text-align:center;">🔷 Bing Maps</a>', unsafe_allow_html=True)

            report = generate_pdf_report("Hospital Finder Report", result, st.session_state.current_user)
            st.download_button("📥 Download Hospital List as PDF", report, "MedAI_Hospitals.pdf", "application/pdf")

    with hosp_tab2:
        st.markdown("#### 👨‍⚕️ Find Best Doctor Near You")
        col1, col2 = st.columns(2)
        with col1:
            doc_location = st.text_input("Your location", placeholder="e.g. Chicago, IL", key="doc_loc")
            doc_condition = st.text_input("Your condition", placeholder="e.g. back pain, skin rash, depression", key="doc_cond")
        with col2:
            doc_speciality = st.selectbox("Doctor type", [
                "General Physician / Family Doctor", "Cardiologist", "Dermatologist",
                "Orthopedic Surgeon", "Neurologist", "Gynecologist / OB-GYN",
                "Pediatrician", "Psychiatrist / Therapist", "Oncologist",
                "Ophthalmologist", "Dentist", "Urologist", "Gastroenterologist",
                "Endocrinologist", "Pulmonologist", "Rheumatologist"
            ], key="doc_spec")
            doc_insurance = st.text_input("Insurance (optional)", placeholder="e.g. Blue Cross, Medicare, Uninsured", key="doc_ins")

        if doc_location and st.button("🔍 Find Best Doctors", type="primary", use_container_width=True, key="find_doc"):
            with st.spinner("🔍 Searching and ranking doctors..."):
                result = ask_medai(
                    f"""Find the BEST {doc_speciality} doctors near: {doc_location}
Condition: {doc_condition or 'General consultation'}
Insurance: {doc_insurance or 'Not specified'}

For TOP 5 doctors provide:
## Dr. [Name]
⭐ Rating: [X/5 — based on public patient reviews]
🏥 Hospital/Clinic: [Where they practice]
📍 Address: [Full address]
📞 Phone: [Number]
🕐 Availability: [Days and hours]
🎓 Qualifications: [Degrees and specializations]
💰 Consultation Fee: [Approximate cost]
✅ Why best: [Specific expertise relevant to condition]
👥 Patient Reviews Summary: [What patients say publicly]
🔗 Book/Find: https://www.google.com/maps/search/[doctor+name+location]

Also provide:
- Questions to ask this doctor
- What to bring to appointment
- Red flags to watch for
- When to get a second opinion""",
                    system_extra="Provide accurate doctor information based on publicly known medical professionals. Always include booking/map links."
                )
            st.markdown("### 👨‍⚕️ Best Doctors For You")
            st.markdown(result)

            query = urllib.parse.quote(f"{doc_speciality} near {doc_location}")
            st.markdown(f'<a href="https://www.google.com/maps/search/{query}" target="_blank" style="background:#1D9E75;color:white;padding:10px 20px;border-radius:10px;text-decoration:none;font-weight:600;">🗺️ Search All {doc_speciality}s on Google Maps</a>', unsafe_allow_html=True)

            report = generate_pdf_report("Doctor Finder Report", result, st.session_state.current_user)
            st.download_button("📥 Download Doctor List as PDF", report, "MedAI_Doctors.pdf", "application/pdf")

    with hosp_tab3:
        st.markdown("#### 💰 Medical Cost Estimator")
        st.caption("Estimate costs for consultations, tests, surgeries and treatments")

        col1, col2 = st.columns(2)
        with col1:
            cost_country = st.selectbox("Country", ["USA", "India", "UK", "Canada", "Australia", "Germany", "UAE", "Singapore", "Other"])
            cost_type = st.selectbox("Type of cost", [
                "Doctor consultation fee",
                "Emergency room visit",
                "Blood test panel",
                "MRI scan",
                "CT scan",
                "X-ray",
                "Surgery cost",
                "Hospital stay per day",
                "Medicine / prescription",
                "Dental treatment",
                "Mental health therapy",
                "Physiotherapy session"
            ])
        with col2:
            cost_procedure = st.text_input("Specific procedure / test", placeholder="e.g. appendix surgery, full blood count, knee replacement")
            cost_insurance = st.selectbox("Insurance status", ["No insurance — paying out of pocket", "Private insurance", "Government / Medicare / Medicaid", "Not sure"])

        if st.button("💰 Estimate Costs", type="primary", use_container_width=True, key="est_cost"):
            with st.spinner("🔍 Calculating costs..."):
                result = ask_medai(
                    f"""Medical cost estimation:
Country: {cost_country}
Type: {cost_type}
Procedure: {cost_procedure or cost_type}
Insurance: {cost_insurance}

Provide:
## 💰 Cost Breakdown

### Without Insurance:
- Minimum cost: $X
- Average cost: $X
- Maximum cost: $X
- What affects the price

### With Insurance:
- Typical copay: $X
- Deductible consideration: $X
- What is usually covered

### How to Reduce Costs:
1. [Tip 1]
2. [Tip 2]
3. [Tip 3]

### Free / Low Cost Alternatives:
- [Option 1 with details]
- [Option 2 with details]

### Questions to Ask Before Paying:
- [Question 1]
- [Question 2]

### Medical Tourism Option:
- Same procedure in nearby affordable country
- Estimated savings""",
                    system_extra="Provide accurate, realistic cost estimates based on real healthcare pricing. Be specific with numbers. Help people save money."
                )
            st.markdown("### 💰 Cost Estimate")
            st.markdown(result)
            report = generate_pdf_report("Medical Cost Estimate", result, st.session_state.current_user)
            st.download_button("📥 Download Cost Report", report, "MedAI_Cost_Report.pdf", "application/pdf")

    with hosp_tab4:
        st.markdown("#### 🗺️ Open Medical Maps")
        st.caption("Find hospitals, clinics, pharmacies, labs on maps — click to open")

        map_location = st.text_input("Your location", placeholder="e.g. Utica, NY or your city", key="map_loc")
        map_type = st.selectbox("What to find", [
            "Hospitals", "Emergency rooms", "Clinics", "Pharmacies",
            "Diagnostic labs", "Dental clinics", "Eye clinics",
            "Mental health centers", "Physical therapy", "Blood banks"
        ], key="map_type")

        if map_location:
            query = urllib.parse.quote(f"{map_type} near {map_location}")
            st.markdown("#### Open in your preferred map:")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <a href="https://www.google.com/maps/search/{query}" target="_blank"
                   style="display:block;background:#1D9E75;color:white;padding:12px;
                   border-radius:12px;text-decoration:none;text-align:center;font-weight:600;">
                   🗺️ Google Maps
                </a>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <a href="https://maps.apple.com/?q={query}" target="_blank"
                   style="display:block;background:#555;color:white;padding:12px;
                   border-radius:12px;text-decoration:none;text-align:center;font-weight:600;">
                   🍎 Apple Maps
                </a>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <a href="https://www.bing.com/maps?q={query}" target="_blank"
                   style="display:block;background:#0078D4;color:white;padding:12px;
                   border-radius:12px;text-decoration:none;text-align:center;font-weight:600;">
                   🔷 Bing Maps
                </a>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <a href="https://waze.com/ul?q={query}" target="_blank"
                   style="display:block;background:#33CCFF;color:#333;padding:12px;
                   border-radius:12px;text-decoration:none;text-align:center;font-weight:600;">
                   🚗 Waze
                </a>""", unsafe_allow_html=True)

            # Embedded map iframe
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="border-radius:16px;overflow:hidden;border:2px solid {BORDER};">
                <iframe
                    src="https://www.google.com/maps/embed/v1/search?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU3aLo&q={query}"
                    width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy">
                </iframe>
            </div>
            <div style="font-size:11px;color:{TEXT2};margin-top:6px;">
                If map does not load, click the map buttons above to open directly ↑
            </div>
            """, unsafe_allow_html=True)

            # AI powered nearby analysis
            if st.button("🤖 Get AI Analysis of Best Options Nearby", type="primary", use_container_width=True, key="ai_map"):
                with st.spinner("🔍 Analyzing best options near you..."):
                    result = ask_medai(
                        f"""Smart analysis for {map_type} near {map_location}:

1. Best known {map_type} in this area (with ratings from public sources)
2. Which ones are highest rated — based on Google/public reviews
3. Which accept walk-ins vs appointment only
4. Which have shortest wait times typically
5. Which are most affordable
6. Operating hours comparison
7. Parking / transport accessibility
8. Special services available
9. Direct links to find each one:
   - Google Maps search links
   - Hospital websites if known
10. Tips for choosing the right one for different situations""",
                        system_extra="Use publicly known information about medical facilities. Provide specific, accurate data about real facilities when possible."
                    )
                st.markdown("### 🤖 AI Analysis")
                st.markdown(result)

# ── EMERGENCY SOS ──
elif st.session_state.page == "emergency":
    st.markdown('<div class="page-header"><h2>🚨 Emergency SOS</h2><p>Life threatening emergency? Get help immediately</p></div>', unsafe_allow_html=True)

    # Big red SOS button
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0;">
        <div style="font-size:80px;margin-bottom:12px;">🚨</div>
        <div style="font-size:22px;font-weight:700;color:#EF4444;margin-bottom:8px;">EMERGENCY SOS</div>
        <div style="font-size:14px;color:{TEXT2};margin-bottom:20px;">Call emergency services immediately in a life-threatening situation</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#EF4444;color:white;border-radius:16px;padding:20px;text-align:center;font-size:18px;font-weight:700;">
            🇺🇸 USA<br>📞 911
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#EF4444;color:white;border-radius:16px;padding:20px;text-align:center;font-size:18px;font-weight:700;">
            🇮🇳 India<br>📞 108
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#EF4444;color:white;border-radius:16px;padding:20px;text-align:center;font-size:18px;font-weight:700;">
            🌍 Global<br>📞 112
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # First aid guides
    st.markdown("### 🩺 Immediate First Aid Guides")
    emergency_type = st.selectbox("Select emergency:", [
        "Heart Attack", "Stroke", "Choking", "Severe Bleeding",
        "Burns", "Drowning", "Seizure", "Allergic Reaction / Anaphylaxis",
        "Diabetic Emergency", "Drug Overdose", "Broken Bone", "Electric Shock"
    ])

    if st.button(f"🆘 Get First Aid for {emergency_type}", type="primary", use_container_width=True):
        with st.spinner("🔍 Getting emergency guide..."):
            result = ask_medai(
                f"Emergency first aid guide for {emergency_type}. Provide step by step immediate actions. Be clear, numbered, urgent. Include what NOT to do. Include when to call ambulance.",
                system_extra="This is an emergency situation. Be extremely clear, direct, and concise. Number every step."
            )
        st.markdown(f"### 🆘 {emergency_type} — First Aid")
        st.markdown(result)

    st.divider()
    st.markdown("### 🧰 What to Keep in Your First Aid Kit")
    if st.button("📋 Show First Aid Kit List", use_container_width=True):
        with st.spinner("Loading..."):
            result = ask_medai("List complete first aid kit contents for home use. Organize by category. Include quantity needed and why each item is important.")
        st.markdown(result)

# ── MEDICAL DIAGRAMS ──
elif st.session_state.page == "diagrams":
    st.markdown('<div class="page-header"><h2>🫀 Medical Diagrams</h2><p>Upload any diagram for analysis · Generate any diagram · Interactive learning · Download and share</p></div>', unsafe_allow_html=True)

    diag_tab1, diag_tab2, diag_tab3 = st.tabs(["📷 Analyze Diagram", "✏️ Generate Diagram", "🎓 Learn with Diagrams"])

    with diag_tab1:
        st.markdown("#### 📷 Upload Any Medical Diagram")
        st.caption("Upload photo of textbook diagram, hand-drawn diagram, X-ray, ECG, pathology slide — AI explains everything")

        diag_mode = st.radio("", ["📷 Camera", "🖼️ Upload"], horizontal=True, label_visibility="collapsed", key="diag_mode")
        if diag_mode == "📷 Camera":
            diag_img = st.camera_input("Take photo of diagram", key="diag_cam", label_visibility="collapsed")
        else:
            diag_img = st.file_uploader("Upload diagram image", type=["jpg","jpeg","png","webp"], key="diag_img", label_visibility="collapsed")

        diag_q = st.text_input("What do you want to know?", "Analyze this diagram completely — label every part and explain", key="diag_q")

        if diag_img and st.button("🔍 Analyze Diagram", type="primary", use_container_width=True, key="btn_diag"):
            img = Image.open(diag_img).convert("RGB")
            col1, col2 = st.columns(2)
            with col1:
                st.image(img, caption="Your diagram", use_container_width=True)
            with col2:
                with st.spinner("🔍 Analyzing diagram..."):
                    result = analyze_image(img,
                        f"{diag_q}. Also: 1) Name every labeled part visible 2) Explain what each part does 3) Describe the process shown 4) Common exam questions on this diagram 5) What this diagram is from (textbook/subject)")
                st.markdown("### 🏥 Diagram Analysis")
                st.markdown(result)
            report = generate_pdf_report("Diagram Analysis", result, st.session_state.current_user)
            st.download_button("📥 Download Analysis as PDF", report, "MedAI_Diagram_Analysis.pdf", "application/pdf")

    with diag_tab2:
        st.markdown("#### ✏️ Generate Any Medical Diagram")
        st.caption("Type what diagram you want → AI draws it with labels and explanations")

        diagram_types = [
            "Heart — chambers, valves, blood flow",
            "Brain — lobes and functions",
            "Kidney — nephron structure",
            "Lung — airways and alveoli",
            "Digestive system — complete",
            "Cell — organelles labeled",
            "DNA replication process",
            "Immune response pathway",
            "Blood circulation complete",
            "ECG waves — PQRST explained",
            "Neuron structure and synapse",
            "Hormone feedback loops",
            "Custom — type your own",
        ]
        selected_diagram = st.selectbox("Choose diagram", diagram_types, key="diag_select")
        if selected_diagram == "Custom — type your own":
            custom_diag = st.text_input("Describe the diagram you want", placeholder="e.g. Mechanism of action of beta blockers")
            diagram_topic = custom_diag
        else:
            diagram_topic = selected_diagram

        diag_detail = st.selectbox("Detail level", ["Simple — for beginners", "Standard — for students", "Advanced — for doctors"], key="diag_detail")

        if diagram_topic and st.button("✏️ Generate Diagram", type="primary", use_container_width=True, key="btn_gen_diag"):
            with st.spinner("🔍 Creating your diagram..."):
                result = ask_medai(
                    f"""Create a detailed text-based diagram/schematic for: {diagram_topic}
Detail level: {diag_detail}

Provide:
1. ASCII/text diagram showing the structure with labels:
   Use lines, arrows, and text to draw it clearly
   Example format:
   [Part A] ──→ [Part B] ──→ [Part C]
       ↑               ↓
   [Part D] ←── [Part E]

2. Labels explained — what each labeled part does
3. Process description — step by step what happens
4. Key numbers to remember (measurements, values)
5. Clinical relevance — why this matters
6. Common exam questions about this diagram
7. How to draw/remember this diagram

Make it clear enough to copy into notes.""",
                    system_extra="Create clear text-based diagrams using ASCII art, arrows, and structured layouts. Be creative with text diagrams."
                )
            st.markdown(f"### 🫀 {diagram_topic}")
            st.markdown(result)
            report = generate_pdf_report(f"Medical Diagram: {diagram_topic}", result, st.session_state.current_user)
            st.download_button("📥 Download Diagram + Notes as PDF", report, "MedAI_Diagram.pdf", "application/pdf")

    with diag_tab3:
        st.markdown("#### 🎓 Learn with Interactive Diagrams")
        st.caption("Quiz mode — blank diagram → you label it → AI checks your answers")

        learn_topic = st.selectbox("Choose body system to learn", [
            "Heart and Cardiovascular", "Brain and Nervous System", "Lungs and Respiratory",
            "Kidney and Urinary", "Digestive System", "Skeletal System", "Muscular System",
            "Endocrine System", "Immune System", "Reproductive System"
        ], key="learn_topic")

        learn_mode = st.radio("Learning mode", ["📖 Teach me this system", "📝 Quiz me on this system", "🔍 Explain this diagram part"], horizontal=True, label_visibility="visible", key="learn_mode")

        if learn_mode == "📖 Teach me this system":
            if st.button("🎓 Teach Me", type="primary", use_container_width=True, key="teach_btn"):
                with st.spinner("🔍 Preparing lesson..."):
                    result = ask_medai(
                        f"""Teach the {learn_topic} system completely:
1. Overview and main function
2. All major parts with descriptions (as a labeled diagram in text)
3. How it works — step by step process
4. Connection with other body systems
5. Common diseases of this system
6. Key facts for exams
7. Memory tricks to remember the parts
8. Free resource links to learn more""",
                        system_extra="Be a great teacher. Use text diagrams, clear explanations, mnemonics. Always provide free learning URLs."
                    )
                st.markdown(f"### 📖 {learn_topic} — Complete Lesson")
                st.markdown(result)
                report = generate_pdf_report(f"Lesson: {learn_topic}", result, st.session_state.current_user)
                st.download_button("📥 Download Lesson as PDF", report, "MedAI_Lesson.pdf", "application/pdf")

        elif learn_mode == "📝 Quiz me on this system":
            num_quiz = st.slider("Number of questions", 5, 20, 10, key="quiz_count")
            if st.button("📝 Start Quiz", type="primary", use_container_width=True, key="quiz_btn"):
                with st.spinner("🔍 Creating quiz..."):
                    result = ask_medai(
                        f"""Create a {num_quiz} question quiz about {learn_topic}.

Mix question types:
- Label the diagram questions (describe a blank diagram, ask to label parts)
- Function questions (what does X do?)
- Process questions (what happens when?)
- Clinical questions (patient has symptom X — which part is affected?)

Format:
Q[number]. [Question]
A) [Option] B) [Option] C) [Option] D) [Option]
✅ Answer: [Letter] — [Explanation]""",
                        system_extra="Create engaging, educational quiz questions that really test understanding, not just memorization."
                    )
                st.markdown(f"### 📝 {learn_topic} Quiz")
                st.markdown(result)
                report = generate_pdf_report(f"Quiz: {learn_topic}", result, st.session_state.current_user)
                st.download_button("📥 Download Quiz as PDF", report, "MedAI_Quiz.pdf", "application/pdf")

        elif learn_mode == "🔍 Explain this diagram part":
            part_name = st.text_input("Type the name of the part you want explained", placeholder="e.g. Mitral valve, Nephron, Alveolus, Synapse")
            if part_name and st.button("🔍 Explain This Part", type="primary", use_container_width=True, key="explain_part"):
                with st.spinner("🔍 Explaining..."):
                    result = ask_medai(
                        f"""Explain {part_name} in the context of {learn_topic}:
1. What is it? (simple definition)
2. Where is it located? (describe precisely)
3. What does it look like? (describe in detail)
4. What does it do? (function — step by step)
5. How does it connect to other parts?
6. What happens if it fails?
7. Clinical diseases related to this part
8. How to remember it (mnemonic)
9. Common exam questions about it
10. Free resource to learn more (URL)""",
                        system_extra="Explain with great clarity. Use simple language first then technical. Always provide a free resource URL."
                    )
                st.markdown(f"### 🔍 {part_name} — Complete Explanation")
                st.markdown(result)

# ── IMAGE ANALYSIS PAGE ──
elif st.session_state.page == "image":
    st.markdown('<div class="page-header"><h2>📸 Image Analysis</h2><p>Upload any medical image — body part, skin, scan, food, diagram — AI analyzes everything</p></div>', unsafe_allow_html=True)

    photo_mode = st.radio("", ["📷 Use Camera", "🖼️ Upload from Gallery"], horizontal=True, label_visibility="collapsed")

    if photo_mode == "📷 Use Camera":
        img_file = st.camera_input("Take photo", key="page_camera", label_visibility="collapsed")
    else:
        img_file = st.file_uploader("Upload image", type=["jpg","jpeg","png","webp"], key="page_img", label_visibility="collapsed")

    question = st.text_input("What do you want to know?", "Give full medical analysis of this image")

    if img_file:
        img = Image.open(img_file).convert("RGB")
        col1, col2 = st.columns(2)
        with col1: st.image(img, caption="Your image", use_container_width=True)
        with col2:
            if st.button("🔍 Analyze", use_container_width=True, type="primary"):
                with st.spinner("🔍 Analyzing..."): result = analyze_image(img, question)
                st.markdown("### 🏥 MedAI Analysis")
                st.markdown(result)
                report = generate_pdf_report("Medical Image Analysis", result, st.session_state.current_user)
                st.download_button("📥 Download Report", report, "MedAI_Image_Report.pdf", "application/pdf")

# ── PDF ANALYSIS PAGE ──
elif st.session_state.page == "pdf":
    st.markdown('<div class="page-header"><h2>📄 PDF Analysis</h2><p>Upload any medical PDF — reports, prescriptions, research papers, lab results</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload medical PDF", type=["pdf"])
    question = st.text_input("What do you want to know?", "Give complete medical analysis and summary")
    if uploaded:
        st.success(f"✅ Uploaded: {uploaded.name}")
        if st.button("🔍 Analyze PDF", use_container_width=True, type="primary"):
            with st.spinner("📄 Reading and analyzing..."):
                result = analyze_pdf(uploaded, question)
            st.markdown("### 🏥 MedAI PDF Analysis")
            st.markdown(result)
            report = generate_pdf_report(f"PDF Analysis: {uploaded.name}", result, st.session_state.current_user)
            st.download_button("📥 Download Report", report, "MedAI_PDF_Report.pdf", "application/pdf")

# ── MEDICAL SEARCH ──
elif st.session_state.page == "search":
    st.markdown('<div class="page-header"><h2>🔬 Medical Search</h2><p>Searches PubMed + WHO + Wikipedia + OpenFDA + Web automatically</p></div>', unsafe_allow_html=True)
    query = st.text_input("Search any medical topic...")
    if query and st.button("🔍 Search Everywhere", use_container_width=True, type="primary"):
        col1, col2 = st.columns([2,1])
        with col1:
            with st.spinner("Searching..."): answer = ask_medai(query)
            st.markdown("### 🤖 MedAI Answer")
            st.markdown(answer)
        with col2:
            st.markdown("### 📚 Sources")
            for s in search_everywhere(query):
                if s.get("url"):
                    st.markdown(f'<div class="source-item">🔗 <a href="{s["url"]}" target="_blank">[{s["source"]}]</a></div>', unsafe_allow_html=True)

# ── HISTORY ──
elif st.session_state.page == "history":
    st.markdown('<div class="page-header"><h2>📚 Chat History</h2><p>All your medical conversations saved automatically</p></div>', unsafe_allow_html=True)
    if not st.session_state.current_user:
        st.warning("⚠️ Please login to see history!")
        if st.button("Login", type="primary"): st.session_state.page = "login"; st.rerun()
    else:
        history = load_db(HISTORY_DB)
        user_history = history.get(st.session_state.current_user, [])
        if not user_history:
            st.info("No history yet!")
        else:
            st.success(f"Total conversations: {len(user_history)}")
            # Export all history
            all_text = "\n\n".join([f"Q: {c['question']}\nA: {c['answer']}" for c in user_history])
            report = generate_pdf_report("Complete Chat History", all_text, st.session_state.current_user)
            st.download_button("📥 Download Full History as PDF", report, "MedAI_History.pdf", "application/pdf")
            for i, chat in enumerate(reversed(user_history[-20:]), 1):
                with st.expander(f"{i}. [{chat['time']}] {chat['question'][:60]}..."):
                    st.markdown(f"**❓** {chat['question']}")
                    st.markdown(f"**🤖** {chat['answer']}")

# ── PROFILE ──
elif st.session_state.page == "profile":
    st.markdown('<div class="page-header"><h2>👤 Health Profile</h2><p>MedAI personalizes every answer based on your health profile</p></div>', unsafe_allow_html=True)
    if not st.session_state.current_user:
        st.warning("⚠️ Please login first!")
        if st.button("Login", type="primary"): st.session_state.page = "login"; st.rerun()
    else:
        users = load_db(USERS_DB)
        profile = users[st.session_state.current_user]["profile"]
        st.success(f"👤 {st.session_state.current_user}")
        col1, col2 = st.columns(2)
        for i, (k, v) in enumerate(profile.items()):
            with col1 if i % 2 == 0 else col2:
                st.metric(k.replace("_"," ").title(), v or "Not set")

# ── MEDICAL EDUCATION ──
elif st.session_state.page == "education":
    st.markdown('<div class="page-header"><h2>🎓 Medical Education</h2><p>Free medical books, study plans, resources — everything a medical student needs</p></div>', unsafe_allow_html=True)

    edu_tab1, edu_tab2, edu_tab3, edu_tab4 = st.tabs(["📚 Free Books", "📋 Study Plan", "🎯 Quick Topics", "📝 MCQ Practice"])

    with edu_tab1:
        st.markdown("### 📚 Free Medical Books — Direct Download Links")
        st.caption("All 100% free and legal — click to open or download")

        book_categories = {
            "🫀 Anatomy": [
                {"name": "Gray's Anatomy for Students", "url": "https://www.ncbi.nlm.nih.gov/books/NBK279167/", "source": "NCBI"},
                {"name": "Gray's Anatomy — Full Online", "url": "https://archive.org/details/grays-anatomy", "source": "Internet Archive"},
                {"name": "Human Anatomy — OpenStax", "url": "https://openstax.org/books/anatomy-and-physiology/pages/1-introduction", "source": "OpenStax Free"},
                {"name": "Anatomy Atlas — Visible Body", "url": "https://www.visiblebody.com/", "source": "Visible Body"},
                {"name": "NCBI Anatomy Books", "url": "https://www.ncbi.nlm.nih.gov/books/NBK493180/", "source": "NCBI"},
            ],
            "🧬 Physiology": [
                {"name": "Guyton and Hall — Physiology", "url": "https://archive.org/details/guyton-and-hall-textbook-of-medical-physiology", "source": "Internet Archive"},
                {"name": "Physiology — OpenStax Free", "url": "https://openstax.org/books/anatomy-and-physiology/pages/1-introduction", "source": "OpenStax"},
                {"name": "Physiology — LibreTexts", "url": "https://bio.libretexts.org/Bookshelves/Human_Biology", "source": "LibreTexts Free"},
                {"name": "Osmosis Physiology Videos", "url": "https://www.osmosis.org/learn/Physiology", "source": "Osmosis"},
            ],
            "💊 Pharmacology": [
                {"name": "Katzung Pharmacology — Free", "url": "https://archive.org/details/basic-clinical-pharmacology", "source": "Internet Archive"},
                {"name": "Pharmacology — NCBI Books", "url": "https://www.ncbi.nlm.nih.gov/books/NBK507808/", "source": "NCBI Free"},
                {"name": "Drug Info — OpenFDA", "url": "https://open.fda.gov/", "source": "FDA Free"},
                {"name": "PharmGKB Drug Database", "url": "https://www.pharmgkb.org/", "source": "PharmGKB Free"},
            ],
            "🦠 Pathology": [
                {"name": "Robbins Pathology — Online", "url": "https://archive.org/details/robbins-basic-pathology", "source": "Internet Archive"},
                {"name": "Pathology — NCBI Books", "url": "https://www.ncbi.nlm.nih.gov/books/NBK507839/", "source": "NCBI Free"},
                {"name": "PathAI Learning Resources", "url": "https://www.pathai.com/resources/", "source": "PathAI"},
            ],
            "🩺 Clinical Medicine": [
                {"name": "Harrison's Internal Medicine — Chapters", "url": "https://www.ncbi.nlm.nih.gov/books/", "source": "NCBI"},
                {"name": "MedlinePlus Medical Encyclopedia", "url": "https://medlineplus.gov/encyclopedia.html", "source": "NIH Free"},
                {"name": "WHO Clinical Guidelines", "url": "https://www.who.int/publications/guidelines", "source": "WHO Free"},
                {"name": "CDC Clinical Resources", "url": "https://www.cdc.gov/", "source": "CDC Free"},
                {"name": "UpToDate Free Topics", "url": "https://www.uptodate.com/contents/table-of-contents/", "source": "UpToDate"},
            ],
            "🧠 Neurology": [
                {"name": "Neurology — NCBI Books", "url": "https://www.ncbi.nlm.nih.gov/books/NBK396/", "source": "NCBI Free"},
                {"name": "Brain Facts Book — Free", "url": "https://www.brainfacts.org/the-brain-facts-book", "source": "Brain Facts"},
                {"name": "Khan Academy Neuroscience", "url": "https://www.khanacademy.org/science/biology/human-biology/neuron-nervous-system", "source": "Khan Academy"},
            ],
            "👶 Pediatrics": [
                {"name": "Nelson Textbook — NCBI", "url": "https://www.ncbi.nlm.nih.gov/books/NBK470544/", "source": "NCBI"},
                {"name": "WHO Child Health Guidelines", "url": "https://www.who.int/health-topics/child-health", "source": "WHO Free"},
                {"name": "AAP Pediatric Resources", "url": "https://www.aap.org/en/patient-care/", "source": "AAP"},
            ],
            "🔬 Research Papers": [
                {"name": "PubMed — 36M Free Papers", "url": "https://pubmed.ncbi.nlm.nih.gov/", "source": "PubMed"},
                {"name": "PubMed Central — Full PDFs", "url": "https://www.ncbi.nlm.nih.gov/pmc/", "source": "PMC Free"},
                {"name": "Europe PMC — Free Papers", "url": "https://europepmc.org/", "source": "Europe PMC"},
                {"name": "bioRxiv — Latest Research", "url": "https://www.biorxiv.org/", "source": "bioRxiv"},
                {"name": "PLOS Medicine — Open Access", "url": "https://journals.plos.org/plosmedicine/", "source": "PLOS Free"},
                {"name": "Cochrane Reviews Free", "url": "https://www.cochranelibrary.com/", "source": "Cochrane"},
            ],
        }

        for category, books in book_categories.items():
            st.markdown(f"#### {category}")
            for book in books:
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"📖 **{book['name']}** — *{book['source']}*")
                with col2:
                    st.markdown(f"[🔗 Open Free]({book['url']})")
            st.markdown("---")

        # AI book recommendation
        st.divider()
        st.markdown("#### 🔍 Search & Read Medical Content Instantly")
        st.caption("MedAI fetches real content from free medical databases and gives you complete notes")

        book_query = st.text_input("What medical topic do you need?", placeholder="e.g. heart attack, pharmacology of aspirin, anatomy of kidney")

        if book_query and st.button("🔍 Find + Explain Instantly", type="primary", use_container_width=True, key="find_books"):
            with st.spinner("🔍 Searching medical databases and creating notes..."):
                fetched = []
                try:
                    r = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(book_query)}&retmax=3&format=json", timeout=8)
                    ids = r.json()["esearchresult"]["idlist"]
                    for pmid in ids[:3]:
                        fetched.append(f"PubMed paper: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
                except: pass
                try:
                    r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(book_query)}", timeout=8)
                    if r.status_code == 200:
                        d = r.json()
                        fetched.append(f"Wikipedia — {d.get('title','')} — {d.get('content_urls',{}).get('desktop',{}).get('page','')}")
                except: pass
                try:
                    r = requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(book_query)}&format=json&pageSize=3", timeout=8)
                    for p in r.json().get("resultList",{}).get("result",[])[:3]:
                        fetched.append(f"Europe PMC — {p.get('title','')} — https://europepmc.org/article/{p.get('source','')}/{p.get('id','')}")
                except: pass

                result = ask_medai(
                    f"""Topic: {book_query}

Real sources found: {chr(10).join(fetched)}

Provide COMPLETE notes:
1. Full explanation — step by step
2. Key concepts with definitions
3. Clinical relevance
4. What research says
5. Direct free book links:
   - https://archive.org/search?query={urllib.parse.quote(book_query)}+medical+textbook
   - https://www.ncbi.nlm.nih.gov/books/
   - https://openstax.org/subjects/science
   - https://bio.libretexts.org/
6. Free YouTube channels for this topic
7. 5 practice exam questions with answers""",
                    system_extra="Give complete detailed notes. Always include direct clickable URLs. Never say cannot provide. Be the best medical tutor."
                )

            if fetched:
                st.markdown("#### 📚 Sources Found:")
                for s in fetched:
                    parts = s.split(" — ")
                    if len(parts) >= 2:
                        st.markdown(f"🔗 [{parts[0]}]({parts[-1]})")

            st.markdown("#### 📖 Complete Notes:")
            st.markdown(result)
            report = generate_pdf_report(f"Medical Notes: {book_query}", result, st.session_state.current_user)
            st.download_button("📥 Download as PDF Notes", report, f"MedAI_Notes.pdf", "application/pdf")

    with edu_tab2:
        st.markdown("### 📋 Personalized Study Plan Generator")

        level = st.selectbox("Your level", ["1st Year MBBS", "2nd Year MBBS", "3rd Year MBBS", "4th Year MBBS", "Final Year MBBS", "Postgraduate / MD", "Nursing Student", "Pharmacy Student", "Self Learning"])
        subject = st.selectbox("Subject / Topic", ["All Subjects", "Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", "Microbiology", "Medicine", "Surgery", "Pediatrics", "Obstetrics & Gynecology", "ENT", "Ophthalmology", "Psychiatry", "Orthopedics"])
        duration = st.selectbox("Study duration", ["1 week", "2 weeks", "1 month", "3 months", "6 months", "1 year"])
        exam = st.text_input("Exam you are preparing for", placeholder="e.g. USMLE Step 1, NEET PG, MBBS finals")
        hours = st.slider("Hours per day available", 1, 12, 4)

        if st.button("📋 Generate My Study Plan", type="primary", use_container_width=True, key="gen_plan"):
            with st.spinner("🔍 Creating your personalized study plan..."):
                result = ask_medai(
                    f"""Create a detailed study plan:
Level: {level}
Subject: {subject}
Duration: {duration}
Exam: {exam or 'General preparation'}
Hours per day: {hours}

Provide:
1. Week by week schedule with specific topics
2. Free books and resources for each topic (with URLs)
3. Daily study routine
4. Important topics to focus on
5. Practice MCQ sources (free)
6. Revision strategy
7. Exam tips""",
                    system_extra="You are an expert medical educator. Always provide specific free resource URLs. Create detailed actionable plans."
                )
            st.markdown("### 📋 Your Personalized Study Plan")
            st.markdown(result)
            report = generate_pdf_report("Medical Study Plan", result, st.session_state.current_user)
            st.download_button("📥 Download Study Plan as PDF", report, "MedAI_Study_Plan.pdf", "application/pdf")

    with edu_tab3:
        st.markdown("### 🎯 Quick Topic Explainer")
        st.caption("Type any medical topic — MedAI explains it simply with diagrams and examples")

        topic = st.text_input("Medical topic to learn", placeholder="e.g. How does the heart work, What is diabetes, Explain DNA replication")
        explain_level = st.selectbox("Explain at level", ["Simple — for patient", "Intermediate — for student", "Advanced — for doctor/researcher"])

        if topic and st.button("🎓 Explain This Topic", type="primary", use_container_width=True, key="explain_topic"):
            with st.spinner("🔍 Preparing explanation..."):
                result = ask_medai(
                    f"""Explain: {topic}
Level: {explain_level}

Provide:
1. Simple explanation first
2. Detailed explanation
3. Key points to remember
4. Common exam questions on this topic
5. Free resources to learn more (with URLs)
6. Common mistakes students make
7. Clinical relevance""",
                    system_extra="You are an expert medical teacher. Explain clearly with examples. Always provide free learning resource URLs."
                )
            st.markdown(f"### 🎓 {topic}")
            st.markdown(result)
            report = generate_pdf_report(f"Topic Notes: {topic}", result, st.session_state.current_user)
            st.download_button("📥 Download Notes as PDF", report, "MedAI_Notes.pdf", "application/pdf")

        st.divider()
        st.markdown("#### Popular Topics:")
        popular = [
            "How does the heart pump blood?",
            "Explain diabetes mellitus",
            "What is the immune system?",
            "How do antibiotics work?",
            "Explain kidney function",
            "What causes cancer?",
            "How does the brain work?",
            "Explain blood pressure",
        ]
        cols = st.columns(2)
        for i, t in enumerate(popular):
            with cols[i % 2]:
                if st.button(t, key=f"pop_{i}", use_container_width=True):
                    st.session_state.auto_question = t
                    st.session_state.page = "chat"
                    st.rerun()

    with edu_tab4:
        st.markdown("### 📝 Practice Exams & Mock Tests")
        st.caption("Real exam-style questions · Past paper analysis · Mock tests · Performance tracking")

        exam_mode = st.radio("", ["📝 MCQ Practice", "📊 Mock Exam", "🔍 Topic Deep Dive", "📈 Analyze My Weak Areas"], horizontal=True, label_visibility="collapsed")

        if exam_mode == "📝 MCQ Practice":
            mcq_subject = st.selectbox("Subject", ["Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", "Microbiology", "Medicine", "Surgery", "Pediatrics", "Gynecology", "ENT", "Ophthalmology", "All subjects"], key="mcq_sub")
            mcq_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed — like real exam"], key="mcq_diff")
            mcq_count = st.slider("Number of questions", 5, 30, 10, key="mcq_count")
            exam_type = st.selectbox("Exam pattern", ["USMLE Step 1", "USMLE Step 2", "NEET PG", "MBBS University Exam", "PLAB UK", "AMC Australia", "General Practice"])

            if st.button("📝 Start Practice", type="primary", use_container_width=True, key="gen_mcq"):
                with st.spinner("🔍 Generating exam-style questions..."):
                    result = ask_medai(
                        f"""Generate {mcq_count} MCQ questions for {mcq_subject} at {mcq_difficulty} difficulty in {exam_type} style.

For EACH question provide:
Q[number]. [Clinical scenario or direct question — make it realistic]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
✅ Correct Answer: [Letter]
📖 Explanation: [Detailed explanation of why correct and why others are wrong]
🔗 Study more: [Free resource URL]

Make questions based on real {exam_type} past paper patterns. Include clinical vignettes.""",
                        system_extra=f"You are an expert {exam_type} examiner. Generate high quality questions exactly like real {exam_type} exams. Always include clinical context. Always explain why wrong options are wrong."
                    )
                st.markdown(f"### 📝 {mcq_subject} — {exam_type} Style Questions")
                st.markdown(result)
                report = generate_pdf_report(f"Practice MCQ: {mcq_subject} — {exam_type}", result, st.session_state.current_user)
                st.download_button("📥 Download Questions as PDF", report, "MedAI_MCQ.pdf", "application/pdf")

        elif exam_mode == "📊 Mock Exam":
            st.markdown("#### 📊 Full Mock Exam")
            mock_exam = st.selectbox("Select exam", ["USMLE Step 1", "USMLE Step 2 CK", "NEET PG", "MBBS Final Year", "PLAB Part 1", "AMC Part 1"])
            mock_duration = st.selectbox("Questions", ["20 questions", "50 questions", "100 questions"])
            mock_time = st.selectbox("Time limit", ["30 minutes", "1 hour", "2 hours", "3 hours"])
            num_q = int(mock_duration.split()[0])

            if st.button("🚀 Start Mock Exam", type="primary", use_container_width=True, key="start_mock"):
                with st.spinner(f"🔍 Creating {num_q} question mock exam..."):
                    result = ask_medai(
                        f"""Create a full {num_q} question mock exam for {mock_exam}.

Mix topics: Anatomy, Physiology, Pathology, Pharmacology, Medicine, Surgery, Pediatrics.
Include: Basic sciences + Clinical medicine + Recent advances.

For EACH question:
Q[number]. [Clinical vignette or question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]

After ALL questions, provide ANSWER KEY:
Answer Key:
Q1: [Letter] — [One line reason]
Q2: [Letter] — [One line reason]
...(continue)

Then provide DETAILED EXPLANATIONS for each answer.""",
                        system_extra=f"You are the official {mock_exam} exam board. Create exactly the style, difficulty and format of real {mock_exam} exams. Mix all medical subjects."
                    )
                st.markdown(f"### 📊 {mock_exam} Mock Exam — {mock_duration}")
                st.info(f"⏱️ Suggested time: {mock_time} — Read each question carefully!")
                st.markdown(result)
                report = generate_pdf_report(f"Mock Exam: {mock_exam}", result, st.session_state.current_user)
                st.download_button("📥 Download Full Mock Exam as PDF", report, "MedAI_Mock_Exam.pdf", "application/pdf")

        elif exam_mode == "🔍 Topic Deep Dive":
            st.markdown("#### 🔍 Master Any Topic Completely")
            topic_input = st.text_input("Enter any medical topic", placeholder="e.g. Myocardial infarction, Diabetes management, Antibiotic mechanisms")
            student_level = st.selectbox("Your level", ["1st Year MBBS", "2nd Year", "3rd Year", "Final Year", "Postgraduate", "Self Learning"])

            if topic_input and st.button("🎓 Master This Topic", type="primary", use_container_width=True, key="deep_dive"):
                with st.spinner(f"🔍 Creating complete guide for {topic_input}..."):
                    result = ask_medai(
                        f"""Create a COMPLETE mastery guide for: {topic_input}
Student level: {student_level}

Provide ALL of the following:

## 1. BASIC CONCEPT
- Simple explanation (3-4 lines)
- Key definition

## 2. DETAILED EXPLANATION
- Full pathophysiology / mechanism
- Step by step process
- Diagrams described in text

## 3. KEY FACTS TO REMEMBER
- Bullet points of most important facts
- Mnemonics if available
- Numbers and values to memorize

## 4. CLINICAL PRESENTATION
- Signs and symptoms
- How it presents in real patients
- Clinical vignette example

## 5. DIAGNOSIS
- Tests and investigations
- What values indicate what
- Diagnostic criteria

## 6. TREATMENT
- Step by step management
- First line, second line drugs
- Doses if important

## 7. COMPLICATIONS
- What can go wrong
- How to prevent

## 8. EXAM TIPS
- Most commonly asked questions on this topic
- Common traps in MCQs
- High yield points

## 9. PRACTICE QUESTIONS
- 5 MCQs on this topic with answers

## 10. FREE RESOURCES
- Direct links to free books, videos, articles on this topic""",
                        system_extra="You are the world's best medical educator. Cover every angle of this topic. Be thorough, clear, and exam-focused. Always provide free resource URLs."
                    )
                st.markdown(f"### 🎓 Complete Guide: {topic_input}")
                st.markdown(result)
                report = generate_pdf_report(f"Complete Guide: {topic_input}", result, st.session_state.current_user)
                st.download_button("📥 Download Complete Notes as PDF", report, f"MedAI_{topic_input[:20]}_Notes.pdf", "application/pdf")

        elif exam_mode == "📈 Analyze My Weak Areas":
            st.markdown("#### 📈 Weak Area Analyzer")
            st.caption("Tell MedAI your weak areas — it creates a targeted improvement plan")

            weak_subjects = st.multiselect("Select your weak subjects", ["Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", "Microbiology", "Medicine", "Surgery", "Pediatrics", "Gynecology", "ENT", "Ophthalmology"])
            weak_topics = st.text_area("Specific topics you struggle with", placeholder="e.g. Heart murmurs, Drug calculations, Hormones, Cranial nerves...")
            exam_target = st.text_input("Exam you are targeting", placeholder="e.g. USMLE Step 1 in 3 months")
            score_goal = st.text_input("Your target score", placeholder="e.g. 240, 60%, Pass")

            if weak_subjects and st.button("📈 Create Improvement Plan", type="primary", use_container_width=True, key="weak_plan"):
                with st.spinner("🔍 Analyzing and creating your plan..."):
                    result = ask_medai(
                        f"""Analyze weak areas and create improvement plan:
Weak subjects: {', '.join(weak_subjects)}
Specific struggles: {weak_topics or 'General weakness'}
Target exam: {exam_target or 'Medical exam'}
Target score: {score_goal or 'Pass'}

Provide:
1. WHY these topics are difficult (common reasons)
2. TARGETED study strategy for each weak area
3. Day by day improvement schedule
4. Best free resources for each weak topic (with URLs)
5. Practice questions focusing on weak areas
6. Memory tricks and mnemonics
7. Common mistakes to avoid
8. How to track improvement
9. Realistic timeline to master each topic
10. Prediction of likely exam questions from these topics""",
                        system_extra="You are an expert medical tutor specializing in helping struggling students. Be encouraging and practical. Always provide free resource URLs."
                    )
                st.markdown("### 📈 Your Personalized Improvement Plan")
                st.markdown(result)
                report = generate_pdf_report("Weak Area Improvement Plan", result, st.session_state.current_user)
                st.download_button("📥 Download Improvement Plan", report, "MedAI_Improvement_Plan.pdf", "application/pdf")

# ── LOGIN ──
elif st.session_state.page == "login":
    st.markdown('<div class="page-header"><h2>🔐 Login / Register</h2><p>Create account to save history, set reminders and track health</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑  Login", "📋  Create Account"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True, type="primary"):
            users = load_db(USERS_DB)
            if username in users and bcrypt.checkpw(password.encode(), users[username]["password"].encode()):
                st.session_state.current_user = username
                st.success(f"✅ Welcome back!")
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.error("❌ Wrong username or password!")

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        st.divider()
        st.caption("Health Profile — optional — helps MedAI personalize answers")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.text_input("Age")
            gender = st.selectbox("Gender", ["","Male","Female","Other"])
            blood = st.selectbox("Blood Group", ["","A+","A-","B+","B-","O+","O-","AB+","AB-"])
            weight = st.text_input("Weight (kg)")
        with col2:
            height = st.text_input("Height (cm)")
            conditions = st.text_input("Existing Conditions")
            allergies = st.text_input("Allergies")
            medicines = st.text_input("Current Medicines")

        if st.button("Create Account", use_container_width=True, type="primary"):
            users = load_db(USERS_DB)
            if new_user in users:
                st.error("❌ Username already exists!")
            elif not new_user or not new_pass:
                st.error("❌ Username and password required!")
            else:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                users[new_user] = {
                    "password": hashed,
                    "profile": {"name": name, "age": age, "gender": gender,
                                "blood_group": blood, "weight": weight, "height": height,
                                "conditions": conditions, "allergies": allergies, "medicines": medicines},
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_db(USERS_DB, users)
                st.session_state.current_user = new_user
                st.success(f"✅ Welcome {name or new_user}!")
                st.session_state.page = "chat"
                st.rerun()
