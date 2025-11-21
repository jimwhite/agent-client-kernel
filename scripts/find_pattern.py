import os

def find_pattern(path):
    with open(path, 'rb') as f:
        content = f.read()
        
    # Search for "isDisabled" and print surrounding bytes
    idx = content.find(b'isDisabled:function')
    if idx != -1:
        print(f"Found in {path}:")
        print(content[idx:idx+100])

for root, dirs, files in os.walk("lite-site/_output/build"):
    for file in files:
        if file.endswith(".js"):
            find_pattern(os.path.join(root, file))

