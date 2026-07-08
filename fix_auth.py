import os

files = ['templates/tienda.html', 'templates/catalogo.html']

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Add hide for profileView
        if "if(document.getElementById('profileView')) document.getElementById('profileView').style.display = 'none';" not in content:
            content = content.replace(
                "document.getElementById('loginForm').style.display = 'none';",
                "document.getElementById('loginForm').style.display = 'none';\n  if(document.getElementById('profileView')) document.getElementById('profileView').style.display = 'none';"
            )
        
        # 2. Add the profile view logic in the if/else chain
        # We find:
        #   } else {
        #     document.getElementById('loginForm').classList.remove('hidden-form');
        #     document.getElementById('loginForm').style.display = 'block';
        #   }
        # And replace with profile check
        
        old_else = """  } else {
    document.getElementById('loginForm').classList.remove('hidden-form');
    document.getElementById('loginForm').style.display = 'block';
  }"""
  
        new_else = """  } else if (view === 'profile') {
    if(document.getElementById('profileView')) {
      document.getElementById('profileView').style.display = 'block';
      loadPedidos();
      loadFavoritosProfile();
    }
  } else {
    document.getElementById('loginForm').classList.remove('hidden-form');
    document.getElementById('loginForm').style.display = 'block';
  }"""
        
        if "} else if (view === 'profile') {" not in content:
            content = content.replace(old_else, new_else)
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file}")
