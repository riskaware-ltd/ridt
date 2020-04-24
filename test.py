import json
from config.idmfconfig import IDMFConfig

with open('default/config.json', 'r') as f:
    d = json.loads(f.read())

t = IDMFConfig(d)

print(t.total_air_change_rate)