import os
import re

# The pattern matches the minified isDisabled function
# It typically looks like: isDisabled:function(e){return-1!==this.getOption("disabledExtensions").indexOf(e)}
# We want to make it safe: isDisabled:function(e){var t=this.getOption("disabledExtensions");return t&&-1!==t.indexOf(e)}

# Regex to match the function body. 
# We look for: isDisabled:function(ARG){return ... .indexOf(ARG)}
pattern = re.compile(rb'isDisabled:function\(([a-zA-Z0-9_]+)\)\{return-1!==this\.getOption\("disabledExtensions"\)\.indexOf\(\1\)\}')

def patch_file(path):
    with open(path, 'rb') as f:
        content = f.read()
    
    match = pattern.search(content)
    if match:
        arg_name = match.group(1).decode('utf-8')
        print(f"Found match in {path} with arg {arg_name}")
        
        # Replacement: check if array exists before calling indexOf
        # Original: return-1!==this.getOption("disabledExtensions").indexOf(e)
        # New:      var d=this.getOption("disabledExtensions");return d&&-1!==d.indexOf(e)
        
        replacement = f'isDisabled:function({arg_name}){{var d=this.getOption("disabledExtensions");return d&&-1!==d.indexOf({arg_name})}}'.encode('utf-8')
        
        new_content = pattern.sub(replacement, content)
        
        with open(path, 'wb') as f:
            f.write(new_content)
        print(f"Patched {path}")
        return True
    return False

count = 0
for root, dirs, files in os.walk("lite-site/_output/build"):
    for file in files:
        if file.endswith(".js"):
            if patch_file(os.path.join(root, file)):
                count += 1

print(f"Total patched files: {count}")

