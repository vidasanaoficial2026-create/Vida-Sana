import os
import re

with open('templates/landing.html', 'r', encoding='utf-8') as f:
    landing = f.read()

# Extract head
head_match = re.search(r'(<!DOCTYPE html>.*?</head>)', landing, re.DOTALL)
head = head_match.group(1) if head_match else ""
# Add some extra CSS for product details
head = head.replace('</style>', """
  .product-details-container {
    max-width: 1200px; margin: 150px auto 50px; padding: 20px;
    display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start;
    background: #fff; border-radius: 20px; box-shadow: 0 5px 30px rgba(0,0,0,0.05);
  }
  @media (max-width: 768px) { .product-details-container { grid-template-columns: 1fr; margin-top: 100px; gap: 20px; } }
  .pd-image {
    background: #f8f9fa; border-radius: 16px; padding: 40px;
    display: flex; justify-content: center; align-items: center; min-height: 400px;
  }
  .pd-image img { max-width: 100%; max-height: 500px; object-fit: contain; }
  .pd-info { padding: 20px 0; }
  .pd-breadcrumb { font-size: 13px; color: #718096; margin-bottom: 20px; }
  .pd-breadcrumb a { color: #3182ce; text-decoration: none; }
  .pd-category { font-size: 12px; font-weight: 700; text-transform: uppercase; color: #718096; letter-spacing: 1px; margin-bottom: 10px; }
  .pd-title { font-size: 32px; font-weight: 800; color: #1a202c; margin-bottom: 15px; line-height: 1.2; }
  .pd-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
  .pd-tag { background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .pd-desc { font-size: 15px; color: #4a5568; line-height: 1.7; margin-bottom: 30px; }
  .pd-features { display: flex; gap: 20px; margin-bottom: 30px; font-size: 13px; color: #2d3748; font-weight: 600; }
  .pd-features i { color: #38a169; margin-right: 5px; }
  
  .pd-actions { display: flex; gap: 15px; margin-top: 20px; }
  .btn-wsp-large {
    flex: 1; background: #2f6547; color: #fff; border: none; border-radius: 8px;
    padding: 16px; font-size: 16px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: 0.3s;
  }
  .btn-wsp-large:hover { background: #1f4530; }
  .btn-fav {
    background: #fff; color: #4a5568; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 16px 24px; font-size: 15px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.3s;
  }
  .btn-fav:hover { border-color: #cbd5e0; background: #f7fafc; }
</style>
""")

# Extract Header
header_match = re.search(r'(<!-- HEADER -->.*?)</header>', landing, re.DOTALL)
header = header_match.group(1) + "</header>" if header_match else ""

# Extract Footer
footer_match = re.search(r'(<!-- FOOTER -->.*?</footer>)', landing, re.DOTALL)
footer = footer_match.group(1) if footer_match else ""

body = f"""
<body>
{header}

<div class="product-details-container" id="productDetails">
  <div style="text-align:center; grid-column: 1/-1; padding: 50px;"><i class="fas fa-spinner fa-spin fa-3x" style="color:var(--primary)"></i><p>Cargando...</p></div>
</div>

{footer}

<script>
  // Mobile Nav logic (same as landing)
  function toggleMobileNav() {{
    const nav = document.getElementById('mainNav');
    nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
  }}
  
  const urlParams = new URLSearchParams(window.location.search);
  const productId = urlParams.get('id');

  async function loadProduct() {{
    if (!productId) {{
      document.getElementById('productDetails').innerHTML = '<h2 style="grid-column:1/-1;text-align:center;">Producto no encontrado</h2>';
      return;
    }}
    try {{
      const res = await fetch('/api/productos/' + productId);
      if (!res.ok) throw new Error('Not found');
      const data = await res.json();
      if(data.ok && data.producto) renderProduct(data.producto);
      else throw new Error('Invalid');
    }} catch(e) {{
      document.getElementById('productDetails').innerHTML = '<h2 style="grid-column:1/-1;text-align:center;">Producto no encontrado</h2>';
    }}
  }}

  function renderProduct(p) {{
    const tagsHtml = (p.categoria || '').split(' ').map(t => `<div class="pd-tag">${{t}}</div>`).join('');
    
    document.getElementById('productDetails').innerHTML = `
      <div class="pd-image">
        ${{p.imagen ? `<img src="${{p.imagen}}" alt="${{p.nombre}}">` : '<i class="fas fa-image" style="font-size:100px;color:#ccc"></i>'}}
      </div>
      <div class="pd-info">
        <div class="pd-breadcrumb">
          <a href="/">Inicio</a> / <a href="/catalogo.html">Productos</a> / ${{p.nombre}}
        </div>
        <div class="pd-category">${{p.categoria || 'Suplementos'}}</div>
        <h1 class="pd-title">${{p.nombre}}</h1>
        <div class="pd-tags">
          ${{tagsHtml}}
          <div class="pd-tag">4mnature</div>
        </div>
        
        <!-- PRICE IS INTENTIONALLY HIDDEN AS REQUESTED -->
        
        <div class="pd-desc">
          ${{p.descripcion || p.nombre}}
        </div>
        
        <div class="pd-features">
          <div><i class="fas fa-check-circle"></i> ${{p.stock > 0 ? 'En stock' : 'Agotado'}}</div>
          <div><i class="fas fa-truck"></i> Envío a todo el Perú</div>
          <div><i class="fas fa-shield-alt"></i> Pago seguro</div>
        </div>
        
        <div class="pd-actions">
          <button class="btn-wsp-large" onclick="window.open('https://wa.me/51951679585?text=Hola%2C%20quiero%20comprar%20el%20producto%20${{encodeURIComponent(p.nombre)}}', '_blank')">
            <i class="fab fa-whatsapp"></i> Compra por WhatsApp
          </button>
          <button class="btn-fav" onclick="alert('Añadido a favoritos')">
            <i class="far fa-heart"></i> Favorito
          </button>
        </div>
      </div>
    `;
  }}

  document.addEventListener('DOMContentLoaded', loadProduct);
</script>
</body>
</html>
"""

with open('templates/producto.html', 'w', encoding='utf-8') as f:
    f.write(head + body)

print("Created producto.html")
