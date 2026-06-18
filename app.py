import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat
from database import (
    sign_in, sign_up, sign_out,
    create_conversation, get_conversations,
    delete_conversation, update_conversation_title,
    save_message, get_messages
)

st.set_page_config(
    page_title="Albert AI",
    page_icon="⊞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
* { overscroll-behavior-y: none !important; }
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background: #0f0f0f !important;
    color: #c8c8c8 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: 15px !important;
}
[data-testid="stMain"], .block-container, [data-testid="block-container"] {
    background: #0f0f0f !important;
    padding: 0 !important;
    max-width: 100% !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── HIDE DEFAULT SIDEBAR ARROW BUTTONS ── */
/* This removes the ugly << >> double arrow toggle button */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="stBaseButton-header"] { display: none !important; }

/* ── FIX SIDEBAR NOT PEEKING ON MOBILE ── */
@media (max-width: 768px) {
    /* Completely hide sidebar on mobile — accessed via our own button */
    [data-testid="stSidebar"] {
        display: none !important;
        transform: translateX(-100%) !important;
        visibility: hidden !important;
    }
    /* When sidebar is open on mobile — show it fullscreen */
    [data-testid="stSidebar"][aria-expanded="true"] {
        display: flex !important;
        transform: translateX(0) !important;
        visibility: visible !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 80vw !important;
        max-width: 280px !important;
        height: 100vh !important;
        z-index: 9999 !important;
        box-shadow: 4px 0 20px rgba(0,0,0,0.8) !important;
    }
    /* Main content takes full width on mobile */
    [data-testid="stMain"] {
        margin-left: 0 !important;
        width: 100% !important;
    }
    .block-container,
    [data-testid="block-container"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
        width: 100% !important;
    }
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #141414 !important;
    border-right: 1px solid #1e1e1e !important;
    min-width: 220px !important;
    max-width: 250px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 20px 14px 16px !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
}
[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: #161616 !important;
    color: #777 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 10px 0 !important;
    transition: all 0.15s !important;
    text-align: left !important;
    padding-left: 12px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1a1a1a !important;
    color: #999 !important;
    border-color: #252525 !important;
}

/* ── AUTH FORM ── */
[data-testid="stTextInput"] input {
    background: #141414 !important;
    color: #d0d0d0 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #2a2a2a !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #3a3a3a !important; }
[data-testid="stTextInput"] label { color: #666 !important; font-size: 13px !important; }

/* Main form buttons */
[data-testid="stMain"] .stButton button {
    background: #f0f0f0 !important;
    color: #111 !important;
    border: none !important;
    border-radius: 9px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 0 !important;
    width: 100% !important;
    transition: background 0.15s !important;
}
[data-testid="stMain"] .stButton button:hover {
    background: #ffffff !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: #161616 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 8px !important;
    max-width: 82% !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #1a1a1a !important;
    border-color: #222 !important;
    margin-left: auto !important;
    border-radius: 12px 3px 12px 12px !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    margin-right: auto !important;
    border-radius: 3px 12px 12px 12px !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li {
    color: #c8c8c8 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessageAvatarUser"] {
    background: #222 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: #1e1e1e !important;
    border: 1px solid #252525 !important;
    border-radius: 8px !important;
}

/* ── CHAT INPUT ── */
[data-testid="stBottom"],
[data-testid="stChatInput"] {
    background: #0f0f0f !important;
    border-top: 1px solid #1a1a1a !important;
    padding: 12px 18px !important;
}
[data-testid="stChatInput"] textarea {
    background: #141414 !important;
    color: #d0d0d0 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: #f0f0f0 !important;
    padding: 12px 16px !important;
    min-height: 48px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #3a3a3a !important; }
[data-testid="stChatInput"] textarea:focus {
    border-color: #2a2a2a !important;
    box-shadow: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: #f0f0f0 !important;
    border: none !important;
    border-radius: 9px !important;
    min-width: 38px !important;
    min-height: 38px !important;
}
[data-testid="stChatInputSubmitButton"] button:hover { background: #fff !important; }
[data-testid="stChatInputSubmitButton"] svg path { stroke: #111 !important; fill: none !important; }

/* ── STATUS / ALERTS ── */
[data-testid="stStatus"], [data-testid="stStatusContainer"] {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
}
[data-testid="stStatus"] *, [data-testid="stStatusContainer"] * {
    color: #666 !important; font-size: 13px !important;
}
[data-testid="stAlert"] {
    background: #161616 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    color: #888 !important;
    font-size: 13px !important;
}

/* ── IMAGES ── */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid #1e1e1e !important;
    width: 100% !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] button {
    background: #161616 !important;
    color: #888 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #1a1a1a !important; color: #aaa !important;
}

/* ── MARKDOWN ── */
[data-testid="stMarkdownContainer"] p { color: #c8c8c8 !important; font-size: 15px !important; line-height: 1.7 !important; }
[data-testid="stMarkdownContainer"] h1 { color: #f0f0f0 !important; font-size: 20px !important; font-weight: 600 !important; }
[data-testid="stMarkdownContainer"] h2 { color: #e0e0e0 !important; font-size: 17px !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] h3 { color: #d0d0d0 !important; font-size: 15px !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] code { background: #1a1a1a !important; color: #a8a8a8 !important; border: 1px solid #222 !important; border-radius: 5px !important; padding: 2px 7px !important; font-size: 13px !important; }
[data-testid="stMarkdownContainer"] pre { background: #141414 !important; border: 1px solid #1e1e1e !important; border-radius: 10px !important; padding: 16px !important; }
[data-testid="stMarkdownContainer"] li { color: #c8c8c8 !important; font-size: 15px !important; margin-bottom: 4px !important; }
[data-testid="stMarkdownContainer"] strong { color: #e0e0e0 !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] a { color: #888 !important; text-decoration: underline; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploaderDropzone"] {
    background: #161616 !important;
    border: 1px dashed #252525 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] * { color: #444 !important; font-size: 12px !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: #1e1e1e !important;
    border: 1px solid #252525 !important;
    color: #666 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
}

/* ── RADIO (tab switcher) ── */
[data-testid="stRadio"] label { color: #666 !important; font-size: 13px !important; }
[data-testid="stRadio"] { display: none; }

/* ── MOBILE ── */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: 100% !important; max-width: 100% !important; }
    [data-testid="stChatMessage"] { max-width: 92% !important; }
    [data-testid="stChatInput"] textarea { font-size: 16px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── SETUP ────────────────────────────────────────────────────────────────────
client = setup_client()

# ── SESSION DEFAULTS ─────────────────────────────────────────────────────────
for key, val in {
    "user":            None,
    "conv_id":         None,
    "messages":        [],
    "auth_mode":       "Login",
    "uploaded_file":   None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN — shown when not logged in
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.user is None:

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;">
            <div style="width:44px;height:44px;background:#f0f0f0;border-radius:11px;
                        display:inline-flex;align-items:center;justify-content:center;
                        margin-bottom:14px;">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <rect x="2" y="2" width="7" height="7" rx="1.5" fill="#111"/>
                    <rect x="11" y="2" width="7" height="7" rx="1.5" fill="#111"/>
                    <rect x="2" y="11" width="7" height="7" rx="1.5" fill="#111"/>
                    <rect x="11" y="11" width="7" height="7" rx="1.5" fill="#111" opacity="0.3"/>
                </svg>
            </div>
            <div style="font-size:22px;font-weight:600;color:#f0f0f0;letter-spacing:-0.02em;">
                Albert AI
            </div>
            <div style="font-size:13px;color:#3a3a3a;margin-top:4px;">
                Sign in to access your chat history
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Toggle login / signup
        mode = st.session_state.auth_mode
        tab1, tab2 = st.columns(2)
        with tab1:
            if st.button("Login", use_container_width=True,
                         type="primary" if mode == "Login" else "secondary"):
                st.session_state.auth_mode = "Login"
                st.rerun()
        with tab2:
            if st.button("Sign Up", use_container_width=True,
                         type="primary" if mode == "Sign Up" else "secondary"):
                st.session_state.auth_mode = "Sign Up"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        email    = st.text_input("Email",    placeholder="you@email.com")
        password = st.text_input("Password", placeholder="••••••••", type="password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.auth_mode == "Login":
            if st.button("Login →", use_container_width=True):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Logging in..."):
                        result = sign_in(email, password)
                    if result["success"]:
                        st.session_state.user = result["user"]
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
        else:
            if st.button("Create Account →", use_container_width=True):
                if not email or not password:
                    st.error("Please enter email and password.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        result = sign_up(email, password)
                    if result["success"]:
                        st.success("✅ Account created! Please login.")
                        st.session_state.auth_mode = "Login"
                        st.rerun()
                    else:
                        st.error(f"Sign up failed: {result['error']}")

    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# MAIN APP — shown when logged in
# ════════════════════════════════════════════════════════════════════════════
user_id    = st.session_state.user.id
user_email = st.session_state.user.email


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo + user
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <div style="width:30px;height:30px;background:#f0f0f0;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <rect x="1" y="1" width="5.5" height="5.5" rx="1.2" fill="#111"/>
                <rect x="7.5" y="1" width="5.5" height="5.5" rx="1.2" fill="#111"/>
                <rect x="1" y="7.5" width="5.5" height="5.5" rx="1.2" fill="#111"/>
                <rect x="7.5" y="7.5" width="5.5" height="5.5" rx="1.2" fill="#111" opacity="0.3"/>
            </svg>
        </div>
        <span style="font-size:15px;font-weight:600;color:#f0f0f0;">Albert AI</span>
    </div>
    <div style="font-size:11px;color:#333;margin-bottom:20px;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {user_email}
    </div>
    """, unsafe_allow_html=True)

    # New chat button
    if st.button("＋  New Chat", use_container_width=True):
        st.session_state.conv_id  = None
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div style="height:1px;background:#1a1a1a;margin:12px 0;"></div>', unsafe_allow_html=True)

    # Chat history
    st.markdown('<p style="font-size:11px;color:#333;letter-spacing:0.09em;text-transform:uppercase;font-weight:500;margin-bottom:8px;">History</p>', unsafe_allow_html=True)

    conversations = get_conversations(user_id)

    if not conversations:
        st.markdown('<p style="font-size:12px;color:#2a2a2a;padding:4px 0;">No conversations yet</p>', unsafe_allow_html=True)
    else:
        for conv in conversations:
            is_active = st.session_state.conv_id == conv["id"]
            col_title, col_del = st.columns([5, 1])

            with col_title:
                label = ("▸ " if is_active else "") + conv["title"]
                if st.button(
                    label,
                    key=f"conv_{conv['id']}",
                    use_container_width=True
                ):
                    st.session_state.conv_id  = conv["id"]
                    st.session_state.messages = get_messages(conv["id"])
                    st.rerun()

            with col_del:
                if st.button("✕", key=f"del_{conv['id']}"):
                    delete_conversation(conv["id"])
                    if st.session_state.conv_id == conv["id"]:
                        st.session_state.conv_id  = None
                        st.session_state.messages = []
                    st.rerun()

    # Spacer
    st.markdown('<div style="flex:1;min-height:20px;"></div>', unsafe_allow_html=True)

    # Upload + model badge + sign out
    st.markdown('<div style="height:1px;background:#1a1a1a;margin:8px 0 12px;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:#333;letter-spacing:0.09em;text-transform:uppercase;font-weight:500;margin-bottom:8px;">Upload source</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        ext      = uploaded_file.name.split(".")[-1].upper()
        size_kb  = round(uploaded_file.size / 1024)
        size_str = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024,1)} MB"
        st.markdown(f"""
        <div style="background:#161616;border:1px solid #1e1e1e;border-radius:9px;
                    padding:10px 12px;margin-top:8px;">
            <div style="font-size:13px;font-weight:500;color:#c8c8c8;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        margin-bottom:3px;">{uploaded_file.name}</div>
            <div style="font-size:12px;color:#444;">{ext} · {size_str}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#161616;border:1px solid #1e1e1e;border-radius:9px;
                padding:10px 12px;margin-top:12px;margin-bottom:10px;">
        <div style="font-size:12px;color:#333;margin-bottom:3px;">Model</div>
        <div style="font-size:13px;font-weight:500;color:#666;">Llama 3.3 · 70B</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out", use_container_width=True):
        sign_out()
        st.session_state.user     = None
        st.session_state.conv_id  = None
        st.session_state.messages = []
        st.rerun()


# ── TOP BAR ──────────────────────────────────────────────────────────────────
conv_title = "New Chat"
if st.session_state.conv_id and conversations:
    match = next((c for c in conversations if c["id"] == st.session_state.conv_id), None)
    if match:
        conv_title = match["title"]

col_menu, col_title, col_status = st.columns([1, 6, 3])

with col_menu:
    # This button toggles the sidebar — works on both mobile and desktop
    if st.button("☰", help="Menu", use_container_width=True):
        # Toggle sidebar via Streamlit's built-in mechanism
        st.session_state["sidebar_open"] = not st.session_state.get("sidebar_open", False)

with col_title:
    st.markdown(f"""
    <div style="display:flex;align-items:center;height:42px;">
        <span style="font-size:14px;font-weight:500;color:#f0f0f0;
                     white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            {conv_title}
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:flex-end;
                gap:6px;height:42px;">
        <div style="background:#141414;border:1px solid #1e1e1e;border-radius:20px;
                    padding:5px 10px;font-size:11px;color:#555;
                    display:flex;align-items:center;gap:5px;white-space:nowrap;">
            <div style="width:5px;height:5px;border-radius:50%;
                        background:#22c55e;flex-shrink:0;"></div>
            Online
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:#1a1a1a;margin-bottom:0;"></div>',
            unsafe_allow_html=True)

# Style the hamburger button to match the dark theme
st.markdown("""
<style>
/* Hamburger menu button */
[data-testid="stMain"] > div > div > div:first-child .stButton button {
    background: transparent !important;
    border: none !important;
    color: #888 !important;
    font-size: 18px !important;
    padding: 4px 8px !important;
    border-radius: 7px !important;
    width: auto !important;
    min-width: 36px !important;
}
[data-testid="stMain"] > div > div > div:first-child .stButton button:hover {
    background: #1a1a1a !important;
    color: #f0f0f0 !important;
}
</style>
""", unsafe_allow_html=True)


# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;padding:64px 24px 40px;text-align:center;">
        <div style="font-size:20px;font-weight:500;color:#e8e8e8;
                    margin-bottom:8px;letter-spacing:-0.02em;">
            Welcome back 👋
        </div>
        <div style="font-size:14px;color:#3a3a3a;margin-bottom:30px;">
            Ask anything · Upload a document · Generate an image
        </div>
        <div style="display:flex;gap:9px;flex-wrap:wrap;justify-content:center;">
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:9px;
                        padding:11px 16px;font-size:13px;color:#555;">
                Summarise a document
            </div>
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:9px;
                        padding:11px 16px;font-size:13px;color:#555;">
                Research a topic
            </div>
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:9px;
                        padding:11px 16px;font-size:13px;color:#555;">
                Generate an image
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── RENDER MESSAGES ───────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str) and msg["content"].startswith("__IMAGE__"):
            image_url = msg["content"].replace("__IMAGE__", "")
            st.markdown(
                f'<img src="{image_url}" width="100%"'
                f' style="border-radius:12px;border:1px solid #1e1e1e;" />',
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
                f'Does this message ask to generate, draw, create, or show an image or artwork?\n'
                f'Message: "{prompt}"\n'
                f'Reply with one word only: IMAGE or TEXT'}],
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

    # Create a new conversation if none exists
    if not st.session_state.conv_id:
        title = prompt[:50]  # first 50 chars as title
        conv_id = create_conversation(user_id, title)
        st.session_state.conv_id = conv_id

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(st.session_state.conv_id, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        if is_image_request(prompt, client):
            full_response = handle_image_generation(prompt, client)
        else:
            full_response = handle_text_chat(
                prompt, client, uploaded_file, st.session_state.messages
            )

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_message(st.session_state.conv_id, "assistant", full_response)