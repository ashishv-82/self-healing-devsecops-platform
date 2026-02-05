import requests
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVICES = [
    {"name": "Frontend", "url": "http://localhost:8080/", "timeout": 5},
    {"name": "Agent", "url": "http://localhost:8000/health", "timeout": 5},
    {"name": "Prometheus", "url": "http://localhost:9090/-/healthy", "timeout": 5},
    {"name": "Grafana", "url": "http://localhost:3000/api/health", "timeout": 5}
]

MAX_RETRIES = 12 # 12 * 5s = 60s
RETRY_INTERVAL = 5

def check_service(service):
    try:
        response = requests.get(service["url"], timeout=service["timeout"])
        if response.status_code == 200:
            logger.info(f"✅ {service['name']} is UP")
            return True
        else:
            logger.warning(f"⚠️ {service['name']} returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"❌ {service['name']} failed: {e}")
        return False

def validate_recovery():
    logger.info("Starting System Recovery Validation...")
    
    all_healthy = False
    attempts = 0
    
    while attempts < MAX_RETRIES:
        attempts += 1
        results = [check_service(s) for s in SERVICES]
        
        if all(results):
            all_healthy = True
            break
            
        logger.info(f"Waiting for services to recover... (Attempt {attempts}/{MAX_RETRIES})")
        time.sleep(RETRY_INTERVAL)
    
    if all_healthy:
        logger.info("🚀 SYSTEM RECOVERED SUCCESSFULLY")
        sys.exit(0)
    else:
        logger.error("🔥 SYSTEM FAILED TO RECOVER")
        sys.exit(1)

if __name__ == "__main__":
    validate_recovery()
