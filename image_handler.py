import streamlit as st
import requests
import hashlib
from io import BytesIO
from PIL import Image


# ---------------------------------------------------------------------------
# Hugging Face Inference API — completely free, no credit card needed
# Model: stabilityai/stable-diffusion-2-1 (free tier)
# ---------------------------------------------------------------------------
HF_API_URL  = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
FETCH_TIMEOUT = 60
MAX_RETRIES   = 2


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


def _get_hf_token() -> str:
    """Load Hugging Face token from Streamlit secrets or environment."""
    import os
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        try:
            token = st.secrets.get("HF_TOKEN", "")
        except Exception:
            pass
    return token


def _fetch_image(art_prompt: str, seed: int) -> Image.Image | None:
    """Call Hugging Face Inference API and return PIL Image."""
    token = _get_hf_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "inputs": art_prompt,
        "parameters": {
            "seed": seed,
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=FETCH_TIMEOUT
            )

            # Model loading — Hugging Face loads models on first call
            if response.status_code == 503:
                import time
                wait = response.json().get("estimated_time", 20)
                st.warning(f"⏳ Model is loading, waiting {int(wait)}s… (this only happens once)")
                time.sleep(min(wait, 30))
                continue

            response.raise_for_status()

            img = Image.open(BytesIO(response.content))
            img.load()
            return img

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                st.warning(f"⏳ Server slow, retrying… ({attempt}/{MAX_RETRIES})")
            else:
                st.error("❌ Request timed out. Please try again.")
                return None

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response else "unknown"
            if code == 429:
                st.error("❌ Rate limit hit. Wait a minute and try again.")
            else:
                st.error(f"❌ Image server error ({code}): {e}")
            return None

        except Exception as e:
            st.error(f"❌ Could not generate image: {e}")
            return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def handle_image_generation(prompt: str, client) -> str:
    """
    Full pipeline:
      1. Enhance prompt via Groq
      2. Call Hugging Face free Stable Diffusion API
      3. Display with st.image()
      4. Provide download button
      5. Return history-safe string
    """

    # Step 1 — Enhance prompt
    with st.status("✍️ Crafting your art prompt...", expanded=False) as status:
        art_prompt = _enhance_prompt(prompt, client)
        status.update(label="✅ Prompt ready", state="complete")

    # Deterministic seed from prompt
    seed = int(hashlib.md5(art_prompt.lower().encode()).hexdigest(), 16) % 999999

    # Step 2 — Generate image
    with st.status("🎨 Generating your image...", expanded=True) as status:
        st.caption(f"📝 Prompt: *{art_prompt}*")
        img = _fetch_image(art_prompt, seed)

        if img is None:
            status.update(label="❌ Generation failed", state="error")
            return f"❌ Image generation failed for: *{art_prompt}*"

        status.update(label="✅ Image ready!", state="complete")

    # Step 3 — Display
    st.image(img, caption=art_prompt, use_container_width=True)

    # Step 4 — Download button
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

    # Step 5 — Save URL placeholder to history
    return f"🎨 Generated image: *{art_prompt}*"