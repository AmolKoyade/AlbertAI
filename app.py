import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat

st.set_page_config(
    page_title="Albert AI",
    page_icon="⊞",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ── RESET ── */
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

/* ── MAIN BLOCK ── */
[data-testid="stMain"],
.block-container,
[data-testid="block-container"] {
    background: #0f0f0f !important;
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
   SIDEBAR
══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #141414 !important;
    border-right: 1px solid #1e1e1e !important;
    min-width: 220px !important;
    max-width: 250px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 22px 16px 18px !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
}
[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar clear button */
[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: #161616 !important;
    color: #777 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 10px 0 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1a1a1a !important;
    color: #999 !important;
    border-color: #252525 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #161616 !important;
    border: 1px dashed #252525 !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #333 !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] div {
    color: #444 !important;
    font-size: 12px !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #1e1e1e !important;
    border: 1px solid #252525 !important;
    color: #666 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button {
    color: #444 !important;
    font-size: 12px !important;
    background: transparent !important;
    border: none !important;
}

/* ══════════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: #161616 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 8px !important;
    max-width: 82% !important;
}

/* User — right side */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #1a1a1a !important;
    border-color: #222 !important;
    margin-left: auto !important;
    border-radius: 12px 3px 12px 12px !important;
}

/* AI — left side */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    margin-right: auto !important;
    border-radius: 3px 12px 12px 12px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] div {
    color: #c8c8c8 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* ── AVATARS ── */
[data-testid="stChatMessageAvatarUser"] {
    background: #222 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #999 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    min-width: 30px !important;
    min-height: 30px !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: #1e1e1e !important;
    border: 1px solid #252525 !important;
    border-radius: 8px !important;
    color: #888 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    min-width: 30px !important;
    min-height: 30px !important;
}

/* ══════════════════════════════════════
   CHAT INPUT
══════════════════════════════════════ */
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
    line-height: 1.5 !important;
    resize: none !important;
    min-height: 48px !important;
    transition: border-color 0.15s !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #3a3a3a !important;
    font-size: 15px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #2a2a2a !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: #f0f0f0 !important;
    border: none !important;
    border-radius: 9px !important;
    min-width: 38px !important;
    min-height: 38px !important;
    transition: background 0.15s !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: #ffffff !important;
}
[data-testid="stChatInputSubmitButton"] svg path {
    stroke: #111 !important;
    fill: none !important;
}

/* ══════════════════════════════════════
   STATUS / ALERTS / WARNINGS
══════════════════════════════════════ */
[data-testid="stStatus"],
[data-testid="stStatusContainer"] {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
}
[data-testid="stStatus"] *,
[data-testid="stStatusContainer"] * {
    color: #666 !important;
    font-size: 13px !important;
}

[data-testid="stAlert"] {
    background: #161616 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    color: #888 !important;
    font-size: 13px !important;
}

[data-testid="stNotification"] {
    background: #161616 !important;
    border: 1px solid #1e1e1e !important;
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
    font-weight: 400 !important;
    padding: 10px 16px !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #1a1a1a !important;
    color: #aaa !important;
}

/* ══════════════════════════════════════
   MARKDOWN CONTENT
══════════════════════════════════════ */
[data-testid="stMarkdownContainer"] p {
    color: #c8c8c8 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}
[data-testid="stMarkdownContainer"] h1 {
    color: #f0f0f0 !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    margin-bottom: 10px !important;
}
[data-testid="stMarkdownContainer"] h2 {
    color: #e0e0e0 !important;
    font-size: 17px !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
}
[data-testid="stMarkdownContainer"] h3 {
    color: #d0d0d0 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}
[data-testid="stMarkdownContainer"] code {
    background: #1a1a1a !important;
    color: #a8a8a8 !important;
    border: 1px solid #222 !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-size: 13px !important;
}
[data-testid="stMarkdownContainer"] pre {
    background: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
[data-testid="stMarkdownContainer"] pre code {
    font-size: 13px !important;
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}
[data-testid="stMarkdownContainer"] a {
    color: #888 !important;
    text-decoration: underline;
    text-underline-offset: 3px;
}
[data-testid="stMarkdownContainer"] li {
    color: #c8c8c8 !important;
    font-size: 15px !important;
    margin-bottom: 4px !important;
    line-height: 1.7 !important;
}
[data-testid="stMarkdownContainer"] strong {
    color: #e0e0e0 !important;
    font-weight: 500 !important;
}
[data-testid="stMarkdownContainer"] hr {
    border-color: #1e1e1e !important;
    margin: 12px 0 !important;
}

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] p {
    color: #444 !important;
    font-size: 12px !important;
}

/* ══════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2a2a2a; }

/* ══════════════════════════════════════
   MOBILE RESPONSIVE
══════════════════════════════════════ */
@media (max-width: 768px) {

    /* Sidebar becomes top drawer on mobile */
    [data-testid="stSidebar"] {
        min-width: 100% !important;
        max-width: 100% !important;
        border-right: none !important;
        border-bottom: 1px solid #1e1e1e !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 16px 16px 14px !important;
        min-height: auto !important;
    }

    /* Larger tap targets on mobile */
    [data-testid="stChatMessage"] {
        max-width: 92% !important;
        padding: 13px 15px !important;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] li {
        font-size: 15px !important;
    }

    [data-testid="stChatInput"] textarea {
        font-size: 16px !important;
        padding: 13px 15px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        font-size: 16px !important;
    }
    [data-testid="stChatInputSubmitButton"] button {
        min-width: 44px !important;
        min-height: 44px !important;
    }

    /* Block container full width */
    .block-container,
    [data-testid="block-container"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Top bar full width */
    .topbar-wrap {
        padding: 10px 14px !important;
    }

    /* Empty state compact on mobile */
    .empty-state {
        padding: 36px 16px 24px !important;
    }
    .suggestion-chips {
        flex-direction: column !important;
        align-items: stretch !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── CLIENT ────────────────────────────────────────────────────────
client = setup_client()

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown("""
    <div style="display:flex;align-items:center;gap:11px;margin-bottom:26px;">
        <div style="width:30px;height:30px;background:#f0f0f0;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <rect x="1" y="1" width="5.5" height="5.5" rx="1.2" fill="#111"/>
                <rect x="7.5" y="1" width="5.5" height="5.5" rx="1.2" fill="#111"/>
                <rect x="1" y="7.5" width="5.5" height="5.5" rx="1.2" fill="#111"/>
                <rect x="7.5" y="7.5" width="5.5" height="5.5" rx="1.2" fill="#111" opacity="0.3"/>
            </svg>
        </div>
        <span style="font-size:15px;font-weight:600;color:#f0f0f0;letter-spacing:-0.02em;">Albert AI</span>
    </div>
    """, unsafe_allow_html=True)

    # Section label
    st.markdown('<p style="font-size:11px;color:#333;letter-spacing:0.09em;text-transform:uppercase;font-weight:500;margin-bottom:7px;">Menu</p>', unsafe_allow_html=True)

    # Chat nav — only active item shown (only page available)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:9px 10px;
                background:#1e1e1e;border:1px solid #252525;border-radius:8px;
                margin-bottom:16px;">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <rect x="1" y="1" width="5.5" height="5.5" rx="1.2" fill="#f0f0f0"/>
            <rect x="8.5" y="1" width="5.5" height="5.5" rx="1.2" fill="#f0f0f0"/>
            <rect x="1" y="8.5" width="5.5" height="5.5" rx="1.2" fill="#f0f0f0"/>
            <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1.2" fill="#f0f0f0" opacity="0.3"/>
        </svg>
        <span style="font-size:14px;color:#f0f0f0;font-weight:500;">Chat</span>
    </div>

    <div style="height:1px;background:#1a1a1a;margin-bottom:16px;"></div>
    """, unsafe_allow_html=True)

    # Upload section label
    st.markdown('<p style="font-size:11px;color:#333;letter-spacing:0.09em;text-transform:uppercase;font-weight:500;margin-bottom:8px;">Upload source</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    # Show file card when uploaded
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].upper()
        size_kb = round(uploaded_file.size / 1024)
        size_str = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024, 1)} MB"
        st.markdown(f"""
        <div style="background:#161616;border:1px solid #1e1e1e;border-radius:9px;
                    padding:10px 12px;margin-top:10px;">
            <div style="font-size:13px;font-weight:500;color:#c8c8c8;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        margin-bottom:3px;">{uploaded_file.name}</div>
            <div style="font-size:12px;color:#444;">{ext} · {size_str} · Ready</div>
        </div>
        """, unsafe_allow_html=True)

    # Push model badge + button to bottom
    st.markdown('<div style="flex:1;min-height:24px;"></div>', unsafe_allow_html=True)

    # Model badge
    st.markdown("""
    <div style="background:#161616;border:1px solid #1e1e1e;border-radius:9px;
                padding:10px 12px;margin-bottom:12px;">
        <div style="font-size:12px;color:#333;margin-bottom:3px;">Model</div>
        <div style="font-size:13px;font-weight:500;color:#666;">Llama 3.3 · 70B</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ══════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════
st.markdown("""
<div class="topbar-wrap" style="display:flex;align-items:center;justify-content:space-between;
     padding:11px 22px;border-bottom:1px solid #1a1a1a;background:#0f0f0f;">
    <span style="font-size:14px;font-weight:500;color:#f0f0f0;letter-spacing:-0.01em;">Chat</span>
    <div style="display:flex;align-items:center;gap:8px;">
        <div style="background:#141414;border:1px solid #1e1e1e;border-radius:20px;
                    padding:5px 12px;font-size:12px;color:#555;
                    display:flex;align-items:center;gap:6px;">
            <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;flex-shrink:0;"></div>
            Online
        </div>
        <div style="background:#141414;border:1px solid #1e1e1e;border-radius:20px;
                    padding:5px 12px;font-size:12px;color:#555;">
            Web search on
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []


# ══════════════════════════════════════
# EMPTY STATE
# ══════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state" style="display:flex;flex-direction:column;align-items:center;
         justify-content:center;padding:64px 24px 40px;text-align:center;">

        <div style="width:44px;height:44px;background:#161616;border:1px solid #1e1e1e;
                    border-radius:11px;display:flex;align-items:center;justify-content:center;
                    margin-bottom:18px;">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="1.5" y="1.5" width="7" height="7" rx="1.5" fill="#333"/>
                <rect x="11.5" y="1.5" width="7" height="7" rx="1.5" fill="#333"/>
                <rect x="1.5" y="11.5" width="7" height="7" rx="1.5" fill="#333"/>
                <rect x="11.5" y="11.5" width="7" height="7" rx="1.5" fill="#333" opacity="0.4"/>
            </svg>
        </div>

        <div style="font-size:20px;font-weight:500;color:#e8e8e8;
                    margin-bottom:8px;letter-spacing:-0.02em;">
            How can I help you today?
        </div>
        <div style="font-size:14px;color:#3a3a3a;margin-bottom:30px;line-height:1.6;">
            Ask anything · Upload a document · Describe an image to create
        </div>

        <div class="suggestion-chips"
             style="display:flex;gap:9px;flex-wrap:wrap;justify-content:center;">
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:9px;
                        padding:11px 16px;font-size:13px;color:#555;line-height:1.4;">
                Summarise a document
            </div>
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:9px;
                        padding:11px 16px;font-size:13px;color:#555;line-height:1.4;">
                Research a topic
            </div>
            <div style="background:#141414;border:1px solid #1e1e1e;border-radius:9px;
                        padding:11px 16px;font-size:13px;color:#555;line-height:1.4;">
                Generate an image
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════
# RENDER CHAT HISTORY
# ══════════════════════════════════════
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


# ══════════════════════════════════════
# INTENT CLASSIFIER
# ══════════════════════════════════════
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


# ══════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════
if prompt := st.chat_input("Ask Albert anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_image_request(prompt, client):
            full_response = handle_image_generation(prompt, client)
        else:
            full_response = handle_text_chat(
                prompt, client, uploaded_file, st.session_state.messages
            )

    st.session_state.messages.append({"role": "assistant", "content": full_response})