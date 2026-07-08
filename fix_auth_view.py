import os

files = ['templates/tienda.html', 'templates/catalogo.html']

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We need to find the else block inside toggleAuthView
        # Currently it looks like:
        # } else if (view === 'forgot') {
        #   ...
        # } else {
        #   document.getElementById('loginForm').classList.remove('hidden-form');
        #   document.getElementById('loginForm').style.display = 'block';
        # }
        
        # And we need to add a check for profileView!
        
        # Also need to add document.getElementById('profileView').style.display = 'none'; at the top.
        
        if "document.getElementById('profileView').style.display = 'none';" not in content:
            content = content.replace(
                "document.getElementById('loginForm').style.display = 'none';",
                "if(document.getElementById('profileView')) document.getElementById('profileView').style.display = 'none';\n    document.getElementById('loginForm').style.display = 'none';"
            )
        
        old_else = "} else {"
        new_else = """} else if (view === 'profile') {
      if(document.getElementById('profileView')) {
        document.getElementById('profileView').style.display = 'block';
        loadPedidos();
        loadFavoritosProfile();
      }
    } else {"""
        
        if "} else if (view === 'profile') {" not in content:
            content = content.replace("} else {", new_else, 1)  # replace only the first occurrence which is in toggleAuthView!
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed toggleAuthView in {file}")
