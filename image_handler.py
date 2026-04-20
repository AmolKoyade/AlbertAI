import streamlit as st
import urllib.parse
import hashlib
import requests
from io import BytesIO
from PIL import Image


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
IMAGE_WIDTH       = 1024
IMAGE_HEIGHT      = 1024
FETCH_TIMEOUT     = 60      # seconds to wait for Pollinations
MAX_RETRIES       = 2       # retry attempts on failure


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _enhance_prompt(raw_prompt: str, client) -> str:
    """
    Use Groq to rewrite the user's prompt into a vivid, detailed art prompt.
    Falls back to the original if the API call fails.
    """
    enhance_cmd = (
        f"Rewrite as a vivid, detailed image generation prompt for: '{raw_prompt}'. "
        f"Include art style, lighting, mood, and composition. "
        f"MAXIMUM 30 WORDS. Return ONLY the prompt — no preamble, no quotes."
    )
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}],
            temperature=0,   # Deterministic: same input → same enhanced prompt
            max_tokens=60
        )
        enhanced = resp.choices[0].message.content.strip()
        return enhanced if enhanced else raw_prompt
    except Exception as e:
        st.warning(f"⚠️ Prompt enhancement skipped ({e}). Using original prompt.")
        return raw_prompt


def _build_url(art_prompt: str) -> tuple:
    """
    Build the Pollinations image URL with a deterministic seed.
    Same prompt always produces the same seed → same image.
    """
    seed = int(hashlib.md5(art_prompt.lower().encode()).hexdigest(), 16) % 999999
    encoded = urllib.parse.quote(art_prompt, safe="")
    url = (
        f"{POLLINATIONS_BASE}/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&nologo=true&enhance=false&seed={seed}&model=flux"
    )
    return url, seed


def _fetch_image(url: str):
    """
    Download the image from Pollinations and return a PIL Image.
    Retries up to MAX_RETRIES times. Returns None if all attempts fail.
    Previously the code only built a URL and hoped the browser would load it.
    This function actually fetches and verifies the image server-side.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=FETCH_TIMEOUT)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                st.error(f"❌ Unexpected response from image server: {content_type}")
                return None

            img = Image.open(BytesIO(response.content))
            img.load()   # Force full decode — catches truncated/corrupt images early
            return img

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                st.toast(f"⏳ Image server is slow, retrying… ({attempt}/{MAX_RETRIES})")
            else:
                st.error("❌ Image server timed out after multiple retries. Please try again.")
                return None

        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Image server error: {e}")
            return None

        except Exception as e:
            st.error(f"❌ Could not load image: {e}")
            return None


# ---------------------------------------------------------------------------
# Main entry point — called from app.py
# ---------------------------------------------------------------------------

def handle_image_generation(prompt: str, client) -> str:
    """
    Full image generation pipeline:
      1. Enhance the user's prompt via Groq
      2. Build a deterministic Pollinations URL
      3. Fetch the image server-side (with retries)
      4. Display it using st.image()
      5. Provide a real download button
      6. Return a history-safe string for st.session_state
    """

    # ── Step 1: Enhance prompt ──────────────────────────────────────────────
    with st.status("✍️ Crafting your art prompt...", expanded=False) as status:
        art_prompt = _enhance_prompt(prompt, client)
        status.update(label="✅ Prompt ready", state="complete")

    # ── Step 2: Build URL ───────────────────────────────────────────────────
    image_url, seed = _build_url(art_prompt)

    # ── Step 3: Fetch image ─────────────────────────────────────────────────
    with st.status("🎨 Generating your image...", expanded=True) as status:
        st.caption(f"📝 Enhanced prompt: *{art_prompt}*")
        img = _fetch_image(image_url)

        if img is None:
            status.update(label="❌ Generation failed", state="error")
            # Never store None in session history — return a readable fallback
            return f"❌ Image generation failed for: *{art_prompt}*"

        status.update(label="✅ Image ready!", state="complete")

    # ── Step 4: Display the image ───────────────────────────────────────────
    st.image(img, caption=art_prompt, use_container_width=True)

    # ── Step 5: Download button ─────────────────────────────────────────────
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    st.download_button(
        label="💾 Download Image",
        data=img_bytes,
        file_name=f"albert_{seed}.png",
        mime="image/png",
        use_container_width=True
    )

    # ── Step 6: Save to history ─────────────────────────────────────────────
    # __IMAGE__ prefix tells app.py to render this as <img> when scrolling history
    return f"__IMAGE__{image_url}"