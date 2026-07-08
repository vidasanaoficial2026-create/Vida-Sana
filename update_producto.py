import re

with open('templates/producto.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix header visibility by adding specific styles for producto.html
header_styles = """
<style>
  .header { background: #fff !important; box-shadow: 0 1px 15px rgba(0,0,0,0.08); padding: 12px 24px !important; }
  .logo { color: var(--green-700) !important; }
  .nav a { color: var(--text) !important; }
  .mobile-toggle { color: var(--green-700) !important; }
  .product-details-container { margin-top: 120px; }
"""
content = content.replace("<style>", header_styles)

# 2. Update the buttons in the renderProduct function
old_actions = """<div class="pd-actions">
          <button class="btn-wsp-large" onclick="window.open('https://wa.me/51951679585?text=Hola%2C%20quiero%20comprar%20el%20producto%20${encodeURIComponent(p.nombre)}', '_blank')">
            <i class="fab fa-whatsapp"></i> Compra por WhatsApp
          </button>
          <button class="btn-fav" onclick="alert('Añadido a favoritos')">
            <i class="far fa-heart"></i> Favorito
          </button>
        </div>"""

new_actions = """<div class="pd-actions" style="display: flex; gap: 20px; margin-top: 25px;">
          <button class="btn-wsp-large" style="background: #2e7d32;" onclick="addToCartAndGo(${p.id}, '${p.nombre.replace("'", "\\'")}', ${p.precio}, '${p.imagen || ''}')">
            <i class="fas fa-shopping-cart"></i> Comprar
          </button>
          <button class="btn-fav" onclick="alert('Añadido a favoritos')">
            <i class="far fa-heart"></i> Favorito
          </button>
        </div>"""
content = content.replace(old_actions, new_actions)

# 3. Add addToCartAndGo function
js_func = """function renderProduct(p) {"""
new_js_func = """
  function addToCartAndGo(id, nombre, precio, imagen) {
    let cart = JSON.parse(localStorage.getItem('vid sana_cart') || '[]');
    let exist = cart.find(c => c.id === id);
    if (exist) {
      exist.qty += 1;
    } else {
      cart.push({ id, nombre, precio, imagen, qty: 1 });
    }
    localStorage.setItem('vid sana_cart', JSON.stringify(cart));
    window.location.href = '/tienda?open_cart=1';
  }

  function renderProduct(p) {"""
content = content.replace(js_func, new_js_func)

with open('templates/producto.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("producto.html updated")
