import requests
from datetime import datetime
import time as t
import json

# === TELEGRAM-INNSTILLINGER ===
telegram_bot_token = '7361447657:AAHG_NNIJPzAGlb0xvinEBEiGnM9Pq4Oou8'
telegram_chat_id = '7659822832'

def send_telegram(message):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {"chat_id": telegram_chat_id, "text": message}
    response = requests.post(url, data=data)
    print("Statuskode:", response.status_code)
    print("Respons:", response.text)

# === LAST INN TOKENS FRA FIL ===
with open("tokens.json", "r") as f:
    tokens = json.load(f)

cookies = {
    'XSRF-TOKEN': tokens["XSRF-TOKEN"],
    'ai_session': tokens["ai_session"],
    'SVVSecurityToken': tokens["SVVSecurityToken"]
}

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'X-XSRF-TOKEN': cookies['XSRF-TOKEN'],
    'Authorization': f"Bearer {cookies['SVVSecurityToken']}"
}

trafikkstasjoner = {
    '051': 'Drøbak',
    '061': 'Billingstad',
    '071': 'Lillestrøm',
    '081': 'Risløkka'
}

while True:
    print("\n🔁 Starter ny sjekk...")
    alle_timer = []
    juli_august_timer = []

    for stasjon_id, stasjonsnavn in trafikkstasjoner.items():
        url = f"https://backend-bestill-time-oppkjoring.atlas.vegvesen.no/provetimer?arbeidsflytId=1161611466&klasse=B&trafikkstasjonIder={stasjon_id}"
        response = requests.get(url, headers=headers, cookies=cookies)

        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    for blokk in data:
                        oppmote = blokk.get("oppmotested", stasjonsnavn)
                        for time in blokk["provetimer"]:
                            start = time["start"]
                            dato = start[:10]
                            if dato.startswith("2025-07") or dato.startswith("2025-08"):
                                juli_august_timer.append(f"📍 {oppmote}: {start.replace('T', ' ')}")
                            else:
                                alle_timer.append(f"📍 {oppmote}: {start.replace('T', ' ')}")
                else:
                    print(f"📍 {stasjonsnavn}: Ingen ledige timer.")
            except Exception as e:
                print(f"❌ Klarte ikke lese JSON for {stasjonsnavn}: {e}")
        else:
            print(f"❌ Feil ved {stasjonsnavn}: Statuskode {response.status_code}")

    if juli_august_timer:
        melding = "✅ Ledige timer i juli/august:\n" + "\n".join(juli_august_timer)
    else:
        melding = "❌ Ingen ledige oppkjøringstimer i juli eller august."
        if alle_timer:
            melding += "\n\n📅 Men det finnes timer senere:\n" + "\n".join(alle_timer)

    send_telegram(melding)
    print("🕐 Venter 1 minutt før neste sjekk...")
    t.sleep(60)
