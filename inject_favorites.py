import os

files = ['templates/tienda.html', 'templates/catalogo.html']

old_prod_card = """  function prodCard(p) {
    const outOfStock = p.stock <= 0;
    return `
      <div class="prod-card">
        <div class="fav-icon"><i class="far fa-heart"></i></div>"""

new_prod_card = """  function prodCard(p) {
    const outOfStock = p.stock <= 0;
    let favs = [];
    try { favs = JSON.parse(localStorage.getItem('favoritos')) || []; } catch(e){}
    const isFav = favs.some(f => f.id === p.id);
    const heartClass = isFav ? 'fas fa-heart' : 'far fa-heart';
    const heartColor = isFav ? '#dc3545' : '#999';
    
    return `
      <div class="prod-card">
        <div class="fav-icon" onclick="toggleFavoriteStore(${p.id}, '${p.nombre.replace(/'/g, "\\'")}', ${p.precio}, '${p.imagen || ''}', this)" style="cursor:pointer; color:${heartColor};"><i class="${heartClass}"></i></div>"""

toggle_function = """
  function toggleFavoriteStore(id, nombre, precio, imagen, element) {
    let favs = [];
    try { favs = JSON.parse(localStorage.getItem('favoritos')) || []; } catch(e){}
    
    const idx = favs.findIndex(f => f.id === id);
    if (idx >= 0) {
      favs.splice(idx, 1);
      element.style.color = '#999';
      element.innerHTML = '<i class="far fa-heart"></i>';
      showToast('Eliminado de favoritos');
    } else {
      favs.push({id, nombre, precio, imagen});
      element.style.color = '#dc3545';
      element.innerHTML = '<i class="fas fa-heart"></i>';
      showToast('Añadido a favoritos');
    }
    localStorage.setItem('favoritos', JSON.stringify(favs));
    
    if (typeof loadFavoritosProfile === 'function') {
      loadFavoritosProfile();
    }
  }
"""

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "function toggleFavoriteStore" not in content:
            # 1. Replace prodCard
            if old_prod_card in content:
                content = content.replace(old_prod_card, new_prod_card)
            
            # 2. Append toggle function at the end of the script block
            # We can find "async function handleGoogleLogin" and put it before that
            if "async function handleGoogleLogin" in content:
                content = content.replace("async function handleGoogleLogin", toggle_function + "\n  async function handleGoogleLogin")
            else:
                # Just stick it before the last </script>
                content = content.replace("</script>\n</body>", toggle_function + "\n</script>\n</body>")
                
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Added favorites logic to {file}")
        else:
            print(f"Logic already exists in {file}")
