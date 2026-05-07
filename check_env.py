
import os
import yaml

filepath = '/home/samu/.hermes/config.yaml'
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("--- config.yaml env ---")
    if 'env' in config:
        print(config['env'])
    else:
        print("No env section found.")
        
    print("\n--- config.yaml model ---")
    if 'model' in config:
        print(config['model'])
        
except Exception as e:
    print(f"Error reading config: {e}")

# Check for .env
try:
    with open('/home/samu/.hermes/.env', 'r') as f:
        print("\n--- .env ---")
        print(f.read())
except:
    print("\nNo .env file found.")
    
# Check for tokens in typical places
try:
    stdin, stdout, stderr = os.popen('find /home/samu/.hermes -name "*token*" -o -name "*cred*" -o -name "*auth*"')
    print("\n--- Other auth files ---")
    print(stdout.read())
except Exception as e:
    pass

