import requests

# getting list of titles for articles
def get_articles_batch(session, lang, apfrom="", batch_size=10):
    if not 1 <= batch_size <= 500:
        raise ValueError("batch_size must be between 1 and 500")

    URL = f"https://{lang}.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apfrom": apfrom,
        "aplimit": batch_size,
    }
    r = session.get(url=URL, params=PARAMS)
    data = r.json()

    pages = data["query"]["allpages"]
    next_title = data["continue"]["apcontinue"]

    return pages, next_title


def articles_batch_generator(lang, batches_count, batch_size=10):
    S = requests.Session()
    next_article = ""
    for _ in range(batches_count):
        batch, next_article = get_articles_batch(S, lang, next_article, batch_size)
        yield batch
