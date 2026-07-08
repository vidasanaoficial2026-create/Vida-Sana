import os
import re

card_css = """
  /* NUEVO DISEÑO DE TARJETA */
  .prod-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.03);
    transition: all 0.3s ease;
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 15px;
  }
  .prod-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  }
  .prod-card .fav-icon {
    position: absolute;
    top: 15px;
    right: 15px;
    color: #a0aec0;
    font-size: 20px;
    cursor: pointer;
    z-index: 2;
    transition: color 0.3s;
  }
  .prod-card .fav-icon:hover { color: #e53e3e; }
  .prod-card-image {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 15px;
    position: relative;
  }
  .prod-card-image img {
    max-height: 100%;
    max-width: 100%;
    object-fit: contain;
    transition: transform 0.4s ease;
  }
  .prod-card:hover .prod-card-image img {
    transform: scale(1.05);
  }
  .prod-card-body {
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  .prod-card-body .category {
    font-size: 12px;
    color: #4a5568;
    margin-bottom: 8px;
    font-weight: 500;
  }
  .prod-card-body h3 {
    font-size: 16px;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 12px;
    line-height: 1.3;
  }
  .delivery-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #e6f4ea;
    color: #006039;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 15px;
    align-self: flex-start;
  }
  .btn-details {
    display: block;
    width: 100%;
    text-align: center;
    background: #008055;
    color: #fff;
    padding: 12px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 14px;
    text-decoration: none;
    transition: background 0.3s;
    margin-top: auto;
  }
  .btn-details:hover {
    background: #006039;
    color: #fff;
  }
"""

card_html = """    <div class="prod-card">
      <div class="fav-icon"><i class="far fa-heart"></i></div>
      <div class="prod-card-image">
        ${p.imagen ? `<img src="${p.imagen}" alt="${p.nombre}" loading="lazy">` : '<i class="fas fa-leaf" style="font-size:56px;color:#ccc"></i>'}
      </div>
      <div class="prod-card-body">
        <div class="category">${p.categoria || 'General'}</div>
        <h3>${p.nombre}</h3>
        <div class="delivery-badge"><i class="fas fa-truck"></i> Delivery</div>
        <a href="/producto.html?id=${p.id}" class="btn-details">VER DETALLES</a>
      </div>
    </div>"""

def update_landing():
    with open('templates/landing.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace render code
    pattern = r'<div class="prod-card">.*?</div>\s*</div>\s*</div>'
    # Wait, the render block in landing.html is in `renderProducts()`
    # Let's just use regex to replace the entire return string
    import re
    content = re.sub(
        r'<div class="prod-card">.*?</div>\s*</div>\s*</div>',
        card_html,
        content,
        flags=re.DOTALL
    )

    # Insert CSS before </style>
    if 'NUEVO DISEÑO DE TARJETA' not in content:
        content = content.replace('</style>', card_css + '\n</style>')

    with open('templates/landing.html', 'w', encoding='utf-8') as f:
        f.write(content)

def update_catalogo():
    with open('templates/catalogo.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # The block in catalogo uses <div class="shop-card">
    content = re.sub(
        r'<div class="shop-card">.*?</div>\s*</div>\s*</div>',
        card_html.replace('prod-card', 'shop-card').replace('prod-card-image', 'shop-card-image').replace('prod-card-body', 'shop-card-body'),
        content,
        flags=re.DOTALL
    )
    
    # We also need to add the generic card_css but replace class names
    c_css = card_css.replace('prod-card', 'shop-card').replace('prod-card-image', 'shop-card-image').replace('prod-card-body', 'shop-card-body')
    if 'NUEVO DISEÑO DE TARJETA' not in content:
        content = content.replace('</style>', c_css + '\n</style>')

    with open('templates/catalogo.html', 'w', encoding='utf-8') as f:
        f.write(content)

update_landing()
update_catalogo()
print("Updated landing and catalogo")
