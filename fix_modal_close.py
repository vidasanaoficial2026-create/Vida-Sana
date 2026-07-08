import os

files = ['templates/tienda.html', 'templates/catalogo.html']

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the bad open modal logic
        bad_logic = "document.getElementById('loginOverlay').style.display='flex';"
        good_logic = "document.getElementById('loginOverlay').style.display='';\n             document.getElementById('loginOverlay').classList.add('open');"
        
        if bad_logic in content:
            content = content.replace(bad_logic, good_logic)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed close bug in {file}")
        else:
            print(f"Already fixed or not found in {file}")
