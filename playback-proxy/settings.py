import os
import sys
from dotenv import load_dotenv
from color_logger import logger

load_dotenv()

envs_correct = True

if (protocol := os.getenv("PROTOCOL")) is None:
    logger.error("PROTOCOL variable not found. Check your env file")
    envs_correct = False
if (endpoint := os.getenv("ENDPOINT")) is None:
    logger.error("ENDPOINT variable not found. Check your env file")
    envs_correct = False
if (mode := os.getenv("MODE")) is None:
    logger.error("MODE variable not found. Check your env file")
    envs_correct = False
if (record_name := os.getenv("RECORDING")) is None:
    logger.error("RECORDING variable not found. Check your env file")
    envs_correct = False
if (records_path := os.getenv("RECORDS_PATH")) is None:
    logger.error("RECORDS_PATH variable not found. Check your env file")
    envs_correct = False

try:
    socket_protocol = os.getenv("SOCKET_PROTOCOL")
    socket_rop = os.getenv("SOCKET_ROP")
except:
    None

try:
    ignore_log = os.getenv("IGNORE_LOG").split('|')
except:
    ignore_log = None

try:
    save_single = os.getenv("SAVE_SINGLE").split('|')
except:
    save_single = None

if envs_correct is False:
    sys.exit(2)