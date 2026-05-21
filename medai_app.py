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

# ── Page Config ──
st.set_page_config(
    page_title="MedAI — Medical Super Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Groq Client — reads from Streamlit secrets ──
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
except:
    GROQ_KEY = os.environ.get("GROQ_KEY", "")

if not GROQ_KEY:
    st.error("⚠️ Groq API key not found! Add it to Streamlit secrets as GROQ_KEY")
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
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "auto_question" not in st.session_state:
    st.session_state.auto_question = ""

# ── Search everywhere ──
def search_everywhere(query):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmax=3&format=json", timeout=8)
        ids = r.json()["esearchresult"]["idlist"]
        for pmid in ids[:3]:
            results.append({"source": "PubMed", "title": f"PubMed paper {pmid}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
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

# ── AI Answer ──
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
                system_prompt += f"\n\nPatient profile: {profile_text}\nPersonalize answer based on this profile."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        max_tokens=4096,
        temperature=0.7
    )
    return response.choices[0].message.content

# ── Image Analysis ──
def analyze_image(img, question):
    buffer = BytesIO()
    img.thumbnail((800, 800))
    img.save(buffer, format="JPEG", quality=85)
    img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}},
                {"type": "text", "text": f"""You are MedAI — Medical Super Intelligence.
Analyze this image as a medical expert.
Question: {question}
Provide:
1. What you see — describe everything visible
2. Medical analysis — conditions, symptoms, concerns
3. Body part or area identified
4. Normal vs abnormal findings
5. Possible conditions if anything concerning
6. Recommended next steps
7. When to see a doctor
Always remind to consult a real doctor."""}
            ]
        }],
        max_tokens=2048
    )
    return response.choices[0].message.content

# ── PDF Analysis ──
def analyze_pdf(pdf_file, question):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    total = len(reader.pages)
    for page in reader.pages:
        text += page.extract_text() or ""
    if len(text) > 8000:
        text = text[:8000]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are MedAI — expert at analyzing medical documents.
Give complete analysis, explain medical terms in simple language,
highlight important values, flag anything concerning, suggest next steps."""},
            {"role": "user", "content": f"Question: {question}\n\nDocument ({total} pages):\n{text}"}
        ],
        max_tokens=4096
    )
    return response.choices[0].message.content

# ── Save history ──
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
    st.markdown("## 🏥 MedAI")
    st.caption("Medical Super Intelligence")
    st.divider()

    if st.session_state.current_user:
        st.success(f"👤 {st.session_state.current_user}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()
    else:
        st.info("👤 Guest Mode")
        if st.button("🔐 Login / Register", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    st.divider()
    st.subheader("📋 Navigation")
    pages = [
        ("💬", "Chat", "chat"),
        ("📸", "Image Analysis", "image"),
        ("📄", "PDF Analysis", "pdf"),
        ("🔍", "Search", "search"),
        ("📚", "History", "history"),
        ("👤", "My Profile", "profile"),
    ]
    for icon, label, page_id in pages:
        if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_id}"):
            st.session_state.page = page_id
            st.rerun()

    st.divider()
    st.caption("💡 Quick Questions")
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

# ══════════════════════════════
# MAIN PAGES
# ══════════════════════════════

# ── CHAT PAGE ──
if st.session_state.page == "chat":
    st.title("🏥 MedAI — Medical Super Intelligence")
    st.caption("Ask ANYTHING medical — no limits — searches entire internet automatically")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle auto question from sidebar
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

    if question := st.chat_input("Ask any medical question in ANY language..."):
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
                    st.write(f"🔗 [{s['source']}]({s['url']})")

# ── IMAGE PAGE ──
elif st.session_state.page == "image":
    st.title("📸 MedAI Image Analysis")
    st.caption("Upload any medical image — body part, skin, scan, food, diagram — AI analyzes everything")

    uploaded = st.file_uploader("Upload medical image", type=["jpg","jpeg","png","webp"])
    question = st.text_input("What do you want to know?", "Give full medical analysis of this image")

    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Uploaded Image", use_container_width=True)
        with col2:
            if st.button("🔍 Analyze Image", use_container_width=True):
                with st.spinner("🔍 MedAI analyzing image..."):
                    result = analyze_image(img, question)
                st.markdown("### 🏥 MedAI Analysis:")
                st.markdown(result)

# ── PDF PAGE ──
elif st.session_state.page == "pdf":
    st.title("📄 MedAI PDF Analysis")
    st.caption("Upload any medical PDF — reports, prescriptions, research papers — AI reads everything")

    uploaded = st.file_uploader("Upload medical PDF", type=["pdf"])
    question = st.text_input("What do you want to know?", "Give complete medical analysis and summary")

    if uploaded:
        st.success(f"✅ PDF uploaded: {uploaded.name}")
        if st.button("🔍 Analyze PDF", use_container_width=True):
            with st.spinner("📄 Reading and analyzing PDF..."):
                result = analyze_pdf(uploaded, question)
            st.markdown("### 🏥 MedAI PDF Analysis:")
            st.markdown(result)

# ── SEARCH PAGE ──
elif st.session_state.page == "search":
    st.title("🔍 MedAI Medical Search")
    st.caption("Searches PubMed + Wikipedia + OpenFDA + Europe PMC + Web — everything automatically")

    query = st.text_input("Search any medical topic...")

    if query:
        if st.button("🔍 Search Everywhere", use_container_width=True):
            col1, col2 = st.columns([2,1])
            with col1:
                with st.spinner("Searching everywhere..."):
                    answer = ask_medai(query)
                st.markdown("### 🤖 MedAI Answer:")
                st.markdown(answer)
            with col2:
                st.markdown("### 📚 Sources Found:")
                sources = search_everywhere(query)
                for s in sources:
                    if s.get("url"):
                        st.write(f"🔗 [{s['source']}]({s['url']})")

# ── HISTORY PAGE ──
elif st.session_state.page == "history":
    st.title("📚 Chat History")
    if not st.session_state.current_user:
        st.warning("⚠️ Please login to see your history!")
        if st.button("Go to Login"):
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
                    st.write(f"**❓ Question:** {chat['question']}")
                    st.write(f"**🤖 Answer:** {chat['answer']}")

# ── PROFILE PAGE ──
elif st.session_state.page == "profile":
    st.title("👤 My Health Profile")
    if not st.session_state.current_user:
        st.warning("⚠️ Please login first!")
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()
    else:
        users = load_db(USERS_DB)
        profile = users[st.session_state.current_user]["profile"]
        st.success(f"👤 {st.session_state.current_user}")
        col1, col2 = st.columns(2)
        fields = list(profile.items())
        for i, (k, v) in enumerate(fields):
            with col1 if i % 2 == 0 else col2:
                st.metric(k.replace("_"," ").title(), v or "Not set")

# ── LOGIN PAGE ──
elif st.session_state.page == "login":
    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["🔑 Login", "📋 Create Account"])

    with tab1:
        st.subheader("Welcome back!")
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
        st.subheader("Create your MedAI account")
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        st.divider()
        st.caption("Health Profile — helps MedAI personalize answers (all optional)")
        col1, col2 = st.columns(2)
        with col1:
            name       = st.text_input("Full Name")
            age        = st.text_input("Age")
            gender     = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            blood      = st.selectbox("Blood Group", ["", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            weight     = st.text_input("Weight (kg)")
        with col2:
            height     = st.text_input("Height (cm)")
            conditions = st.text_input("Existing Conditions (e.g. diabetes, BP)")
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
                    "profile": {
                        "name": name, "age": age, "gender": gender,
                        "blood_group": blood, "weight": weight, "height": height,
                        "conditions": conditions, "allergies": allergies,
                        "medicines": medicines
                    },
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_db(USERS_DB, users)
                st.session_state.current_user = new_user
                st.success(f"✅ Account created! Welcome {name or new_user}!")
                st.session_state.page = "chat"
                st.rerun()
