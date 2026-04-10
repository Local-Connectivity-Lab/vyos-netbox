import json

CONFIG_FILE = "export-json-9-19-25.json"

with open(CONFIG_FILE) as f:
    d = json.load(f)


print(d.keys())
print(d['interfaces']['wireguard']['wg0']['peer'])
