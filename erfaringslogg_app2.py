
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
from datetime import datetime

# --- Google Sheets Setup ---
SHEET_ID = "145O8zzegaZc9WxIIR9--nzNEz1C5VNOe5VCyBHyKqZ4"
SHEET_NAME = "Erfaringslogg"
SERVICE_ACCOUNT_FILE = "service_account.json"

# Authenticate and connect to Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# --- Weather Data from MET API ---
def get_weather(lat=70.1112, lon=29.35321):
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    headers = {"User-Agent": "streamlit-weather-app"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        timeseries = data["properties"]["timeseries"]
        if timeseries:
            details = timeseries[0]["data"]["instant"]["details"]
            temperature = details.get("air_temperature", "N/A")
            wind_speed = details.get("wind_speed", "N/A")
            return f"{temperature}°C, {wind_speed} m/s"
    return "Værdata ikke tilgjengelig"

# --- Streamlit App ---
st.set_page_config(page_title="Erfaringslogg", layout="centered")
st.title("📘 Erfaringslogg med værdata")

with st.form("log_form"):
    col1, col2 = st.columns(2)
    with col1:
        dato = st.date_input("Dato", value=datetime.today())
    with col2:
        erfaring = st.text_input("Erfaring")
    notat = st.text_area("Notat")
    submitted = st.form_submit_button("Lagre oppføring")

if submitted and erfaring:
    weather = get_weather()
    new_row = [str(datetime.now()), str(dato), erfaring, notat, weather]
    sheet.append_row(new_row)
    st.success("Oppføring lagret!")

# --- Vis de tre siste oppføringene ---
data = sheet.get_all_values()
headers = data[0]
rows = data[1:]
df = pd.DataFrame(rows, columns=headers)
df_recent = df.tail(3).iloc[::-1]  # Siste tre, i omvendt rekkefølge

st.subheader("🕒 Siste 3 oppføringer")
for _, row in df_recent.iterrows():
    st.markdown(f"**Dato:** {row.get('Dato', '')}")
    st.markdown(f"**Erfaring:** {row.get('Erfaring', '')}")
    st.markdown(f"**Notat:** {row.get('Notat', '')}")
    st.markdown(f"**Vær:** {row.get('Vær', '')}")
    st.markdown("---")
