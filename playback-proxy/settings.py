import os
from dotenv import load_dotenv

load_dotenv()

protocol = os.getenv("PROTOCOL")
endpoint = os.getenv("ENDPOINT")
mode = os.getenv("MODE")
record_name = os.getenv("RECORD_NAME")
records_path = os.getenv("RECORDS_PATH")

try:
    socket_protocol = os.getenv("SOCKET_PROTOCOL")
    socket_rop = os.getenv("SOCKET_ROP")
except:
    None

try:
    ignore_log = os.getenv("IGNORE_LOG").split('|')
except:
    None

try:
    save_single = os.getenv("SAVE_SINGLE").split('|')
except:
    None
