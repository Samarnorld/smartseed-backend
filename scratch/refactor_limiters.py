# scratch/refactor_limiters.py
import re
import os

files_to_refactor = [
    "app/api/endpoints/account_deletion.py",
    "app/api/endpoints/elevation.py",
    "app/api/endpoints/nandi_recommendations.py",
    "app/api/endpoints/nandi_seed.py",
    "app/api/endpoints/ndvi.py",
    "app/api/endpoints/ndvi_anomaly.py",
    "app/api/endpoints/ndvi_climatology.py",
    "app/api/endpoints/ndvi_tiles.py",
    "app/api/endpoints/rainfall.py",
    "app/api/endpoints/rainfall_anomaly.py",
    "app/api/endpoints/rainfall_climatology.py",
    "app/api/endpoints/rainfall_monthly.py",
    "app/api/endpoints/rainfall_tiles.py",
    "app/api/endpoints/soil_analysis.py",
    "app/api/endpoints/soil_tiles.py",
    "app/api/endpoints/temperature.py",
    "app/api/endpoints/temperature_anomaly.py",
    "app/api/endpoints/temperature_monthly.py",
    "app/api/endpoints/temperature_tiles.py",
    "app/api/endpoints/ussd.py"
]

base_dir = r"c:\Users\Elitebook\Desktop\smartseed-backend"

for rel_path in files_to_refactor:
    abs_path = os.path.join(base_dir, rel_path.replace("/", os.sep))
    if not os.path.exists(abs_path):
        print(f"File not found: {abs_path}")
        continue
    
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Replace the slowapi imports with app.core.limiter import
    # Match:
    # from slowapi import Limiter
    # from slowapi.util import get_remote_address
    content = re.sub(
        r'from slowapi import Limiter\s*\r?\n\s*from slowapi\.util import get_remote_address',
        'from app.core.limiter import limiter',
        content
    )
    
    # Or in case they are separated by something else or in different order, try individual replacements:
    content = content.replace("from slowapi import Limiter", "from app.core.limiter import limiter")
    # Clean up get_remote_address import if it's still there
    content = re.sub(r'from slowapi\.util import get_remote_address\s*\r?\n', '', content)
    content = content.replace("from slowapi.util import get_remote_address", "")
    
    # 2. Remove limiter = Limiter(key_func=get_remote_address)
    content = re.sub(r'limiter = Limiter\(key_func=get_remote_address\)\s*\r?\n', '', content)
    content = content.replace("limiter = Limiter(key_func=get_remote_address)", "")
    
    if content != original:
        with open(abs_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"Refactored: {rel_path}")
    else:
        print(f"No changes made to: {rel_path}")

print("Done refactoring!")
