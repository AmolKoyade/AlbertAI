import streamlit as st
import requests
import hashlib
import os
from io import BytesIO
from PIL import Image


# ---------------------------------------------------------------------------
# Free image generation APIs — tried in order until one works
# ---------------------------------------------------------------------------

FETCH_TIMEOUT = 90
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
        st.warning(f"⚠️ Prompt enhancement skipped. Using original.")
        return raw_prompt


def _get_hf_token() -> str:
    """Load HF token from env or Streamlit secrets."""
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        try:
            token = st.secrets.get("HF_TOKEN", "")
        except Exception:
            pass
    return token


def _get_seed(art_prompt: str) -> int:
    return int(hashlib.md5(art_prompt.lower().encode()).hexdigest(), 16) % 999999


# ---------------------------------------------------------------------------
# Method 1 — Hugging Face Inference API (free with token)
# ---------------------------------------------------------------------------
def _try_huggingface(art_prompt: str, seed: int) -> Image.Image | None:
    import time
    token = _get_hf_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": art_prompt,
        "parameters": {"seed": seed, "num_inference_steps": 25}
    }

    models = [
        "stabilityai/stable-diffusion-2-1",
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4"
    ]

    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=FETCH_TIMEOUT)

            if resp.status_code == 503:
                wait = min(resp.json().get("estimated_time", 20), 30)
                time.sleep(wait)
                resp = requests.post(url, headers=headers, json=payload, timeout=FETCH_TIMEOUT)

            if resp.status_code == 200:
                img = Image.open(BytesIO(resp.content))
                img.load()
                return img

        except Exception:
            continue

    return None


# ---------------------------------------------------------------------------
# Method 2 — Stable Horde (free, community GPU, no key needed)
# ---------------------------------------------------------------------------
def _try_stable_horde(art_prompt: str, seed: int) -> Image.Image | None:
    import time
    import base64

    try:
        # Submit generation job
        headers = {
            "apikey": "0000000000",   # anonymous free key
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": art_prompt,
            "params": {
                "seed": str(seed),
                "steps": 25,
                "width": 512,
                "height": 512,
                "cfg_scale": 7.5,
                "sampler_name": "k_euler"
            },
            "models": ["stable_diffusion"],
            "r2": False
        }

        submit = requests.post(
            "https://stablehorde.net/api/v2/generate/async",
            headers=headers,
            json=payload,
            timeout=30
        )
        if submit.status_code != 202:
            return None

        job_id = submit.json().get("id")
        if not job_id:
            return None

        # Poll for result (max 90 seconds)
        for _ in range(18):
            time.sleep(5)
            check = requests.get(
                f"https://stablehorde.net/api/v2/generate/check/{job_id}",
                headers={"apikey": "0000000000"},
                timeout=15
            )
            data = check.json()
            if data.get("done"):
                break

        # Fetch result
        result = requests.get(
            f"https://stablehorde.net/api/v2/generate/status/{job_id}",
            headers={"apikey": "0000000000"},
            timeout=15
        )
        generations = result.json().get("generations", [])
        if not generations:
            return None

        img_data = base64.b64decode(generations[0]["img"])
        img = Image.open(BytesIO(img_data))
        img.load()
        return img

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Method 3 — Pollinations (fallback, no-model param)
# ---------------------------------------------------------------------------
def _try_pollinations(art_prompt: str, seed: int) -> Image.Image | None:
    import urllib.parse
    try:
        encoded = urllib.parse.quote(art_prompt, safe="")
        # Try without specifying model — lets Pollinations pick free one
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=512&height=512&nologo=true&seed={seed}"
        )
        resp = requests.get(url, timeout=FETCH_TIMEOUT)
        if resp.status_code == 200 and "image" in resp.headers.get("Content-Type", ""):
            img = Image.open(BytesIO(resp.content))
            img.load()
            return img
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def handle_image_generation(prompt: str, client) -> str:

    # Step 1 — Enhance prompt
    with st.status("✍️ Crafting your art prompt...", expanded=False) as status:
        art_prompt = _enhance_prompt(prompt, client)
        status.update(label="✅ Prompt ready", state="complete")

    seed = _get_seed(art_prompt)
    img  = None

    # Step 2 — Try each method in order
    with st.status("🎨 Generating your image...", expanded=True) as status:
        st.caption(f"📝 Prompt: *{art_prompt}*")

        # Method 1 — Hugging Face
        if not img:
            st.caption("Trying Hugging Face...")
            img = _try_huggingface(art_prompt, seed)

        # Method 2 — Stable Horde (community GPUs, always free)
        if not img:
            st.caption("Trying Stable Horde (free community GPUs)...")
            img = _try_stable_horde(art_prompt, seed)

        # Method 3 — Pollinations without model param
        if not img:
            st.caption("Trying Pollinations fallback...")
            img = _try_pollinations(art_prompt, seed)

        if img is None:
            status.update(label="❌ All methods failed", state="error")
            return (
                f"❌ Image generation failed for: *{art_prompt}*\n\n"
                f"**Fix:** Add your `HF_TOKEN` from huggingface.co to secrets for reliable generation."
            )

        status.update(label="✅ Image ready!", state="complete")

    # Step 3 — Display
    st.image(img, caption=art_prompt, use_container_width=True)

    # Step 4 — Download
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

    return f"🎨 Generated image: *{art_prompt}*"