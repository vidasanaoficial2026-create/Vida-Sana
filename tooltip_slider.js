const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

// Move slider down
html = html.replace('.price-slider-wrap {\n    position: relative;\n    height: 4px;\n    background: #ddd;\n    margin-bottom: 20px;\n  }', 
`.price-slider-wrap {
    position: relative;
    height: 4px;
    background: #ddd;
    margin-top: 30px;
    margin-bottom: 30px;
  }`);
  
// Add tooltips to handles
html = html.replace('<div class="price-slider-handle left" id="pHLeft"></div>', '<div class="price-slider-handle left" id="pHLeft"><div class="slider-tooltip" id="tipL">S/ 0</div></div>');
html = html.replace('<div class="price-slider-handle right" id="pHRight"></div>', '<div class="price-slider-handle right" id="pHRight"><div class="slider-tooltip" id="tipR">S/ 500</div></div>');

// Add tooltip CSS
const tooltipCss = `
  .slider-tooltip {
    position: absolute;
    top: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: #111;
    color: #fff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
  }
  .price-slider-handle:hover .slider-tooltip,
  .price-slider-handle.active .slider-tooltip {
    opacity: 1;
  }
`;
html = html.replace('</style>', tooltipCss + '\n</style>');

// Update JS to update tooltips and add .active class
const jsReplace = `
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
`;

html = html.replace(/if\(dragL\) \{[\s\S]*?iMax\.value = 'S\/ ' \+ cMax;\n    \}/, jsReplace);

// Also add active class
html = html.replace('function downL(e) { e.preventDefault(); dragL = true; }', "function downL(e) { e.preventDefault(); dragL = true; hL.classList.add('active'); }");
html = html.replace('function downR(e) { e.preventDefault(); dragR = true; }', "function downR(e) { e.preventDefault(); dragR = true; hR.classList.add('active'); }");
html = html.replace('dragL = false; dragR = false;', "dragL = false; dragR = false; hL.classList.remove('active'); hR.classList.remove('active');");

// Set initial tooltips in initSlider
html = html.replace("hR.style.left = '100%';", "hR.style.left = '100%';\n  if(document.getElementById('tipL')) document.getElementById('tipL').innerText = 'S/ ' + cMin;\n  if(document.getElementById('tipR')) document.getElementById('tipR').innerText = 'S/ ' + cMax;");

// Update from inputs
const updateInputsReplace = `
  hR.style.left = (cMax / absMax * 100) + '%';
  bar.style.right = (100 - (cMax / absMax * 100)) + '%';
  
  if(document.getElementById('tipL')) document.getElementById('tipL').innerText = 'S/ ' + cMin;
  if(document.getElementById('tipR')) document.getElementById('tipR').innerText = 'S/ ' + cMax;
  
  applyCatalogFilters();
`;
html = html.replace(/hR\.style\.left = \(cMax \/ absMax \* 100\) \+ '%';[\s\S]*?applyCatalogFilters\(\);/, updateInputsReplace);

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log('done');
