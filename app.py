import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat
from database import (
    sign_in, sign_up, sign_out,
    create_conversation, get_conversations,
    delete_conversation,
    save_message, get_messages
)

st.set_page_config(
    page_title="Albert AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ══════════════════════════════════════
   PALETTE — Navy Blue Aesthetic
══════════════════════════════════════ */
:root {
    --bg:       #0b1120;
    --bg2:      #0f1729;
    --bg3:      #162038;
    --bg4:      #1c2a47;
    --accent:   #4d9fff;
    --accentlo: rgba(77,159,255,0.12);
    --accentbrd:rgba(77,159,255,0.25);
    --text:     #e2eaf5;
    --text2:    #a8b8d0;
    --muted:    rgba(168,184,208,0.45);
    --border:   rgba(77,159,255,0.12);
    --border2:  rgba(77,159,255,0.22);
    --white:    #ffffff;
}

/* ══════════════════════════════════════
   GLOBAL
══════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
* { overscroll-behavior-y: none !important; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: 15px !important;
}

[data-testid="stMain"],
.block-container,
[data-testid="block-container"] {
    background: var(--bg) !important;
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* ══════════════════════════════════════
   SIDEBAR NATIVE TOGGLE
══════════════════════════════════════ */
[data-testid="stSidebarCollapsedControl"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    top: 14px !important;
    left: 12px !important;
    width: 38px !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4) !important;
    z-index: 999 !important;
}
[data-testid="stSidebarCollapsedControl"]:hover {
    background: var(--bg4) !important;
    border-color: var(--accent) !important;
}
[data-testid="stSidebarCollapsedControl"] svg {
    fill: var(--text2) !important;
    width: 16px !important;
    height: 16px !important;
}

[data-testid="stSidebarCollapseButton"] {
    background: transparent !important;
    border: none !important;
    color: var(--text2) !important;
    border-radius: 8px !important;
    padding: 4px !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    background: var(--bg4) !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: var(--text2) !important;
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 240px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 18px 14px 16px !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
}
[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: var(--bg3) !important;
    color: var(--text2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 9px 12px !important;
    transition: all 0.15s !important;
    text-align: left !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: var(--bg4) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
}

/* ══════════════════════════════════════
   AUTH FORM
══════════════════════════════════════ */
[data-testid="stTextInput"] input {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.15s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(77,159,255,0.1) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--muted) !important; }
[data-testid="stTextInput"] label {
    color: var(--text2) !important;
    font-size: 13px !important;
}

.auth-btn button {
    background: var(--accent) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 12px 0 !important;
    width: 100% !important;
    transition: opacity 0.15s !important;
}
.auth-btn button:hover { opacity: 0.88 !important; }

/* ══════════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 8px !important;
    max-width: 82% !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--bg4) !important;
    border-color: var(--border2) !important;
    margin-left: auto !important;
    border-radius: 14px 3px 14px 14px !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    margin-right: auto !important;
    border-radius: 3px 14px 14px 14px !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li {
    color: var(--text) !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* Avatars */
[data-testid="stChatMessageAvatarAssistant"] {
    background: var(--accentlo) !important;
    border: 1px solid var(--accentbrd) !important;
    border-radius: 9px !important;
    color: var(--accent) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
[data-testid="stChatMessageAvatarUser"] {
    background: var(--bg4) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 9px !important;
    color: var(--text2) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════
   CHAT INPUT
══════════════════════════════════════ */
[data-testid="stBottom"],
[data-testid="stChatInput"] {
    background: var(--bg) !important;
    border-top: 1px solid var(--border) !important;
    padding: 12px 18px !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: var(--accent) !important;
    padding: 12px 16px !important;
    min-height: 48px !important;
    transition: border-color 0.15s !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(77,159,255,0.1) !important;
    outline: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 10px !important;
    min-width: 40px !important;
    min-height: 40px !important;
    transition: opacity 0.15s !important;
}
[data-testid="stChatInputSubmitButton"] button:hover { opacity: 0.85 !important; }
[data-testid="stChatInputSubmitButton"] svg path {
    stroke: #fff !important;
    fill: none !important;
}

/* ══════════════════════════════════════
   STATUS / ALERTS
══════════════════════════════════════ */
[data-testid="stStatus"],
[data-testid="stStatusContainer"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stStatus"] *,
[data-testid="stStatusContainer"] * {
    color: var(--text2) !important;
    font-size: 13px !important;
}
[data-testid="stAlert"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text2) !important;
    font-size: 13px !important;
}

/* ══════════════════════════════════════
   IMAGES & DOWNLOAD
══════════════════════════════════════ */
[data-testid="stImage"] img {
    border-radius: 14px !important;
    border: 1px solid var(--border2) !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] button {
    background: var(--bg3) !important;
    color: var(--text2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    width: 100% !important;
    padding: 9px !important;
    transition: all 0.15s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--bg4) !important;
    color: var(--text) !important;
}

/* ══════════════════════════════════════
   MARKDOWN
══════════════════════════════════════ */
[data-testid="stMarkdownContainer"] p   { color: var(--text)  !important; font-size: 15px !important; line-height: 1.7 !important; }
[data-testid="stMarkdownContainer"] h1  { color: var(--white) !important; font-size: 20px !important; font-weight: 600 !important; }
[data-testid="stMarkdownContainer"] h2  { color: var(--text)  !important; font-size: 17px !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] h3  { color: var(--text2) !important; font-size: 15px !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] li  { color: var(--text)  !important; font-size: 15px !important; margin-bottom: 4px !important; }
[data-testid="stMarkdownContainer"] strong { color: var(--white) !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] a   { color: var(--accent) !important; text-decoration: underline; text-underline-offset: 3px; }
[data-testid="stMarkdownContainer"] code {
    background: var(--bg4) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-size: 13px !important;
}
[data-testid="stMarkdownContainer"] pre {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
[data-testid="stMarkdownContainer"] pre code {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
    color: var(--text2) !important;
}

/* ══════════════════════════════════════
   FILE UPLOADER
══════════════════════════════════════ */
[data-testid="stFileUploaderDropzone"] {
    background: var(--bg3) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 10px !important;
    transition: border-color 0.15s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploaderDropzone"] * {
    color: var(--muted) !important;
    font-size: 12px !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: var(--bg4) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text2) !important;
    border-radius: 7px !important;
    font-size: 12px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button {
    background: transparent !important;
    border: none !important;
    color: var(--muted) !important;
}

/* ══════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--border2); }

/* ══════════════════════════════════════
   MOBILE
══════════════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="stChatMessage"] {
        max-width: 92% !important;
        padding: 12px 14px !important;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 16px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        font-size: 16px !important;
    }
    [data-testid="stChatInputSubmitButton"] button {
        min-width: 44px !important;
        min-height: 44px !important;
    }
    [data-testid="stSidebar"] {
        min-width: 80vw !important;
        max-width: 85vw !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        width: 44px !important;
        height: 44px !important;
        top: 10px !important;
        left: 8px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── CLIENT ────────────────────────────────────────────────────────────────────
client = setup_client()

# ── SESSION DEFAULTS ──────────────────────────────────────────────────────────
for key, val in {
    "user":     None,
    "conv_id":  None,
    "messages": [],
    "auth_mode": "Login",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-bottom:32px;">
            <div style="width:52px;height:52px;
                        background:rgba(77,159,255,0.12);
                        border:1px solid rgba(77,159,255,0.3);
                        border-radius:14px;display:inline-flex;
                        align-items:center;justify-content:center;
                        margin-bottom:16px;">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="2" width="8" height="8" rx="2" fill="#4d9fff"/>
                    <rect x="12" y="2" width="8" height="8" rx="2" fill="#4d9fff"/>
                    <rect x="2" y="12" width="8" height="8" rx="2" fill="#4d9fff"/>
                    <rect x="12" y="12" width="8" height="8" rx="2" fill="#4d9fff" opacity="0.35"/>
                </svg>
            </div>
            <div style="font-size:24px;font-weight:600;color:#e2eaf5;
                        letter-spacing:-0.02em;margin-bottom:6px;">
                Albert AI
            </div>
            <div style="font-size:13px;color:rgba(168,184,208,0.55);">
                Sign in to continue
            </div>
        </div>
        """, unsafe_allow_html=True)

        mode = st.session_state.auth_mode
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login", use_container_width=True, type="primary" if mode == "Login" else "secondary"):
                st.session_state.auth_mode = "Login"
                st.rerun()
        with c2:
            if st.button("Sign Up", use_container_width=True, type="primary" if mode == "Sign Up" else "secondary"):
                st.session_state.auth_mode = "Sign Up"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="you@email.com")
        password = st.text_input("Password", placeholder="••••••••", type="password")
        st.markdown("<br>", unsafe_allow_html=True)

        if mode == "Login":
            if st.button("Login →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Logging in..."):
                        res = sign_in(email, password)
                    if res["success"]:
                        st.session_state.user = res["user"]
                        st.rerun()
                    else:
                        st.error(f"Login failed: {res['error']}")
        else:
            if st.button("Create Account →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter email and password.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        res = sign_up(email, password)
                    if res["success"]:
                        st.success("✅ Account created! Please login.")
                        st.session_state.auth_mode = "Login"
                        st.rerun()
                    else:
                        st.error(f"Sign up failed: {res['error']}")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════
user_id = st.session_state.user.id
user_email = st.session_state.user.email


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <div style="width:32px;height:32px;
                    background:rgba(77,159,255,0.12);
                    border:1px solid rgba(77,159,255,0.28);
                    border-radius:9px;display:flex;
                    align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <rect x="1" y="1" width="5.5" height="5.5" rx="1.2" fill="#4d9fff"/>
                <rect x="8.5" y="1" width="5.5" height="5.5" rx="1.2" fill="#4d9fff"/>
                <rect x="1" y="8.5" width="5.5" height="5.5" rx="1.2" fill="#4d9fff"/>
                <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1.2" fill="#4d9fff" opacity="0.35"/>
            </svg>
        </div>
        <span style="font-size:15px;font-weight:600;color:#e2eaf5;">Albert AI</span>
    </div>
    <div style="font-size:11px;color:rgba(168,184,208,0.35);
                margin-bottom:20px;white-space:nowrap;
                overflow:hidden;text-overflow:ellipsis;">
        {user_email}
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋   New Chat", use_container_width=True):
        st.session_state.conv_id = None
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div style="height:1px;background:rgba(77,159,255,0.1);margin:12px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:rgba(168,184,208,0.4);letter-spacing:0.09em;text-transform:uppercase;font-weight:500;margin-bottom:8px;">History</p>', unsafe_allow_html=True)

    conversations = get_conversations(user_id)

    if not conversations:
        st.markdown('<p style="font-size:12px;color:rgba(168,184,208,0.25);padding:4px 0;">No conversations yet</p>', unsafe_allow_html=True)
    else:
        for conv in conversations:
            is_active = st.session_state.conv_id == conv["id"]
            c1, c2 = st.columns([5, 1])
            with c1:
                label = ("▸ " if is_active else "  ") + conv["title"]
                if st.button(label, key=f"c_{conv['id']}", use_container_width=True):
                    st.session_state.conv_id = conv["id"]
                    st.session_state.messages = get_messages(conv["id"])
                    st.rerun()
            with c2:
                if st.button("✕", key=f"d_{conv['id']}"):
                    delete_conversation(conv["id"])
                    if st.session_state.conv_id == conv["id"]:
                        st.session_state.conv_id = None
                        st.session_state.messages = []
                    st.rerun()

    st.markdown('<div style="flex:1;min-height:20px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:rgba(77,159,255,0.1);margin:10px 0 12px;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:rgba(168,184,208,0.4);letter-spacing:0.09em;text-transform:uppercase;font-weight:500;margin-bottom:8px;">Upload source</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].upper()
        size_kb = round(uploaded_file.size / 1024)
        size_str = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024,1)} MB"
        st.markdown(f"""
        <div style="background:rgba(77,159,255,0.06);
                    border:1px solid rgba(77,159,255,0.18);
                    border-radius:9px;padding:10px 12px;margin-top:8px;">
            <div style="font-size:13px;font-weight:500;color:#e2eaf5;
                        white-space:nowrap;overflow:hidden;
                        text-overflow:ellipsis;margin-bottom:2px;">
                {uploaded_file.name}
            </div>
            <div style="font-size:11px;color:rgba(168,184,208,0.45);">
                {ext} · {size_str} · Ready
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(77,159,255,0.06);
                border:1px solid rgba(77,159,255,0.12);
                border-radius:9px;padding:10px 12px;margin-top:12px;margin-bottom:10px;">
        <div style="font-size:11px;color:rgba(168,184,208,0.35);margin-bottom:2px;">Model</div>
        <div style="font-size:13px;font-weight:500;color:#a8b8d0;">Llama 3.3 · 70B</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out", use_container_width=True):
        sign_out()
        st.session_state.user = None
        st.session_state.conv_id = None
        st.session_state.messages = []
        st.rerun()


# ── TOP BAR ───────────────────────────────────────────────────────────────────
conversations = get_conversations(user_id)
conv_title = "New Chat"
if st.session_state.conv_id:
    match = next((c for c in conversations if c["id"] == st.session_state.conv_id), None)
    if match:
        conv_title = match["title"]

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:12px 24px 12px 58px;
            border-bottom:1px solid rgba(77,159,255,0.1);
            background:var(--bg);">
    <span style="font-size:14px;font-weight:500;color:#e2eaf5;
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                 max-width:60%;">
        {conv_title}
    </span>
    <div style="display:flex;align-items:center;gap:7px;flex-shrink:0;">
        <div style="background:rgba(77,159,255,0.08);
                    border:1px solid rgba(77,159,255,0.18);
                    border-radius:20px;padding:5px 12px;
                    font-size:12px;color:rgba(168,184,208,0.6);
                    display:flex;align-items:center;gap:5px;">
            <div style="width:5px;height:5px;border-radius:50%;
                        background:#22c55e;flex-shrink:0;"></div>
            Online
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;padding:64px 24px 40px;text-align:center;">
        <div style="width:56px;height:56px;
                    background:rgba(77,159,255,0.1);
                    border:1px solid rgba(77,159,255,0.25);
                    border-radius:16px;display:flex;
                    align-items:center;justify-content:center;
                    margin-bottom:20px;">
            <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <rect x="2" y="2" width="9" height="9" rx="2.5" fill="#4d9fff"/>
                <rect x="15" y="2" width="9" height="9" rx="2.5" fill="#4d9fff"/>
                <rect x="2" y="15" width="9" height="9" rx="2.5" fill="#4d9fff"/>
                <rect x="15" y="15" width="9" height="9" rx="2.5" fill="#4d9fff" opacity="0.35"/>
            </svg>
        </div>
        <div style="font-size:22px;font-weight:600;color:#e2eaf5;
                    margin-bottom:8px;letter-spacing:-0.02em;">
            How can I help you?
        </div>
        <div style="font-size:13px;color:rgba(168,184,208,0.4);
                    margin-bottom:32px;line-height:1.6;">
            Ask anything · Upload a document · Generate an image
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">
            <div style="background:rgba(77,159,255,0.07);
                        border:1px solid rgba(77,159,255,0.18);
                        border-radius:10px;padding:12px 16px;
                        font-size:13px;color:rgba(168,184,208,0.7);">
                📄 Summarise a document
            </div>
            <div style="background:rgba(77,159,255,0.07);
                        border:1px solid rgba(77,159,255,0.18);
                        border-radius:10px;padding:12px 16px;
                        font-size:13px;color:rgba(168,184,208,0.7);">
                🔍 Research a topic
            </div>
            <div style="background:rgba(77,159,255,0.07);
                        border:1px solid rgba(77,159,255,0.18);
                        border-radius:10px;padding:12px 16px;
                        font-size:13px;color:rgba(168,184,208,0.7);">
                🎨 Generate an image
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── CHAT HISTORY ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str) and msg["content"].startswith("__IMAGE__"):
            image_url = msg["content"].replace("__IMAGE__", "")
            st.markdown(
                f'<img src="{image_url}" width="100%"'
                f' style="border-radius:14px;border:1px solid rgba(77,159,255,0.2);" />',
                unsafe_allow_html=True
            )
        else:
            st.markdown(msg["content"])


# ── INTENT CLASSIFIER ─────────────────────────────────────────────────────────
def is_image_request(prompt: str, client) -> bool:
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content":
                f'Does this message ask to generate, draw, create, or show an image?\n'
                f'Message: "{prompt}"\nReply with one word only: IMAGE or TEXT'}],
            temperature=0,
            max_tokens=5
        )
        return resp.choices[0].message.content.strip().upper() == "IMAGE"
    except Exception:
        fallback = ["draw", "generate image", "create image",
                    "paint", "make an image", "show me a picture"]
        return any(t in prompt.lower() for t in fallback)


# ── CHAT INPUT ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask Albert anything..."):

    if not st.session_state.conv_id:
        conv_id = create_conversation(user_id, prompt[:50])
        st.session_state.conv_id = conv_id

    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(st.session_state.conv_id, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_image_request(prompt, client):
            full_response = handle_image_generation(prompt, client)
            # FIX: Render the real-time image response
            image_url = full_response.replace("__IMAGE__", "")
            st.markdown(
                f'<img src="{image_url}" width="100%"'
                f' style="border-radius:14px;border:1px solid rgba(77,159,255,0.2);" />',
                unsafe_allow_html=True
            )
        else:
            full_response = handle_text_chat(
                prompt, client, uploaded_file, st.session_state.messages
            )
            # FIX: Render the real-time text response
            st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_message(st.session_state.conv_id, "assistant", full_response)