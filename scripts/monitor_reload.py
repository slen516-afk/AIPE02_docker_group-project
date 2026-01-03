import docker
import datetime
import os

# 設定監控目標容器名稱（需與 docker-compose.yml 一致）
TARGET_CONTAINER = "aipe02_backend"
LOG_FILE = "fail.log"
MAINTAINER = "tz"

def log_error(error_msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ALERT for {MAINTAINER}:\n{error_msg}\n{'-'*50}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"!!! Detected Hot Reload Failure, logged to {LOG_FILE} !!!")

def start_monitor():
    client = docker.from_env()
    print(f"--- Monitoring {TARGET_CONTAINER} for reload failures... ---")
    
    try:
        container = client.containers.get(TARGET_CONTAINER)
        # 持續串流容器日誌
        for line in container.logs(stream=True, follow=True):
            log_line = line.decode('utf-8')
            
            # 偵測常見的 Python 錯誤關鍵字
            if "Traceback" in log_line or "Error:" in log_line or "Internal Server Error" in log_line:
                log_error(log_line)
                
    except docker.errors.NotFound:
        print(f"Error: Container {TARGET_CONTAINER} not found. Please ensure it is running.")
    except Exception as e:
        print(f"Monitor encountered an error: {e}")

if __name__ == "__main__":
    # 確保日誌檔案存在
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"Log initialized by {MAINTAINER}\n")
            
    start_monitor()
