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
FETCH_TIMEOUT     = 60
MAX_RETRIES       = 2

# FIX: "flux" model now requires payment on Pollinations.
# "turbo" is completely free and generates faster.
FREE_MODEL        = "turbo"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _enhance_prompt(raw_prompt: str, client) -> str:
    """Use Groq to rewrite the prompt into a vivid art prompt."""
    enhance_cmd = (
        f"Rewrite as a vivid, detailed image generation prompt for: '{raw_prompt}'. "
        f"Include art style, lighting, mood, and composition. "
        f"MAXIMUM 30 WORDS. Return ONLY the prompt — no preamble, no quotes."
    )
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}],
            temperature=0,
            max_tokens=60
        )
        enhanced = resp.choices[0].message.content.strip()
        return enhanced if enhanced else raw_prompt
    except Exception as e:
        st.warning(f"⚠️ Prompt enhancement skipped ({e}). Using original.")
        return raw_prompt


def _build_url(art_prompt: str) -> tuple:
    """Build a deterministic Pollinations URL. Same prompt = same image."""
    seed = int(hashlib.md5(art_prompt.lower().encode()).hexdigest(), 16) % 999999
    encoded = urllib.parse.quote(art_prompt, safe="")
    url = (
        f"{POLLINATIONS_BASE}/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&nologo=true&enhance=false&seed={seed}&model={FREE_MODEL}"
    )
    return url, seed


def _fetch_image(url: str):
    """Download and return a PIL Image. Retries on failure."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=FETCH_TIMEOUT)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                st.error(f"❌ Unexpected response from image server: {content_type}")
                return None

            img = Image.open(BytesIO(response.content))
            img.load()
            return img

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                st.warning(f"⏳ Image server slow, retrying… ({attempt}/{MAX_RETRIES})")
            else:
                st.error("❌ Image server timed out. Please try again.")
                return None

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            if status_code == 402:
                st.error("❌ This image model requires payment. Switching to free model automatically.")
            else:
                st.error(f"❌ Image server error ({status_code}): {e}")
            return None

        except Exception as e:
            st.error(f"❌ Could not load image: {e}")
            return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def handle_image_generation(prompt: str, client) -> str:
    """
    Full pipeline:
      1. Enhance prompt via Groq
      2. Build free Pollinations URL (turbo model)
      3. Fetch image server-side with retries
      4. Display with st.image()
      5. Provide download button
      6. Return history-safe string
    """

    # Step 1 — Enhance prompt
    with st.status("✍️ Crafting your art prompt...", expanded=False) as status:
        art_prompt = _enhance_prompt(prompt, client)
        status.update(label="✅ Prompt ready", state="complete")

    # Step 2 — Build URL
    image_url, seed = _build_url(art_prompt)

    # Step 3 — Fetch image
    with st.status("🎨 Generating your image...", expanded=True) as status:
        st.caption(f"📝 Prompt: *{art_prompt}*")
        img = _fetch_image(image_url)

        if img is None:
            status.update(label="❌ Generation failed", state="error")
            return f"❌ Image generation failed for: *{art_prompt}*"

        status.update(label="✅ Image ready!", state="complete")

    # Step 4 — Display
    st.image(img, caption=art_prompt, use_container_width=True)

    # Step 5 — Download button
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

    # Step 6 — Return for history
    return f"__IMAGE__{image_url}"