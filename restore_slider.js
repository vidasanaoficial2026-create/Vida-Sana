const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

// Remove noUiSlider links
html = html.replace(/<link rel="stylesheet"[^>]*nouislider[^>]*>\s*/i, '');
html = html.replace(/<script src="[^"]*nouislider[^"]*"><\/script>\s*/i, '');
html = html.replace(/<style>[\s\S]*?\.noUi-[^<]*<\/style>\s*/, '');

// Restore the custom slider HTML
const oldSliderHTML = `
        <div class="price-slider-wrap" id="pWrap">
          <div class="price-slider-bar" id="pBar"></div>
          <div class="price-slider-handle left" id="pHLeft"><div class="slider-tooltip" id="tipL">S/ 0</div></div>
          <div class="price-slider-handle right" id="pHRight"><div class="slider-tooltip" id="tipR">S/ 500</div></div>
        </div>
        <div class="price-inputs">
          <input type="text" id="pMinIn" value="S/ 0" onchange="updateFromInputs()">
          <input type="text" id="pMaxIn" value="S/ 1000" onchange="updateFromInputs()">
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:5px; font-size:12px; color:#666;">
          <span>Precio mnimo</span>
          <span>Precio mximo</span>
        </div>
`;

// Find where to put it
const startDiv = html.indexOf('<div id="priceSlider"></div>');
if (startDiv !== -1) {
    const endDiv = startDiv + '<div id="priceSlider"></div>'.length;
    html = html.substring(0, startDiv) + oldSliderHTML + html.substring(endDiv);
} else {
    console.log("Could not find priceSlider div to replace.");
}

// Restore the custom JS logic
const startInit = html.indexOf('function initSlider() {');
const endInit = html.indexOf('window.applyCatalogFilters = function() {');

if (startInit !== -1 && endInit !== -1) {
    const customSliderInit = `function initSlider() {
  const wrap = document.getElementById('pWrap');
  if(!wrap) return;
  const bar = document.getElementById('pBar');
  const hL = document.getElementById('pHLeft');
  const hR = document.getElementById('pHRight');
  const iMin = document.getElementById('pMinIn');
  const iMax = document.getElementById('pMaxIn');
  
  let dragL = false, dragR = false;
  
  function getX(e) {
    if(e.touches && e.touches.length > 0) return e.touches[0].clientX;
    return e.clientX;
  }
  
  function downL(e) { e.preventDefault(); dragL = true; hL.classList.add('active'); }
  function downR(e) { e.preventDefault(); dragR = true; hR.classList.add('active'); }
  
  hL.addEventListener('mousedown', downL);
  hL.addEventListener('touchstart', downL, {passive: false});
  hR.addEventListener('mousedown', downR);
  hR.addEventListener('touchstart', downR, {passive: false});
  
  function stopDrag() {
    if(dragL || dragR) {
      dragL = false; dragR = false; hL.classList.remove('active'); hR.classList.remove('active');
      applyCatalogFilters();
    }
  }
  
  window.addEventListener('mouseup', stopDrag);
  window.addEventListener('touchend', stopDrag);
  
  function move(e) {
    if(!dragL && !dragR) return;
    const rect = wrap.getBoundingClientRect();
    let clientX = getX(e);
    let pct = (clientX - rect.left) / rect.width;
    pct = Math.max(0, Math.min(1, pct));
    
    if(dragL) {
      let maxPct = parseFloat(hR.style.left || '100%') / 100;
      if(pct > maxPct - 0.05) pct = maxPct - 0.05;
      hL.style.left = (pct * 100) + '%';
      bar.style.left = (pct * 100) + '%';
      cMin = Math.round(pct * absMax);
      iMin.value = 'S/ ' + cMin;
      document.getElementById('tipL').innerText = 'S/ ' + cMin;
    }
    if(dragR) {
      let minPct = parseFloat(hL.style.left || '0%') / 100;
      if(pct < minPct + 0.05) pct = minPct + 0.05;
      hR.style.left = (pct * 100) + '%';
      bar.style.right = (100 - (pct * 100)) + '%';
      cMax = Math.round(pct * absMax);
      iMax.value = 'S/ ' + cMax;
      document.getElementById('tipR').innerText = 'S/ ' + cMax;
    }
  }
  
  window.addEventListener('mousemove', move);
  window.addEventListener('touchmove', move, {passive: false});
  
  hL.style.left = '0%'; bar.style.left = '0%'; hR.style.left = '100%'; bar.style.right = '0%';
  if(document.getElementById('tipL')) document.getElementById('tipL').innerText = 'S/ ' + cMin;
  if(document.getElementById('tipR')) document.getElementById('tipR').innerText = 'S/ ' + cMax;
}

window.updateFromInputs = function() {
  let min = parseFloat(document.getElementById('pMinIn').value.replace(/[^0-9.]/g, '')) || 0;
  let max = parseFloat(document.getElementById('pMaxIn').value.replace(/[^0-9.]/g, '')) || 1000;
  if(min < 0) min = 0; if(max > absMax) max = absMax;
  if(min > max) { let temp = min; min = max; max = temp; }
  
  cMin = min; cMax = max;
  document.getElementById('pMinIn').value = 'S/ ' + min;
  document.getElementById('pMaxIn').value = 'S/ ' + max;
  
  const hL = document.getElementById('pHLeft'); const hR = document.getElementById('pHRight'); const bar = document.getElementById('pBar');
  hL.style.left = (cMin / absMax * 100) + '%'; bar.style.left = (cMin / absMax * 100) + '%';
  hR.style.left = (cMax / absMax * 100) + '%'; bar.style.right = (100 - (cMax / absMax * 100)) + '%';
  
  if(document.getElementById('tipL')) document.getElementById('tipL').innerText = 'S/ ' + cMin;
  if(document.getElementById('tipR')) document.getElementById('tipR').innerText = 'S/ ' + cMax;
  
  applyCatalogFilters();
};

`;
    html = html.substring(0, startInit) + customSliderInit + html.substring(endInit);
} else {
    console.log("Could not find initSlider to replace.");
}

// Add the tooltip CSS if it's missing
if (!html.includes('.slider-tooltip')) {
  const tooltipCss = `
  .slider-tooltip {
    position: absolute;
    top: -35px;
    left: 50%;
    transform: translateX(-50%);
    background: #111;
    color: #fff;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }
  .price-slider-handle:hover .slider-tooltip,
  .price-slider-handle.active .slider-tooltip {
    opacity: 1;
  }
`;
  html = html.replace('</style>', tooltipCss + '\n</style>');
}

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log('Restored custom slider');
