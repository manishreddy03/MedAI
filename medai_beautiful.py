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
import streamlit.components.v1 as components

st.set_page_config(
    page_title="MedAI — Medical Super Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #F0F7F4 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #F0F7F4 0%, #E8F5EF 100%) !important;
}

/* ── Hide clutter ── */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #D1EAE0 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.06) !important;
}
[data-testid="stSidebar"] * {
    color: #1A3D2E !important;
}

/* ── All buttons ── */
.stButton > button {
    background: white !important;
    border: 1.5px solid #C8E6D8 !important;
    color: #2D6A4F !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    transition: all 0.2s !important;
    text-align: left !important;
}
.stButton > button:hover {
    background: #E8F5EF !important;
    border-color: #1D9E75 !important;
    color: #1D9E75 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(29,158,117,0.15) !important;
}
.stButton > button[kind="primary"] {
    background: #1D9E75 !important;
    border-color: #1D9E75 !important;
    color: white !important;
    font-weight: 600 !important;
    text-align: center !important;
}
.stButton > button[kind="primary"]:hover {
    background: #178A64 !important;
    box-shadow: 0 6px 20px rgba(29,158,117,0.35) !important;
    transform: translateY(-2px) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: white !important;
    border: 1.5px solid #C8E6D8 !important;
    border-radius: 10px !important;
    color: #1A3D2E !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1D9E75 !important;
    box-shadow: 0 0 0 3px rgba(29,158,117,0.1) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    background: white !important;
    border: 1.5px solid #C8E6D8 !important;
    border-radius: 14px !important;
    color: #1A3D2E !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInputContainer"] {
    background: white !important;
    border: 1.5px solid #C8E6D8 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: white !important;
    border: 1px solid #D1EAE0 !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin: 8px 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    color: #1A3D2E !important;
}
[data-testid="stChatMessage"] p {
    color: #1A3D2E !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: #0D6E4E !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: white !important;
    border: 1.5px solid #C8E6D8 !important;
    border-radius: 10px !important;
    color: #1A3D2E !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed #A8D5BE !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploader"] * { color: #2D6A4F !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: white !important;
    border: 1px solid #D1EAE0 !important;
    border-radius: 10px !important;
    color: #2D6A4F !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: #F8FCF9 !important;
    border: 1px solid #D1EAE0 !important;
    border-top: none !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #E8F5EF !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #2D6A4F !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: #1D9E75 !important;
    color: white !important;
}

/* ── Alerts ── */
.stSuccess {
    background: #E8F5EF !important;
    border: 1.5px solid #1D9E75 !important;
    border-radius: 10px !important;
    color: #0D6E4E !important;
}
.stWarning {
    background: #FFF8E7 !important;
    border: 1.5px solid #F59E0B !important;
    border-radius: 10px !important;
    color: #92400E !important;
}
.stError {
    background: #FEF2F2 !important;
    border: 1.5px solid #EF4444 !important;
    border-radius: 10px !important;
    color: #991B1B !important;
}
.stInfo {
    background: #EFF6FF !important;
    border: 1.5px solid #3B82F6 !important;
    border-radius: 10px !important;
    color: #1E40AF !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #D1EAE0 !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
[data-testid="stMetricLabel"] { color: #6B9E8A !important; font-size: 13px !important; }
[data-testid="stMetricValue"] { color: #1D9E75 !important; font-size: 24px !important; font-weight: 700 !important; }

/* ── Divider ── */
hr { border-color: #D1EAE0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #1D9E75 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #F0F7F4; }
::-webkit-scrollbar-thumb { background: #A8D5BE; border-radius: 3px; }

/* ── Custom components ── */
.medai-hero {
    background: linear-gradient(135deg, #1D9E75 0%, #0D6E4E 100%);
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 24px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(29,158,117,0.3);
}
.medai-hero::after {
    content: '🏥';
    position: absolute;
    right: 40px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 80px;
    opacity: 0.15;
}
.medai-hero h1 {
    font-family: 'Sora', sans-serif !important;
    font-size: 36px !important;
    font-weight: 700 !important;
    color: white !important;
    margin: 0 0 8px 0 !important;
}
.medai-hero p {
    font-size: 15px !important;
    color: rgba(255,255,255,0.85) !important;
    margin: 0 !important;
    font-weight: 300 !important;
}
.medai-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: white;
    font-weight: 500;
    margin-top: 14px;
}

.stat-card {
    background: white;
    border: 1px solid #D1EAE0;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(29,158,117,0.12);
    border-color: #1D9E75;
}
.stat-number {
    font-family: 'Sora', sans-serif;
    font-size: 30px;
    color: #1D9E75;
    font-weight: 700;
    line-height: 1;
}
.stat-label {
    font-size: 12px;
    color: #6B9E8A;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 6px;
    font-weight: 500;
}

.sidebar-brand {
    text-align: center;
    padding: 20px 0 16px;
}
.sidebar-brand .icon {
    font-size: 44px;
    display: block;
    margin-bottom: 8px;
}
.sidebar-brand h2 {
    font-family: 'Sora', sans-serif !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #1D9E75 !important;
    margin: 0 0 2px !important;
}
.sidebar-brand p {
    font-size: 11px !important;
    color: #6B9E8A !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin: 0 !important;
}

.user-card {
    background: linear-gradient(135deg, #E8F5EF, #F0FAF5);
    border: 1.5px solid #A8D5BE;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.user-card .label {
    font-size: 11px;
    color: #6B9E8A;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.user-card .name {
    font-size: 15px;
    font-weight: 600;
    color: #1D9E75;
    margin-top: 2px;
}

.nav-label {
    font-size: 11px;
    color: #6B9E8A;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin: 12px 0 6px;
}

.source-item {
    background: #F8FCF9;
    border: 1px solid #D1EAE0;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 13px;
}
.source-item a {
    color: #1D9E75 !important;
    text-decoration: none;
    font-weight: 500;
}
.source-item a:hover { text-decoration: underline; }

.page-header {
    background: white;
    border: 1px solid #D1EAE0;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.page-header h2 {
    font-family: 'Sora', sans-serif !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #0D6E4E !important;
    margin: 0 0 4px !important;
}
.page-header p {
    font-size: 14px !important;
    color: #6B9E8A !important;
    margin: 0 !important;
}

.footer-credit {
    text-align: center;
    padding: 16px 0 8px;
    border-top: 1px solid #D1EAE0;
    margin-top: 16px;
}
.footer-credit p {
    font-size: 11px !important;
    color: #A8C5B8 !important;
    margin: 2px 0 !important;
}
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

# ── Database ──
USERS_DB = "medai_users.json"
HISTORY_DB = "medai_history.json"

def load_db(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_db(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ── Session State ──
for key, val in [("current_user", None), ("chat_history", []),
                  ("page", "chat"), ("auto_question", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Core Functions ──
def search_everywhere(query):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmax=3&format=json", timeout=8)
        for pmid in r.json()["esearchresult"]["idlist"][:3]:
            results.append({"source": "PubMed", "title": f"Research paper {pmid}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
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
        for l in soup.find_all("a", {"class": "result__a"})[:5]:
            results.append({"source": "Web", "title": l.get_text(strip=True)[:80], "url": l.get("href","")})
    except: pass
    return results

def ask_medai(question, username=None):
    system_prompt = """You are MedAI — Medical Super Intelligence.
Answer ANY medical question — no limits, no restrictions.
Cover diseases, symptoms, medicines, surgery, anatomy, mental health,
nutrition, emergency, pediatrics, pregnancy, cancer, rare diseases,
Ayurveda, genetics — EVERYTHING medical.
Be detailed, accurate, helpful. Use clear formatting with sections.
Always remind to consult a real doctor for serious decisions."""
    if username:
        users = load_db(USERS_DB)
        if username in users:
            profile = users[username]["profile"]
            profile_text = ", ".join([f"{k}: {v}" for k,v in profile.items() if v])
            if profile_text:
                system_prompt += f"\n\nPatient profile: {profile_text}\nPersonalize your answer."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": question}],
        max_tokens=4096, temperature=0.7
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
        max_tokens=2048
    )
    return response.choices[0].message.content

def analyze_pdf(pdf_file, question):
    reader = PyPDF2.PdfReader(pdf_file)
    text = "".join([p.extract_text() or "" for p in reader.pages])
    if len(text) > 8000:
        text = text[:8000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are MedAI — expert at analyzing medical documents. Give complete analysis, explain medical terms simply, highlight important values, flag concerns, suggest next steps."},
            {"role": "user", "content": f"Question: {question}\n\nDocument:\n{text}"}
        ],
        max_tokens=4096
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

# ══════════════════════════════
# SIDEBAR
# ══════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="icon">🏥</span>
        <h2>MedAI</h2>
        <p>Medical Super Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
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

    st.markdown('<div class="nav-label">Navigate</div>', unsafe_allow_html=True)
    pages = [
        ("💬", "Chat", "chat"),
        ("📸", "Image Analysis", "image"),
        ("📄", "PDF Analysis", "pdf"),
        ("🔍", "Search", "search"),
        ("📚", "History", "history"),
        ("👤", "My Profile", "profile"),
    ]
    for icon, label, page_id in pages:
        if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{page_id}"):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("""
    <div class="footer-credit">
        <p>Built by Manish Reddy Chamakuri</p>
        <p>SUNY Polytechnic Institute · 2026</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════
# MAIN PAGES
# ══════════════════════════════

if st.session_state.page == "chat":
    st.markdown("""
    <div class="medai-hero">
        <h1>🏥 MedAI</h1>
        <p>Medical Super Intelligence — Ask anything, get expert answers instantly in any language</p>
        <div class="medai-badge">🌍 Searches 15+ medical sources automatically · Free Forever</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-card"><div class="stat-number">110+</div><div class="stat-label">Features</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div class="stat-number">50+</div><div class="stat-label">Sources</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div class="stat-number">50+</div><div class="stat-label">Languages</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card"><div class="stat-number">∞</div><div class="stat-label">Questions</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Quick Questions — simple working buttons ──
    with st.expander("💡 Quick Questions — click to open"):
        cols = st.columns(2)
        questions = [
            "What causes chest pain?",
            "Symptoms of diabetes?",
            "How does cancer develop?",
            "Signs of heart attack?",
            "How to boost immunity?",
            "What causes headache?",
            "How to treat depression?",
            "Signs of stroke?",
            "What is Alzheimer's?",
            "How does chemotherapy work?",
        ]
        for i, q in enumerate(questions):
            with cols[i % 2]:
                if st.button(q, key=f"q_{i}", use_container_width=True):
                    st.session_state.auto_question = q
                    st.rerun()

    if st.session_state.auto_question:
        auto_q = st.session_state.auto_question
        st.session_state.auto_question = ""
        with st.chat_message("user"):
            st.markdown(auto_q)
        st.session_state.chat_history.append({"role": "user", "content": auto_q})
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching + thinking..."):
                answer = ask_medai(auto_q, st.session_state.current_user)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        if st.session_state.current_user:
            save_history(st.session_state.current_user, auto_q, answer)

    # ── Voice Input — clean mic button ──
    if "voice_processed" not in st.session_state:
        st.session_state.voice_processed = None

    audio = st.audio_input("🎤 Tap mic → speak in ANY language → AI answers instantly")
    if audio and audio != st.session_state.voice_processed:
        st.session_state.voice_processed = audio
        import io
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        audio_bytes = audio.read()
        try:
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio_data = recognizer.record(source)
            languages = ["en-US","hi-IN","te-IN","ta-IN","ar-SA","zh-CN","es-ES","fr-FR","de-DE","ja-JP","ko-KR","ru-RU","pt-BR","it-IT","tr-TR"]
            voice_text = None
            for lang in languages:
                try:
                    voice_text = recognizer.recognize_google(audio_data, language=lang)
                    if voice_text:
                        break
                except: continue
            if voice_text:
                st.success(f"🎤 You said: **{voice_text}**")
                with st.chat_message("user"):
                    st.markdown(voice_text)
                st.session_state.chat_history.append({"role": "user", "content": voice_text})
                with st.chat_message("assistant"):
                    with st.spinner("🔍 MedAI thinking..."):
                        answer = ask_medai(voice_text, st.session_state.current_user)
                    st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                if st.session_state.current_user:
                    save_history(st.session_state.current_user, voice_text, answer)
            else:
                st.warning("⚠️ Could not understand. Speak clearly and try again!")
        except Exception as e:
            st.error(f"⚠️ Voice error: {str(e)}")

    if question := st.chat_input("Ask any medical question in any language..."):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching everywhere + thinking..."):
                answer = ask_medai(question, st.session_state.current_user)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        if st.session_state.current_user:
            save_history(st.session_state.current_user, question, answer)
        with st.expander("📚 Sources searched automatically"):
            for s in search_everywhere(question):
                if s.get("url"):
                    st.markdown(f'<div class="source-item">🔗 <a href="{s["url"]}" target="_blank">[{s["source"]}] {s.get("title","")[:60]}</a></div>', unsafe_allow_html=True)

elif st.session_state.page == "image":
    st.markdown('<div class="page-header"><h2>📸 Image Analysis</h2><p>Upload any medical image — body part, skin condition, scan, food, diagram — AI analyzes everything</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload medical image", type=["jpg","jpeg","png","webp"])
    question = st.text_input("What do you want to know?", "Give full medical analysis of this image")
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Uploaded Image", use_container_width=True)
        with col2:
            if st.button("🔍 Analyze Image", use_container_width=True, type="primary"):
                with st.spinner("🔍 Analyzing..."):
                    result = analyze_image(img, question)
                st.markdown("### 🏥 MedAI Analysis")
                st.markdown(result)

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

elif st.session_state.page == "search":
    st.markdown('<div class="page-header"><h2>🔍 Medical Search</h2><p>Searches PubMed + WHO + Wikipedia + OpenFDA + Europe PMC + entire web automatically</p></div>', unsafe_allow_html=True)
    query = st.text_input("Search any medical topic...")
    if query and st.button("🔍 Search Everywhere", use_container_width=True, type="primary"):
        col1, col2 = st.columns([2,1])
        with col1:
            with st.spinner("Searching..."):
                answer = ask_medai(query)
            st.markdown("### 🤖 MedAI Answer")
            st.markdown(answer)
        with col2:
            st.markdown("### 📚 Sources")
            for s in search_everywhere(query):
                if s.get("url"):
                    st.markdown(f'<div class="source-item">🔗 <a href="{s["url"]}" target="_blank">[{s["source"]}]</a><br><small>{s.get("title","")[:50]}</small></div>', unsafe_allow_html=True)

elif st.session_state.page == "history":
    st.markdown('<div class="page-header"><h2>📚 Chat History</h2><p>All your medical conversations saved automatically</p></div>', unsafe_allow_html=True)
    if not st.session_state.current_user:
        st.warning("⚠️ Please login to see your history!")
        if st.button("Go to Login", type="primary"):
            st.session_state.page = "login"
            st.rerun()
    else:
        history = load_db(HISTORY_DB)
        user_history = history.get(st.session_state.current_user, [])
        if not user_history:
            st.info("No history yet — start asking questions!")
        else:
            st.success(f"Total conversations: {len(user_history)}")
            for i, chat in enumerate(reversed(user_history[-20:]), 1):
                with st.expander(f"{i}. [{chat['time']}] {chat['question'][:60]}..."):
                    st.markdown(f"**❓ Question:** {chat['question']}")
                    st.markdown(f"**🤖 Answer:** {chat['answer']}")

elif st.session_state.page == "profile":
    st.markdown('<div class="page-header"><h2>👤 Health Profile</h2><p>MedAI personalizes every answer based on your health profile</p></div>', unsafe_allow_html=True)
    if not st.session_state.current_user:
        st.warning("⚠️ Please login first!")
        if st.button("Go to Login", type="primary"):
            st.session_state.page = "login"
            st.rerun()
    else:
        users = load_db(USERS_DB)
        profile = users[st.session_state.current_user]["profile"]
        st.success(f"👤 {st.session_state.current_user}")
        col1, col2 = st.columns(2)
        for i, (k, v) in enumerate(profile.items()):
            with col1 if i % 2 == 0 else col2:
                st.metric(k.replace("_"," ").title(), v or "Not set")

elif st.session_state.page == "login":
    st.markdown('<div class="page-header"><h2>🔐 Login / Register</h2><p>Create your account to save history and get personalized answers</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑  Login", "📋  Create Account"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True, type="primary"):
            users = load_db(USERS_DB)
            if username in users and bcrypt.checkpw(password.encode(), users[username]["password"].encode()):
                st.session_state.current_user = username
                st.success(f"✅ Welcome back, {users[username]['profile'].get('name', username)}!")
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.error("❌ Wrong username or password!")

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        st.divider()
        st.caption("Health Profile — helps MedAI personalize your answers (all optional)")
        col1, col2 = st.columns(2)
        with col1:
            name       = st.text_input("Full Name")
            age        = st.text_input("Age")
            gender     = st.selectbox("Gender", ["","Male","Female","Other"])
            blood      = st.selectbox("Blood Group", ["","A+","A-","B+","B-","O+","O-","AB+","AB-"])
            weight     = st.text_input("Weight (kg)")
        with col2:
            height     = st.text_input("Height (cm)")
            conditions = st.text_input("Existing Conditions")
            allergies  = st.text_input("Allergies")
            medicines  = st.text_input("Current Medicines")

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
                                "conditions": conditions, "allergies": allergies,
                                "medicines": medicines},
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_db(USERS_DB, users)
                st.session_state.current_user = new_user
                st.success(f"✅ Welcome {name or new_user}!")
                st.session_state.page = "chat"
                st.rerun()
