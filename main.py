from fastapi import FastAPI, Query
import requests

app = FastAPI()

_EP = "https://downr.org/.netlify/functions"

_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://downr.org",
    "Referer": "https://downr.org/",
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def clean_url(url: str) -> str:
    if "?" in url:
        url = url.split("?")[0]
    if not url.endswith("/"):
        url += "/"
    return url


def fetch(url: str):
    url = clean_url(url)
    s = requests.Session()
    try:
        try:
            s.get(f"{_EP}/analytics", headers=_HEADERS, timeout=5)
        except:
            pass

        r = s.post(
            f"{_EP}/nyt",
            json={"url": url},
            headers=_HEADERS,
            timeout=30
        )

        data = r.json()

        if data.get("error"):
            return None, data.get("error")

        medias = data.get("medias", [])
        if not medias:
            return None, "no_media_found"

        return medias, None

    except Exception as e:
        return None, str(e)

    finally:
        s.close()


@app.get("/dl")
def download(
    url: str = Query(...),
    api: str = Query(None)
):
    if api != "@TeamDevXBots":
        return {"error": "invalid_api_key"}

    medias, err = fetch(url)

    if err:
        return {"error": err}

    video_360 = None
    video_240 = None
    audio = None

    for m in medias:
        quality = str(m.get("quality", ""))
        ext = m.get("extension")

        if ext == "mp4":
            if "360" in quality:
                video_360 = m.get("url")
            elif "240" in quality:
                video_240 = m.get("url")

        if ext in ["mp3", "m4a"]:
            audio = m.get("url")

    return {
        "status": True,
        "creator": "@TeamDevXBots",
        "video_360p": video_360,
        "video_240p": video_240,
        "audio": audio
  }
