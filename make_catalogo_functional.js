const fs = require('fs');

let html = fs.readFileSync('templates/catalogo.html', 'utf8');

// 1. Add IDs to the select
html = html.replace('<select>', '<select id="catalogSort" onchange="applyCatalogFilters()">');

// 2. Add IDs to the slider elements
html = html.replace('<div class="price-slider-wrap">', '<div class="price-slider-wrap" id="pWrap">');
html = html.replace('<div class="price-slider-bar"></div>', '<div class="price-slider-bar" id="pBar"></div>');
html = html.replace('<div class="price-slider-handle left"></div>', '<div class="price-slider-handle left" id="pHLeft"></div>');
html = html.replace('<div class="price-slider-handle right"></div>', '<div class="price-slider-handle right" id="pHRight"></div>');

// 3. Add IDs to the price inputs
html = html.replace('<input type="text" value="S/ 18" readonly>', '<input type="text" id="pMinIn" value="S/ 0" readonly>');
html = html.replace('<input type="text" value="S/ 584" readonly>', '<input type="text" id="pMaxIn" value="S/ 500" readonly>');

// 4. Add IDs to grid and pagination
html = html.replace('<div class="shop-grid">', '<div class="shop-grid" id="catalogGrid">');
html = html.replace('<div class="shop-pagination">', '<div class="shop-pagination" id="catalogPagination">');

// 5. Add onclick to category links
// Find all <li><a href="#">...</a></li> inside .shop-cats and inject onclick
html = html.replace(/<ul class="shop-cats">([\s\S]*?)<\/ul>/, (match, p1) => {
    let replaced = p1.replace(/<a href="#">/g, '<a href="javascript:void(0)" onclick="setCatalogCat(this)">');
    return `<ul class="shop-cats" id="catalogCats">\n${replaced}</ul>`;
});

// The javascript to inject
const js = `
let cCat = 'all';
let cMin = 0;
let cMax = 500;
const absMax = 1000;
let cPage = 1;

function setCatalogCat(el) {
  document.querySelectorAll('#catalogCats a').forEach(a => {
    a.style.fontWeight = 'normal';
    a.style.color = '#555';
  });
  el.style.fontWeight = 'bold';
  el.style.color = '#111';
  
  // Extract text ignoring icons
  let text = el.childNodes[0].nodeValue.trim();
  cCat = text;
  cPage = 1;
  applyCatalogFilters();
}

function initSlider() {
  const wrap = document.getElementById('pWrap');
  if(!wrap) return;
  const bar = document.getElementById('pBar');
  const hL = document.getElementById('pHLeft');
  const hR = document.getElementById('pHRight');
  const iMin = document.getElementById('pMinIn');
  const iMax = document.getElementById('pMaxIn');
  
  let dragL = false, dragR = false;
  
  hL.addEventListener('mousedown', () => dragL = true);
  hR.addEventListener('mousedown', () => dragR = true);
  window.addEventListener('mouseup', () => {
    if(dragL || dragR) {
      dragL = false; dragR = false;
      applyCatalogFilters();
    }
  });
  
  window.addEventListener('mousemove', (e) => {
    if(!dragL && !dragR) return;
    const rect = wrap.getBoundingClientRect();
    let pct = (e.clientX - rect.left) / rect.width;
    pct = Math.max(0, Math.min(1, pct));
    
    if(dragL) {
      let maxPct = parseFloat(hR.style.left || '100%') / 100;
      if(pct > maxPct - 0.05) pct = maxPct - 0.05;
      hL.style.left = (pct * 100) + '%';
      bar.style.left = (pct * 100) + '%';
      cMin = Math.round(pct * absMax);
      iMin.value = 'S/ ' + cMin;
    }
    if(dragR) {
      let minPct = parseFloat(hL.style.left || '0%') / 100;
      if(pct < minPct + 0.05) pct = minPct + 0.05;
      hR.style.left = (pct * 100) + '%';
      bar.style.right = (100 - (pct * 100)) + '%';
      cMax = Math.round(pct * absMax);
      iMax.value = 'S/ ' + cMax;
    }
  });
  
  // Initial pos
  hL.style.left = '0%';
  bar.style.left = '0%';
  hR.style.left = '50%';
  bar.style.right = '50%';
}

function applyCatalogFilters() {
  if(!allProducts || allProducts.length === 0) return;
  
  let filtered = [...allProducts];
  
  if(cCat !== 'all') {
    // Match part of category name
    filtered = filtered.filter(p => p.categoria && p.categoria.includes(cCat.split(' ')[0]));
  }
  
  filtered = filtered.filter(p => p.precio >= cMin && p.precio <= cMax);
  
  const sort = document.getElementById('catalogSort').value;
  if(sort.includes('bajo a alto')) filtered.sort((a,b) => a.precio - b.precio);
  else if(sort.includes('alto a bajo')) filtered.sort((a,b) => b.precio - a.precio);
  else filtered.sort((a,b) => b.id - a.id);
  
  renderCatalog(filtered);
}

function renderCatalog(products) {
  const grid = document.getElementById('catalogGrid');
  const pag = document.getElementById('catalogPagination');
  if(!grid) return;
  
  const totalPages = Math.ceil(products.length / 6) || 1;
  if(cPage > totalPages) cPage = totalPages;
  const toShow = products.slice((cPage - 1) * 6, cPage * 6);
  
  if(toShow.length === 0) {
    grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:40px;">No se encontraron productos.</p>';
    pag.innerHTML = '';
    return;
  }
  
  grid.innerHTML = toShow.map((p, i) => {
    const isPromo = i % 3 === 2; // Fake promotion for visuals
    const oldPrice = isPromo ? (p.precio * 1.3).toFixed(2) : null;
    return \`
      <div class="shop-card">
        \${isPromo ? '<div class="shop-card-badge">-30%</div>' : ''}
        <img src="\${p.imagen}" alt="\${p.nombre}">
        <div class="shop-card-title">\${p.nombre}</div>
        <div class="shop-card-price">\${oldPrice ? \`<strike>S/ \${oldPrice}</strike> \` : ''}S/ \${p.precio.toFixed(2)}</div>
        <div class="shop-card-desc">\${(p.descripcion || p.nombre).substring(0, 100)}...</div>
        <button class="shop-card-btn" onclick="addToCart(\${p.id})">Añadir al carrito</button>
      </div>
    \`;
  }).join('');
  
  let phtml = '';
  for(let i=1; i<=totalPages; i++) {
    phtml += \`<span class="\${i === cPage ? 'active' : ''}" onclick="cPage=\${i}; applyCatalogFilters(); window.scrollTo({top: document.querySelector('.shop-section').offsetTop - 50, behavior:'smooth'})">\${i}</span>\`;
  }
  pag.innerHTML = phtml;
}

// Hook it into loadProducts
const originalLoadProducts = window.loadProducts;
window.renderProducts = function(data) {
  applyCatalogFilters();
};

document.addEventListener('DOMContentLoaded', () => {
  initSlider();
});
`;

html = html.replace('updateCart();\nloadProducts();', 'updateCart();\n' + js + '\nloadProducts();');

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log('Done');
