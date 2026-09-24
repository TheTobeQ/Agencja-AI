import os, re, requests
import google.generativeai as genai

# Pobieranie kluczy
gemini_key = os.environ.get("GEMINI_API_KEY")
hf_key = os.environ.get("HF_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
comments_url = os.environ.get("ISSUE_URL")
gh_token = os.environ.get("GITHUB_TOKEN")

genai.configure(api_key=gemini_key)

# Szukanie zdjęcia
image_urls = re.findall(r'(https?://\S+\.(?:jpg|jpeg|png|gif))', issue_body, re.IGNORECASE)
image_urls_markdown = re.findall(r'!\[.*?\]\((https?://.*?)\)', issue_body)
urls = image_urls + image_urls_markdown

if not urls:
    requests.post(comments_url, headers={"Authorization": f"Bearer {gh_token}"}, json={"body": "Hej! Nie widzę zdjęcia. Wrzuć nową ofertę wraz ze zdjęciem!"})
    exit()

img_url = urls[0]
img_data = requests.get(img_url).content
with open("temp.jpg", "wb") as f:
    f.write(img_data)

# Twój model PRO
model = genai.GenerativeModel('gemini-3-flash-preview')
plik = genai.upload_file("temp.jpg")

prompt = """
Jesteś nieszablonowym Dyrektorem Kreatywnym w agencji nieruchomości z Płocka. Twój cel to 'Pattern Interrupt' na Facebooku. 
Oto zdjęcie nieruchomości. Wykonaj dwa zadania:
1. Wymyśl niesamowitą wizję na ulepszenie tego zdjęcia (np. piękny ogród, luksusowe meble). Zapisz tę instrukcję po angielsku w nawiasach kwadratowych, np: [turn the empty room into a luxury living room].
2. Pod spodem napisz piekielnie angażujący post sprzedażowy na FB (po polsku), odwołujący się do emocji i wygenerowanej wizji. Użyj emotikon.
"""

odpowiedz = model.generate_content([prompt, plik]).text
instrukcja_grafika = re.search(r'\[(.*?)\]', odpowiedz)
post_fb = re.sub(r'\[.*?\]', '', odpowiedz).strip()

wynik = f"🔥 **Oto Twój gotowy post (Wersja PRO):**\n\n{post_fb}"

if instrukcja_grafika:
    polecenie = instrukcja_grafika.group(1)
    wynik += f"\n\n---\n*Instrukcja dla grafika AI: '{polecenie}'. Generowanie obrazu może chwilę potrwać na zewnętrznych serwerach.* 🖼️"

requests.post(comments_url, headers={"Authorization": f"Bearer {gh_token}"}, json={"body": wynik})
