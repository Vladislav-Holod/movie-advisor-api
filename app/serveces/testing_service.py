import requests

r = requests.get(
    "https://openlibrary.org/search.json",
    params={"q": "Hello"}
)

data = r.json()

books = data["docs"][:3]

for b in books:
    print("Title:", b.get("title"))
    print("Author:", b.get("author_name"))
    print("Cover ID:", b.get("cover_i"))
    print(b.get('cover_i'))