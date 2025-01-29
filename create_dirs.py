import os

dirs = [
    'src',
    'src/models',
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
