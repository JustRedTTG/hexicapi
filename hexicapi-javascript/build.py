import os

order = [
  'verinfo.js',
  'connectors.js',
  'client.js'
]


print("Compiling scripts...")
hexicapi = []

for file in order:
  with open(os.path.join('hexicapi', file), 'r') as f:
    hexicapi.extend(f.readline())
    
print("Building...")

with open('hexicapi.client.js', 'w') as f:
  f.write(''.join(hexicapi))