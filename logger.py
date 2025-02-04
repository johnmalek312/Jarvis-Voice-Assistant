import logging
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

app_logger = logging.getLogger("nova_logger")
app_logger.setLevel(logging.DEBUG)
#
# # File logging
file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Set formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# app_logger.addHandler(file_handler)
app_logger.addHandler(console_handler)
app_logger.propagate = False

