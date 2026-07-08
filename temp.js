
// ─── State ────────────────────────────────────────────────────────────────────
let cart = JSON.parse(localStorage.getItem('vidasana_cart') || '[]');
let allProducts = [];
let cCat = 'all';
let cMin = 0;
let cMax = 1000;
const absMax = 1000;
let cPage = 1;

// ─── Header scroll ────────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const h = document.getElementById('siteHeader');
  if (window.scrollY > 50) h.classList.add('scrolled');
  else h.classList.remove('scrolled');
});

function toggleMobileNav() {
  document.getElementById('mainNav').classList.toggle('open');
}

// ─── API ──────────────────────────────────────────────────────────────────────
async function loadProducts() {
  try {
    const res = await fetch('/api/productos?_=' + Date.now());
    const data = await res.json();
    if (!data.ok) return;
    allProducts = data.productos;
    // Update max price dynamically
    if (allProducts.length) {
      // keep absMax at 1000 unless products exceed it
    }
    applyCatalogFilters();
    updateCounts(data.productos);
  } catch(e) { console.error('Error loading products:', e); }
}

function updateCounts(products) {
  // Future: update category counts if needed
}

// ─── CART ─────────────────────────────────────────────────────────────────────
function addToCart(id) {
  const p = allProducts.find(x => x.id === id);
  if (!p) return;
  if (p.stock <= 0) { showToast('Producto agotado'); return; }
  const exist = cart.find(c => c.id === id);
  const currentQty = exist ? exist.qty : 0;
  if (currentQty >= p.stock) { showToast('Stock máximo alcanzado'); return; }
  if (exist) exist.qty += 1;
  else cart.push({ id: p.id, nombre: p.nombre, precio: p.precio, imagen: p.imagen, qty: 1 });
  updateCart();
  showToast(`${p.nombre} añadido`);
}

function removeFromCart(id) {
  cart = cart.filter(c => c.id !== id);
  updateCart();
}

function changeQty(id, d) {
  const item = cart.find(c => c.id === id);
  if (!item) return;
  item.qty += d;
  if (item.qty <= 0) { removeFromCart(id); return; }
  updateCart();
}

function updateCart() {
  localStorage.setItem('vidasana_cart', JSON.stringify(cart));
  const count = cart.reduce((s, c) => s + c.qty, 0);
  document.getElementById('cartCount').textContent = count;
  renderCart();
}

function renderCart() {
  const el = document.getElementById('cartItems');
  if (!cart.length) {
    el.innerHTML = `<div class="cart-empty"><div class="icon"><i class="fas fa-shopping-bag"></i></div><p>Tu carrito está vacío</p></div>`;
    document.getElementById('cartTotal').textContent = 'S/0.00';
    return;
  }
  el.innerHTML = cart.map(c => `
    <div class="cart-item">
      <div class="cart-item-img">${c.imagen ? `<img src="${c.imagen}" alt="${c.nombre}">` : '<i class="fas fa-leaf"></i>'}</div>
      <div class="cart-item-info">
        <div class="cart-item-name">${c.nombre}</div>
        <div class="cart-item-price">S/${(c.precio * c.qty).toFixed(2)}</div>
      </div>
      <div class="cart-item-qty">
        <button onclick="changeQty(${c.id}, -1)">−</button>
        <span>${c.qty}</span>
        <button onclick="changeQty(${c.id}, 1)">+</button>
      </div>
      <button class="cart-item-remove" onclick="removeFromCart(${c.id})"><i class="fas fa-trash-alt"></i></button>
    </div>
  `).join('');
  const total = cart.reduce((s, c) => s + c.precio * c.qty, 0);
  document.getElementById('cartTotal').textContent = `S/${total.toFixed(2)}`;
}

function toggleCart() {
  document.getElementById('cartOverlay').classList.toggle('open');
  renderCart();
}

function checkout() {
  if (!cart.length) { alert('Carrito vacío'); return; }
  const total = cart.reduce((s, c) => s + c.precio * c.qty, 0);
  let msg = 'Hola, quiero hacer el siguiente pedido:%0A%0A';
  cart.forEach(c => { msg += `• ${c.nombre} x${c.qty} - S/${(c.precio * c.qty).toFixed(2)}%0A`; });
  msg += `%0ATotal: S/${total.toFixed(2)}%0A%0ADatos de entrega:`;
  window.open(`https://wa.me/51951679585?text=${msg}`, '_blank');
}

function showToast(msg) {
  const t = document.getElementById('toastMsg');
  document.getElementById('toastText').textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.getElementById('cartOverlay').classList.remove('open');
});

// ─── SEARCH ───────────────────────────────────────────────────────────────────
function filterProducts(e) {
  if (e && e.type === 'keyup' && e.key !== 'Enter') return;
  const q = document.getElementById('searchInput').value.toLowerCase().trim();
  if (!q) { applyCatalogFilters(); return; }
  const filtered = allProducts.filter(p =>
    p.nombre.toLowerCase().includes(q) ||
    (p.descripcion && p.descripcion.toLowerCase().includes(q))
  );
  renderCatalog(filtered);
}

// ─── CATALOG FILTERS ──────────────────────────────────────────────────────────
window.setCatalogCat = function(el) {
  // Remove active from all
  document.querySelectorAll('#catalogCats a').forEach(a => a.classList.remove('active'));
  el.classList.add('active');
  let text = el.childNodes[0].nodeValue.trim();
  cCat = text;
  cPage = 1;
  applyCatalogFilters();
}

window.resetCat = function(el) {
  document.querySelectorAll('#catalogCats a').forEach(a => a.classList.remove('active'));
  el.classList.add('active');
  cCat = 'all';
  cPage = 1;
  applyCatalogFilters();
}

window.applyCatalogFilters = function() {
  if (!allProducts || allProducts.length === 0) {
    // Show placeholder cards if no products loaded yet
    return;
  }

  let filtered = [...allProducts];

  // Category filter
  if (cCat !== 'all') {
    filtered = filtered.filter(p => p.categoria && p.categoria.toLowerCase().includes(cCat.split(' ')[0].toLowerCase()));
  }

  // Price filter
  filtered = filtered.filter(p => p.precio >= cMin && p.precio <= cMax);

  // Sort
  const sort = document.getElementById('catalogSort').value;
  if (sort === 'low') filtered.sort((a, b) => a.precio - b.precio);
  else if (sort === 'high') filtered.sort((a, b) => b.precio - a.precio);
  else filtered.sort((a, b) => b.id - a.id); // latest

  renderCatalog(filtered);
}

window.renderCatalog = function(products) {
  const grid = document.getElementById('catalogGrid');
  const pag = document.getElementById('catalogPagination');
  if (!grid) return;

  const ITEMS_PER_PAGE = 6;
  const totalPages = Math.ceil(products.length / ITEMS_PER_PAGE) || 1;
  if (cPage > totalPages) cPage = totalPages;
  const toShow = products.slice((cPage - 1) * ITEMS_PER_PAGE, cPage * ITEMS_PER_PAGE);

  if (toShow.length === 0) {
    grid.innerHTML = `<p style="grid-column:1/-1;text-align:center;padding:60px;color:#999;font-size:16px;">
      <i class="fas fa-search" style="font-size:40px;display:block;margin-bottom:15px;color:#ccc;"></i>
      No se encontraron productos con estos filtros.
    </p>`;
    pag.innerHTML = '';
    return;
  }

  grid.innerHTML = toShow.map((p, i) => {
    const isPromo = i % 3 === 2;
    const oldPrice = isPromo ? (p.precio * 1.3).toFixed(2) : null;
    return `
      <div class="shop-card">
        ${isPromo ? '<div class="shop-card-badge">-30%</div>' : ''}
        <img src="${p.imagen}" alt="${p.nombre}" loading="lazy">
        <div class="shop-card-title">${p.nombre}</div>
        <div class="shop-card-price">${oldPrice ? `<strike>S/ ${oldPrice}</strike> ` : ''}S/ ${p.precio.toFixed(2)}</div>
        <div class="shop-card-desc">${(p.descripcion || p.nombre).substring(0, 100)}...</div>
        <button class="shop-card-btn" onclick="addToCart(${p.id})">Añadir al carrito</button>
      </div>
    `;
  }).join('');

  let phtml = '';
  for (let i = 1; i <= totalPages; i++) {
    phtml += `<span class="${i === cPage ? 'active' : ''}" onclick="cPage=${i}; applyCatalogFilters(); window.scrollTo({top: document.querySelector('.shop-section').offsetTop - 50, behavior:'smooth'})">${i}</span>`;
  }
  pag.innerHTML = phtml;
}

window.renderProducts = function(data) {
  applyCatalogFilters();
};

// ─── SLIDER ───────────────────────────────────────────────────────────────────
function initSlider() {
  const wrap = document.getElementById('pWrap');
  if (!wrap) return;
  const bar = document.getElementById('pBar');
  const hL = document.getElementById('pHLeft');
  const hR = document.getElementById('pHRight');
  const iMin = document.getElementById('pMinIn');
  const iMax = document.getElementById('pMaxIn');
  const tipL = document.getElementById('tipL');
  const tipR = document.getElementById('tipR');

  let dragL = false, dragR = false;

  function getX(e) {
    if (e.touches && e.touches.length > 0) return e.touches[0].clientX;
    return e.clientX;
  }

  function updateBar() {
    const leftPct = parseFloat(hL.style.left) || 0;
    const rightPct = parseFloat(hR.style.left) || 100;
    bar.style.left = leftPct + '%';
    bar.style.right = (100 - rightPct) + '%';
  }

  function downL(e) {
    e.preventDefault();
    dragL = true;
    hL.classList.add('active');
  }
  function downR(e) {
    e.preventDefault();
    dragR = true;
    hR.classList.add('active');
  }

  hL.addEventListener('mousedown', downL);
  hL.addEventListener('touchstart', downL, { passive: false });
  hR.addEventListener('mousedown', downR);
  hR.addEventListener('touchstart', downR, { passive: false });

  function stopDrag() {
    if (dragL || dragR) {
      dragL = false;
      dragR = false;
      hL.classList.remove('active');
      hR.classList.remove('active');
      applyCatalogFilters();
    }
  }

  window.addEventListener('mouseup', stopDrag);
  window.addEventListener('touchend', stopDrag);

  function move(e) {
    if (!dragL && !dragR) return;
    e.preventDefault();
    const rect = wrap.getBoundingClientRect();
    let clientX = getX(e);
    let pct = (clientX - rect.left) / rect.width;
    pct = Math.max(0, Math.min(1, pct));

    if (dragL) {
      let rightPct = parseFloat(hR.style.left || '100') / 100;
      if (pct > rightPct - 0.05) pct = rightPct - 0.05;
      const pctPercent = (pct * 100).toFixed(1);
      hL.style.left = pctPercent + '%';
      cMin = Math.round(pct * absMax);
      iMin.value = 'S/ ' + cMin;
      tipL.innerText = 'S/ ' + cMin;
      updateBar();
    }
    if (dragR) {
      let leftPct = parseFloat(hL.style.left || '0') / 100;
      if (pct < leftPct + 0.05) pct = leftPct + 0.05;
      const pctPercent = (pct * 100).toFixed(1);
      hR.style.left = pctPercent + '%';
      cMax = Math.round(pct * absMax);
      iMax.value = 'S/ ' + cMax;
      tipR.innerText = 'S/ ' + cMax;
      updateBar();
    }
  }

  window.addEventListener('mousemove', move);
  window.addEventListener('touchmove', move, { passive: false });

  // Initial positions
  hL.style.left = '0%';
  hR.style.left = '100%';
  bar.style.left = '0%';
  bar.style.right = '0%';
  tipL.innerText = 'S/ 0';
  tipR.innerText = 'S/ ' + absMax;
}

window.updateFromInputs = function() {
  let min = parseFloat(document.getElementById('pMinIn').value.replace(/[^0-9.]/g, '')) || 0;
  let max = parseFloat(document.getElementById('pMaxIn').value.replace(/[^0-9.]/g, '')) || absMax;
  if (min < 0) min = 0;
  if (max > absMax) max = absMax;
  if (min > max) { let t = min; min = max; max = t; }

  cMin = min;
  cMax = max;

  document.getElementById('pMinIn').value = 'S/ ' + min;
  document.getElementById('pMaxIn').value = 'S/ ' + max;

  const hL = document.getElementById('pHLeft');
  const hR = document.getElementById('pHRight');
  const bar = document.getElementById('pBar');

  const leftPct = (cMin / absMax * 100).toFixed(1);
  const rightPct = (cMax / absMax * 100).toFixed(1);

  hL.style.left = leftPct + '%';
  hR.style.left = rightPct + '%';
  bar.style.left = leftPct + '%';
  bar.style.right = (100 - parseFloat(rightPct)) + '%';

  document.getElementById('tipL').innerText = 'S/ ' + cMin;
  document.getElementById('tipR').innerText = 'S/ ' + cMax;

  applyCatalogFilters();
};

// ─── INIT ─────────────────────────────────────────────────────────────────────
updateCart();
initSlider();
loadProducts();

// ─── CENTER-HIGHLIGHT CAROUSELS ───────────────────────────────────────────────
function highlightCenterItem(viewportEl, itemSelector) {
  if (!viewportEl) return;
  const vpRect = viewportEl.getBoundingClientRect();
  const vpCenterX = vpRect.left + vpRect.width / 2;
  const items = viewportEl.querySelectorAll(itemSelector);
  let closestItem = null;
  let closestDist = Infinity;
  items.forEach(item => {
    const rect = item.getBoundingClientRect();
    const itemCenterX = rect.left + rect.width / 2;
    const dist = Math.abs(vpCenterX - itemCenterX);
    if (dist < closestDist) {
      closestDist = dist;
      closestItem = item;
    }
  });
  items.forEach(item => item.classList.remove('is-center'));
  if (closestItem) closestItem.classList.add('is-center');
}

// Run center highlight continuously using rAF
function runCenterHighlight() {
  const insumosVp = document.getElementById('insumosViewport');
  const clientsVp = document.getElementById('clientsViewport');
  highlightCenterItem(insumosVp, '.insumo-item');
  highlightCenterItem(clientsVp, '.client-item');
  requestAnimationFrame(runCenterHighlight);
}
requestAnimationFrame(runCenterHighlight);
