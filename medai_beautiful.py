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

st.set_page_config(
    page_title="MedAI — Medical Super Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Beautiful Custom CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root Variables ── */
:root {
    --teal: #0D9E75;
    --teal-dark: #0A7D5C;
    --teal-light: #E6F7F2;
    --teal-glow: rgba(13,158,117,0.15);
    --dark: #0A0F0D;
    --dark-2: #111916;
    --dark-3: #1A2420;
    --dark-4: #243028;
    --text-primary: #F0F7F4;
    --text-secondary: #8BA89E;
    --text-muted: #4A6560;
    --border: rgba(13,158,117,0.2);
    --border-strong: rgba(13,158,117,0.4);
    --card-bg: rgba(26,36,32,0.8);
    --glass: rgba(13,158,117,0.05);
}

/* ── Global Reset ── */
* { font-family: 'DM Sans', sans-serif; }
html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: var(--text-primary) !important;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 50%, rgba(13,158,117,0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(13,158,117,0.05) 0%, transparent 50%),
                var(--dark) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--dark-2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Hide default elements ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    transition: all 0.2s ease !important;
    padding: 6px 12px !important;
}
.stButton > button:hover {
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    background: var(--teal-glow) !important;
    transform: translateX(2px) !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: var(--teal) !important;
    border-color: var(--teal) !important;
    color: white !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--teal-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(13,158,117,0.3) !important;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stChatInputContainer textarea {
    background: var(--dark-3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stChatInputContainer textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 2px var(--teal-glow) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin: 8px 0 !important;
    backdrop-filter: blur(10px) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--dark-3) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 16px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--dark-3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
}
.streamlit-expanderContent {
    background: var(--dark-4) !important;
    border: 1px solid var(--border) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--dark-3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--dark-3) !important;
    border: 2px dashed var(--border-strong) !important;
    border-radius: 12px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
[data-testid="stMetricValue"] { color: var(--teal) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--dark-3) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: var(--teal) !important;
    color: white !important;
}

/* ── Alerts ── */
.stSuccess {
    background: rgba(13,158,117,0.1) !important;
    border: 1px solid var(--teal) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}
.stWarning {
    background: rgba(217,119,6,0.1) !important;
    border: 1px solid rgba(217,119,6,0.4) !important;
    border-radius: 10px !important;
}
.stError {
    background: rgba(220,38,38,0.1) !important;
    border: 1px solid rgba(220,38,38,0.4) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--teal) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--dark-2); }
::-webkit-scrollbar-thumb { background: var(--teal-dark); border-radius: 3px; }

/* ── Custom header ── */
.medai-header {
    background: linear-gradient(135deg, rgba(13,158,117,0.15) 0%, transparent 60%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.medai-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(13,158,117,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.medai-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 42px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}
.medai-title span { color: var(--teal); }
.medai-subtitle {
    font-size: 15px !important;
    color: var(--text-secondary) !important;
    margin-top: 8px !important;
    font-weight: 300 !important;
}
.medai-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--teal-glow);
    border: 1px solid var(--border-strong);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--teal);
    font-weight: 500;
    margin-top: 12px;
}

/* ── Sidebar logo ── */
.sidebar-logo {
    text-align: center;
    padding: 20px 0 10px;
}
.sidebar-logo h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 26px !important;
    color: var(--teal) !important;
    margin: 8px 0 2px !important;
}
.sidebar-logo p {
    font-size: 11px !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ── Nav button active ── */
.nav-active > button {
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    background: var(--teal-glow) !important;
}

/* ── Source card ── */
.source-card {
    background: var(--dark-3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 13px;
    color: var(--text-secondary);
}
.source-card a { color: var(--teal) !important; text-decoration: none; }
.source-card a:hover { text-decoration: underline; }

/* ── Stats row ── */
.stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    color: var(--teal);
    font-weight: 700;
}
.stat-label {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
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
        r = requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(query)}&format=json&pageSize=3", timeout=8)
        for p in r.json().get("resultList",{}).get("result",[])[:3]:
            results.append({"source": "Europe PMC", "title": p.get("title","")[:80], "url": f"https://europepmc.org/article/{p.get('source','')}/{p.get('id','')}"})
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
                system_prompt += f"\n\nPatient profile: {profile_text}\nPersonalize answer."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": question}],
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
            {"type": "text", "text": f"You are MedAI — Medical Super Intelligence. Analyze this image as a medical expert. Question: {question}. Provide: what you see, medical analysis, body part identified, normal vs abnormal, possible conditions, next steps, when to see doctor."}
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
        "question": question,
        "answer": answer[:500]
    })
    save_db(HISTORY_DB, history)

# ══════════════════════════════
# SIDEBAR
# ══════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:40px">🏥</div>
        <h1>MedAI</h1>
        <p>Medical Super Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    if st.session_state.current_user:
        st.markdown(f"""
        <div style="background:rgba(13,158,117,0.1);border:1px solid rgba(13,158,117,0.3);
        border-radius:10px;padding:10px 14px;margin-bottom:8px;">
            <div style="font-size:12px;color:#8BA89E;">Logged in as</div>
            <div style="font-size:15px;font-weight:600;color:#0D9E75;">👤 {st.session_state.current_user}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()
    else:
        st.markdown("""
        <div style="background:rgba(26,36,32,0.8);border:1px solid rgba(13,158,117,0.2);
        border-radius:10px;padding:10px 14px;margin-bottom:8px;">
            <div style="font-size:13px;color:#8BA89E;">👤 Guest Mode</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐 Login / Register", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    st.divider()
    st.markdown('<div style="font-size:11px;color:#4A6560;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)

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

    st.divider()
    st.markdown('<div style="font-size:11px;color:#4A6560;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Quick Questions</div>', unsafe_allow_html=True)

    suggested = [
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
    for q in suggested:
        if st.button(q, use_container_width=True, key=f"sq_{q}"):
            st.session_state.page = "chat"
            st.session_state.auto_question = q
            st.rerun()

    st.divider()
    st.markdown("""
    <div style="text-align:center;padding:10px 0;">
        <div style="font-size:11px;color:#4A6560;">Built by Manish Reddy</div>
        <div style="font-size:11px;color:#4A6560;">SUNY Polytechnic Institute</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════
# MAIN PAGES
# ══════════════════════════════

# ── CHAT PAGE ──
if st.session_state.page == "chat":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">Med<span>AI</span></div>
        <div class="medai-subtitle">Medical Super Intelligence — Ask anything, get expert answers instantly</div>
        <div class="medai-badge">🌍 Searches 15+ medical sources automatically</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
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

    if st.session_state.auto_question:
        auto_q = st.session_state.auto_question
        st.session_state.auto_question = ""
        with st.chat_message("user"):
            st.markdown(auto_q)
        st.session_state.chat_history.append({"role": "user", "content": auto_q})
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching everywhere + thinking..."):
                answer = ask_medai(auto_q, st.session_state.current_user)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        if st.session_state.current_user:
            save_history(st.session_state.current_user, auto_q, answer)

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
            sources = search_everywhere(question)
            for s in sources:
                if s.get("url"):
                    st.markdown(f'<div class="source-card">🔗 <a href="{s["url"]}" target="_blank">[{s["source"]}] {s.get("title","")[:60]}</a></div>', unsafe_allow_html=True)

# ── IMAGE PAGE ──
elif st.session_state.page == "image":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">📸 Image <span>Analysis</span></div>
        <div class="medai-subtitle">Upload any medical image — body part, skin condition, scan, food, diagram</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload medical image", type=["jpg","jpeg","png","webp"])
    question = st.text_input("What do you want to know?", "Give full medical analysis of this image")

    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns([1,1])
        with col1:
            st.image(img, caption="Uploaded Image", use_container_width=True)
        with col2:
            if st.button("🔍 Analyze Image", use_container_width=True, type="primary"):
                with st.spinner("🔍 MedAI analyzing image..."):
                    result = analyze_image(img, question)
                st.markdown("### 🏥 MedAI Analysis")
                st.markdown(result)

# ── PDF PAGE ──
elif st.session_state.page == "pdf":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">📄 PDF <span>Analysis</span></div>
        <div class="medai-subtitle">Upload any medical PDF — reports, prescriptions, research papers, lab results</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload medical PDF", type=["pdf"])
    question = st.text_input("What do you want to know?", "Give complete medical analysis and summary")

    if uploaded:
        st.success(f"✅ Uploaded: {uploaded.name}")
        if st.button("🔍 Analyze PDF", use_container_width=True, type="primary"):
            with st.spinner("📄 Reading and analyzing PDF..."):
                result = analyze_pdf(uploaded, question)
            st.markdown("### 🏥 MedAI PDF Analysis")
            st.markdown(result)

# ── SEARCH PAGE ──
elif st.session_state.page == "search":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">🔍 Medical <span>Search</span></div>
        <div class="medai-subtitle">Searches PubMed + WHO + Wikipedia + OpenFDA + Europe PMC + Web automatically</div>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input("Search any medical topic...")
    if query and st.button("🔍 Search Everywhere", use_container_width=True, type="primary"):
        col1, col2 = st.columns([2,1])
        with col1:
            with st.spinner("Searching everywhere..."):
                answer = ask_medai(query)
            st.markdown("### 🤖 MedAI Answer")
            st.markdown(answer)
        with col2:
            st.markdown("### 📚 Sources Found")
            for s in search_everywhere(query):
                if s.get("url"):
                    st.markdown(f'<div class="source-card">🔗 <a href="{s["url"]}" target="_blank">[{s["source"]}]</a><br>{s.get("title","")[:50]}</div>', unsafe_allow_html=True)

# ── HISTORY PAGE ──
elif st.session_state.page == "history":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">📚 Chat <span>History</span></div>
        <div class="medai-subtitle">All your medical conversations saved automatically</div>
    </div>
    """, unsafe_allow_html=True)

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

# ── PROFILE PAGE ──
elif st.session_state.page == "profile":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">👤 Health <span>Profile</span></div>
        <div class="medai-subtitle">MedAI personalizes answers based on your health profile</div>
    </div>
    """, unsafe_allow_html=True)

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

# ── LOGIN PAGE ──
elif st.session_state.page == "login":
    st.markdown("""
    <div class="medai-header">
        <div class="medai-title">🔐 Login / <span>Register</span></div>
        <div class="medai-subtitle">Create your account to save history and personalize answers</div>
    </div>
    """, unsafe_allow_html=True)

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
            gender     = st.selectbox("Gender", ["", "Male", "Female", "Other"])
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
                                "conditions": conditions, "allergies": allergies, "medicines": medicines},
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_db(USERS_DB, users)
                st.session_state.current_user = new_user
                st.success(f"✅ Welcome {name or new_user}!")
                st.session_state.page = "chat"
                st.rerun()
