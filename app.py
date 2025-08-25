import streamlit as st
import os
import io
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(page_title="📤 Drive Uploader", page_icon="📁")
st.title("📁 Upload Files Directly to Google Drive Folder")

# ----------------------------
# Define Google Drive Scope
# ----------------------------
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ----------------------------
# Authenticate with Google (once)
# ----------------------------
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# If no token or expired
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if os.path.exists('credentials.json'):
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            st.error("❌ credentials.json file not found.")
            st.stop()
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# ----------------------------
# Connect to Google Drive API
# ----------------------------
try:
    drive_service = build('drive', 'v3', credentials=creds)
except Exception as e:
    st.error(f"❌ Error connecting to Google Drive: {e}")
    st.stop()

# ----------------------------
# Upload Area
# ----------------------------
uploaded_file = st.file_uploader("📂 Select a file to upload to Drive", type=None)

# 🔁 Replace with your Drive Folder ID (not file ID)
FOLDER_ID = '1lVsJ3-CjtgKaAyBszmaDWEC6MaOVpZwV'  # <--- Change if needed

if uploaded_file is not None:
    st.info(f"📤 Uploading `{uploaded_file.name}`...")

    # File metadata with folder destination
    file_metadata = {
        'name': uploaded_file.name,
        'parents': [FOLDER_ID]
    }

    # Convert file to MediaUpload
    media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)

    try:
        # Upload the file
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        st.success(f"✅ Upload done! File ID: {file.get('id')}")
        st.markdown(f"[🔗 View File in Drive](https://drive.google.com/file/d/{file.get('id')})", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Upload failed: {e}")