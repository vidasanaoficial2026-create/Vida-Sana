import os
import re

files = ['templates/tienda.html', 'templates/catalogo.html']

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We want to replace <div class="fav-icon"><i class="far fa-heart"></i></div> inside prodCard(p)
        # First check if the onclick is already there
        if 'onclick="toggleFavoriteStore(' not in content:
            # Let's find the exact block for prodCard
            # It looks like:
            # function prodCard(p) {
            #   const outOfStock = p.stock <= 0;
            #   return `
            #     <div class="prod-card">
            #       <div class="fav-icon"><i class="far fa-heart"></i></div>
            
            pattern = re.compile(r"function prodCard\(p\) \{.*?const outOfStock = p\.stock <= 0;.*?return `.*?<div class=\"prod-card\">.*?<div class=\"fav-icon\"><i class=\"far fa-heart\"></i></div>", re.DOTALL)
            
            new_block = """function prodCard(p) {
  const outOfStock = p.stock <= 0;
  let favs = [];
  try { favs = JSON.parse(localStorage.getItem('favoritos')) || []; } catch(e){}
  const isFav = favs.some(f => f.id === p.id);
  const heartClass = isFav ? 'fas fa-heart' : 'far fa-heart';
  const heartColor = isFav ? '#dc3545' : '#999';
  
  return `
    <div class="prod-card">
      <div class="fav-icon" onclick="toggleFavoriteStore(${p.id}, '${p.nombre.replace(/'/g, "\\'")}', ${p.precio}, '${p.imagen || ''}', this)" style="cursor:pointer; color:${heartColor};"><i class="${heartClass}"></i></div>"""

            match = pattern.search(content)
            if match:
                content = content[:match.start()] + new_block + content[match.end():]
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed prodCard in {file}")
            else:
                print(f"Could not find pattern in {file}")
        else:
            print(f"onclick already present in {file}")
