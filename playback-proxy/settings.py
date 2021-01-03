import os
from dotenv import load_dotenv

load_dotenv()

protocol = os.getenv("PROTOCOL")
socket_protocol = os.getenv("SOCKET_PROTOCOL")
endpoint = os.getenv("ENDPOINT")
socket_rop = os.getenv("SOCKET_ROP")
mode = os.getenv("MODE")
record_name = os.getenv("RECORD_NAME")

try:
    ignore_log = os.getenv("IGNORE_LOG").split('|')
except:
    print()

try:
    save_single = os.getenv("SAVE_SINGLE").split('|')
except:
    print()
