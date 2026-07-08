const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

const newInitSlider = `function initSlider() {
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
  
  function downL(e) { e.preventDefault(); dragL = true; }
  function downR(e) { e.preventDefault(); dragR = true; }
  
  hL.addEventListener('mousedown', downL);
  hL.addEventListener('touchstart', downL, {passive: false});
  hR.addEventListener('mousedown', downR);
  hR.addEventListener('touchstart', downR, {passive: false});
  
  function stopDrag() {
    if(dragL || dragR) {
      dragL = false; dragR = false;
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
    }
    if(dragR) {
      let minPct = parseFloat(hL.style.left || '0%') / 100;
      if(pct < minPct + 0.05) pct = minPct + 0.05;
      hR.style.left = (pct * 100) + '%';
      bar.style.right = (100 - (pct * 100)) + '%';
      cMax = Math.round(pct * absMax);
      iMax.value = 'S/ ' + cMax;
    }
  }
  
  window.addEventListener('mousemove', move);
  window.addEventListener('touchmove', move, {passive: false});
  
  hL.style.left = '0%';
  bar.style.left = '0%';
  hR.style.left = '100%';
  bar.style.right = '0%';
}`;

// Replace the old initSlider function
html = html.replace(/function initSlider\(\) \{[\s\S]*?hR\.style\.left = '100%';\s*bar\.style\.right = '0%';\s*\}/, newInitSlider);

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log('done');
