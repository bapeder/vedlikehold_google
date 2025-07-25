
import streamlit as st
import pandas as pd
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Set page config for mobile-friendly layout
st.set_page_config(page_title="Erfaringslogg", layout="centered")

# Authenticate with Google Sheets using st.secrets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)

# Open the spreadsheet and worksheet
spreadsheet_id = "145O8zzegaZc9WxIIR9--nzNEz1C5VNOe5VCyBHyKqZ4"
sheet = client.open_by_key(spreadsheet_id).worksheet("Erfaringslogg")

# Function to fetch weather data from MET API for given coordinates
def get_weather():
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    headers = {"User-Agent": "streamlit-erfaringslogg-app"}
    params = {"lat": 70.1112, "lon": 29.35321}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        timeseries = data["properties"]["timeseries"]
        if timeseries:
            details = timeseries[0]["data"]["instant"]["details"]
            temperature = details.get("air_temperature")
            wind_speed = details.get("wind_speed")
            return f"{temperature}°C, {wind_speed} m/s"
    return "Værdata ikke tilgjengelig"

# Function to append a new row to the sheet
def append_entry(id, dato, erfaring, notat, vær):
    sheet.append_row([id, dato, erfaring, notat, vær])

# Display the form
st.title("📘 Erfaringslogg")
with st.form("logg_form"):
    erfaring = st.text_input("Erfaring")
    notat = st.text_area("Notat")
    submitted = st.form_submit_button("Lagre oppføring")

    if submitted and erfaring:
        dato = datetime.now().strftime("%Y-%m-%d %H:%M")
        vær = get_weather()
        id = str(datetime.now().timestamp()).replace(".", "")
        append_entry(id, dato, erfaring, notat, vær)
        st.success("Oppføring lagret!")

# Fetch and display the last 3 entries
data = sheet.get_all_records()
df = pd.DataFrame(data)
if not df.empty:
    df = df.sort_values(by="Dato", ascending=False).head(3)
    st.subheader("🕒 Siste oppføringer")
    for _, row in df.iterrows():
        st.markdown(f"**Dato:** {row['Dato']}")
        st.markdown(f"**Erfaring:** {row['Erfaring']}")
        st.markdown(f"**Notat:** {row['Notat']}")
        st.markdown(f"**Vær:** {row['Vær']}")
        st.markdown("---")
else:
    st.info("Ingen oppføringer funnet.")
