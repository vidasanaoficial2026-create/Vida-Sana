const fs = require('fs');

const htmlNew = `<!-- NEW SHOP LAYOUT (FROM SCREENSHOTS) -->
  <div class="shop-section">
    <!-- SIDEBAR -->
    <div class="shop-sidebar">
      <div class="shop-filter-group" style="border-bottom: 2px solid #eee; padding-bottom:15px; margin-bottom:15px;">
        <select id="sortSelect" onchange="applyFilters()" style="width:100%; border:1px solid #ddd; border-radius:4px; padding:10px; outline:none; font-family:inherit; font-weight:bold; cursor:pointer; background:#f9f9f9;">
          <option value="latest">Ordenar por los últimos</option>
          <option value="price-asc">Ordenar por precio: bajo a alto</option>
          <option value="price-desc">Ordenar por precio: alto a bajo</option>
        </select>
      </div>
      
      <div class="shop-filter-group" style="border-bottom: 2px solid #eee; padding-bottom:15px; margin-bottom:15px;">
        <div class="shop-filter-title" style="font-weight:700; margin-bottom:15px; font-size:1.1em;">Filtrar por precio</div>
        <div style="display:flex; gap:10px; margin-bottom:15px; align-items:center;">
          <input type="number" id="minPrice" placeholder="S/ Min" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px;">
          <span>-</span>
          <input type="number" id="maxPrice" placeholder="S/ Max" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px;">
        </div>
        <button onclick="applyFilters()" style="width:100%; padding:10px; background:#2e7d32; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Aplicar Filtro</button>
      </div>
  
      <div class="shop-filter-group">
        <div class="shop-filter-title" style="font-weight:700; margin-bottom:15px; font-size:1.1em;">Categorías</div>
        <ul class="shop-cats" id="sidebarCats">
          <!-- JS fills this -->
        </ul>
      </div>
    </div>
  
    <!-- CONTENT -->
    <div class="shop-content">
      <div class="shop-grid" id="catalogGrid">
        <!-- JS fills this -->
      </div>
      <div class="shop-pagination" id="catalogPagination">
        <!-- JS fills this -->
      </div>
    </div>
  </div>`;

const jsNew = `let currentFilterCat = 'all';
let currentPage = 1;
const itemsPerPage = 9;

function renderCategories() {
  const cats = [...new Set(allProducts.map(p => p.categoria))].filter(Boolean).sort();
  const ul = document.getElementById('sidebarCats');
  if(!ul) return;
  let html = \`<li class="\${currentFilterCat==='all'?'active':''}"><a href="javascript:void(0)" onclick="setCatFilter('all')">Todas las categorías</a></li>\`;
  cats.forEach(c => {
    html += \`<li class="\${currentFilterCat===c?'active':''}"><a href="javascript:void(0)" onclick="setCatFilter('\${c}')">\${c}</a></li>\`;
  });
  ul.innerHTML = html;
}

function setCatFilter(cat) {
  currentFilterCat = cat;
  currentPage = 1;
  applyFilters();
}

function applyFilters() {
  let filtered = [...allProducts];
  
  if(currentFilterCat !== 'all') {
    filtered = filtered.filter(p => p.categoria === currentFilterCat);
  }
  
  const minP = parseFloat(document.getElementById('minPrice').value);
  const maxP = parseFloat(document.getElementById('maxPrice').value);
  if (!isNaN(minP)) filtered = filtered.filter(p => p.precio >= minP);
  if (!isNaN(maxP)) filtered = filtered.filter(p => p.precio <= maxP);
  
  const sort = document.getElementById('sortSelect').value;
  if(sort === 'price-asc') filtered.sort((a,b) => a.precio - b.precio);
  else if(sort === 'price-desc') filtered.sort((a,b) => b.precio - a.precio);
  else filtered.sort((a,b) => b.id - a.id);
  
  renderCatalog(filtered);
}

function renderCatalog(products) {
  renderCategories();
  const grid = document.getElementById('catalogGrid');
  const pagination = document.getElementById('catalogPagination');
  if(!grid) return;
  
  const totalPages = Math.ceil(products.length / itemsPerPage) || 1;
  if(currentPage > totalPages) currentPage = totalPages;
  
  const start = (currentPage - 1) * itemsPerPage;
  const toShow = products.slice(start, start + itemsPerPage);
  
  if(toShow.length === 0) {
    grid.innerHTML = '<p style="grid-column:1/-1; text-align:center; padding:40px; font-weight:bold; color:#666;">No se encontraron productos en esta categoría o rango de precio.</p>';
    pagination.innerHTML = '';
    return;
  }
  
  grid.innerHTML = toShow.map(p => {
    const isOferta = p.categoria === 'Top Ventas' || p.nombre.toLowerCase().includes('oferta') || p.id % 4 === 0;
    return \`
    <div class="shop-card">
      \${isOferta ? '<div class="shop-badge">-20%</div>' : ''}
      <img src="\${p.imagen}" alt="\${p.nombre}">
      <div class="shop-card-title">\${p.nombre}</div>
      <div class="shop-card-price">
        \${isOferta ? \`<span style="text-decoration:line-through;color:#999;font-size:14px;margin-right:5px;">S/\${(p.precio * 1.2).toFixed(2)}</span>\` : ''}
        S/\${p.precio.toFixed(2)}
      </div>
      <div class="shop-card-desc">\${p.descripcion ? p.descripcion.substring(0, 60) + '...' : 'Suplemento natural'}</div>
      <button class="shop-card-btn" onclick="addToCart(\${p.id})">Añadir al carrito</button>
    </div>
    \`;
  }).join('');
  
  let pageHtml = '';
  for(let i = 1; i <= totalPages; i++) {
    pageHtml += \`<span class="\${i === currentPage ? 'active' : ''}" onclick="goToPage(\${i})">\${i}</span>\`;
  }
  pagination.innerHTML = pageHtml;
}

function goToPage(p) {
  currentPage = p;
  applyFilters();
  window.scrollTo({ top: document.querySelector('.shop-section').offsetTop - 50, behavior: 'smooth' });
}

async function loadProducts() {
  try {
    const res = await fetch('/api/productos');
    const data = await res.json();
    allProducts = data.filter(p => p.estado !== 'Inactivo');
    applyFilters();
  } catch(e) {
    console.log(e);
  }
}
`;

let content = fs.readFileSync('templates/catalogo.html', 'utf8');

// replace HTML
content = content.replace(/<!-- NEW SHOP LAYOUT \(FROM SCREENSHOTS\) -->[\s\S]*?<!-- INSUMOS CAROUSEL -->/, htmlNew + '\n\n  <!-- INSUMOS CAROUSEL -->');

// JS might have different structures, replace renderProducts completely
content = content.replace(/function renderProducts\(products\) \{[\s\S]*?(?=function addToCart)/, jsNew + '\n\n');
content = content.replace(/let currentProductLimit = 8;\n/, '');
content = content.replace(/async function loadProducts\(\) \{[\s\S]*?\}\n/, '');

fs.writeFileSync('templates/catalogo.html', content, 'utf8');
