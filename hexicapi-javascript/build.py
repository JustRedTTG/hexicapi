import os
from jsmin import jsmin

order = [
  'verinfo.js',
  'connectors.js',
  'socketMessage.js',
  'client.js'
]


print("Compiling scripts...")
hexicapi = []

for file in order:
  with open(os.path.join('hexicapi', file), 'r') as f:
    hexicapi.extend(jsmin(f.read()))
    
print("Building...")

with open('hexicapi.client.js', 'w') as f:
  f.write(''.join(hexicapi))