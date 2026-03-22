import requests

API_KEY = "69e166aa2e8a95ca651cf8770c4f5c09"

def check_real_news(query):
    articles = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
            }

        url = f"https://gnews.io/api/v4/search?q={query}&lang=en&country=in&max=5&token={API_KEY}"
        res = requests.get(url, headers=headers).json()

        print("API RESPONSE:", res)  # Debug log

        if res.get("articles"):
            for a in res.get("articles", [])[:5]:
                if a.get("title") and a.get("url"):
                    articles.append({
                        "title": a["title"],
                        "url": a["url"],
                        "source": a["source"]["name"]
                    })

        # 🔁 fallback
        if len(articles) == 0:
            fallback_url = f"https://gnews.io/api/v4/top-headlines?country=us&token={API_KEY}"
            res = requests.get(fallback_url, headers=headers).json()

            print("Fallback API RESPONSE:", res)  # Debug log

            if res.get("articles"):
                for a in res.get("articles", [])[:5]:
                    articles.append({
                        "title": a["title"],
                        "url": a["url"],
                        "source": a["source"]["name"]
                    })

    except Exception as e:
        print("API ERROR:", e)

        print("Finally, returning empty articles list.", articles)

    return articles