import os

files = ['templates/tienda.html', 'templates/catalogo.html']

google_script = """
  <!-- Google Identity Services Script -->
  <script src="https://accounts.google.com/gsi/client" async defer></script>
"""

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'accounts.google.com/gsi/client' not in content:
            # Inject right before the closing </head>
            content = content.replace('</head>', f'{google_script}</head>')
            
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Injected Google script in {file}")
