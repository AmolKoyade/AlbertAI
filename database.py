import os
import streamlit as st
from supabase import create_client, Client


# ---------------------------------------------------------------------------
# Supabase client
# ---------------------------------------------------------------------------

def _get_secret(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        try:
            val = st.secrets.get(key, "")
        except Exception:
            pass
    return val


@st.cache_resource
def get_supabase() -> Client:
    url   = _get_secret("SUPABASE_URL")
    key   = _get_secret("SUPABASE_KEY")
    if not url or not key:
        st.error("⚠️ SUPABASE_URL and SUPABASE_KEY not found in secrets.")
        st.stop()
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def sign_up(email: str, password: str) -> dict:
    try:
        sb  = get_supabase()
        res = sb.auth.sign_up({"email": email, "password": password})
        return {"success": True, "user": res.user}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_in(email: str, password: str) -> dict:
    try:
        sb  = get_supabase()
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        return {"success": True, "user": res.user, "session": res.session}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_out():
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

def create_conversation(user_id: str, title: str = "New Chat") -> str | None:
    """Create a new conversation and return its ID."""
    try:
        sb  = get_supabase()
        res = sb.table("conversations").insert({
            "user_id": user_id,
            "title":   title
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.error(f"DB error: {e}")
        return None


def get_conversations(user_id: str) -> list:
    """Get all conversations for a user, newest first."""
    try:
        sb  = get_supabase()
        res = (
            sb.table("conversations")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def update_conversation_title(conv_id: str, title: str):
    """Update conversation title (auto-named from first message)."""
    try:
        get_supabase().table("conversations").update(
            {"title": title[:60]}
        ).eq("id", conv_id).execute()
    except Exception:
        pass


def delete_conversation(conv_id: str):
    """Delete a conversation and all its messages."""
    try:
        sb = get_supabase()
        sb.table("messages").delete().eq("conversation_id", conv_id).execute()
        sb.table("conversations").delete().eq("id", conv_id).execute()
    except Exception as e:
        st.error(f"Delete error: {e}")


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def save_message(conv_id: str, role: str, content: str):
    """Save a single message to the database."""
    try:
        get_supabase().table("messages").insert({
            "conversation_id": conv_id,
            "role":            role,
            "content":         content
        }).execute()
        # Bump updated_at on the conversation
        get_supabase().table("conversations").update(
            {"updated_at": "now()"}
        ).eq("id", conv_id).execute()
    except Exception as e:
        st.error(f"Save error: {e}")


def get_messages(conv_id: str) -> list:
    """Get all messages for a conversation, oldest first."""
    try:
        sb  = get_supabase()
        res = (
            sb.table("messages")
            .select("*")
            .eq("conversation_id", conv_id)
            .order("created_at", desc=False)
            .execute()
        )
        return [{"role": m["role"], "content": m["content"]} for m in (res.data or [])]
    except Exception:
        return []