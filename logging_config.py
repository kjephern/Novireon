import logging
import sys


def setup_logging():
    """設定應用程式的日誌記錄器"""

    # 創建一個格式化器
    log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 獲取根記錄器 (root logger)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 設定最低層級為 DEBUG

    # --- 設定控制台輸出 (StreamHandler) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)

    # --- 設定檔案輸出 (FileHandler) ---
    file_handler = logging.FileHandler("app.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)

    # 將 handler 加入到根記錄器
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
