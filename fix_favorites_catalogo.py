import os
import re

file = 'templates/catalogo.html'

if os.path.exists(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace the static fav-icon inside renderCatalog
    # It looks like:
    #      const oldPrice = isPromo ? (p.precio * 1.3).toFixed(2) : null;
    #      return `
    #      <div class="prod-card">
    #        <div class="fav-icon"><i class="far fa-heart"></i></div>
    
    pattern = re.compile(r"const oldPrice = isPromo \? \(p\.precio \* 1\.3\)\.toFixed\(2\) : null;\s*return `\s*<div class=\"prod-card\">\s*<div class=\"fav-icon\"><i class=\"far fa-heart\"></i></div>", re.DOTALL)
    
    new_block = """const oldPrice = isPromo ? (p.precio * 1.3).toFixed(2) : null;
      
      let favs = [];
      try { favs = JSON.parse(localStorage.getItem('favoritos')) || []; } catch(e){}
      const isFav = favs.some(f => f.id === p.id);
      const heartClass = isFav ? 'fas fa-heart' : 'far fa-heart';
      const heartColor = isFav ? '#dc3545' : '#999';

      return `
      <div class="prod-card">
        <div class="fav-icon" onclick="toggleFavoriteStore(${p.id}, '${p.nombre.replace(/'/g, "\\'")}', ${p.precio}, '${p.imagen || ''}', this)" style="cursor:pointer; color:${heartColor};"><i class="${heartClass}"></i></div>"""

    if 'onclick="toggleFavoriteStore(' not in content.split('window.renderCatalog = function(products) {')[1]:
        match = pattern.search(content)
        if match:
            content = content[:match.start()] + new_block + content[match.end():]
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed renderCatalog in {file}")
        else:
            print(f"Could not find pattern in {file}")
    else:
        print(f"onclick already present in {file} renderCatalog")
