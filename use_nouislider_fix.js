const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

const cdnLinks = `
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.css" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.js"></script>
<style>
  .noUi-connect { background: #008000; }
  .noUi-horizontal { height: 4px; margin-top: 40px; margin-bottom: 50px; }
  .noUi-handle { border-radius: 50%; background: #fff; border: 2px solid #000; box-shadow: none; cursor: grab; }
  .noUi-handle:active { cursor: grabbing; }
  .noUi-horizontal .noUi-handle { width: 24px; height: 24px; right: -12px; top: -10px; }
  .noUi-handle:before, .noUi-handle:after { display: none; }
  .noUi-tooltip { background: #111; color: #fff; border: none; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 2px 6px; }
</style>
`;

if (!html.includes('nouislider.min.css')) {
  html = html.replace('</head>', cdnLinks + '\n</head>');
}

// Manually replace the slider div
const startDiv = html.indexOf('<div class="price-slider-wrap"');
const endDiv = html.indexOf('<div class="price-inputs">');
if (startDiv !== -1 && endDiv !== -1) {
    html = html.substring(0, startDiv) + '<div id="priceSlider"></div>\n        ' + html.substring(endDiv);
}

// Manually replace initSlider
const startInit = html.indexOf('function initSlider() {');
const endInit = html.indexOf('window.applyCatalogFilters = function() {');
if (startInit !== -1 && endInit !== -1) {
    const noUiSliderInit = `function initSlider() {
  const slider = document.getElementById('priceSlider');
  if(!slider) return;
  const iMin = document.getElementById('pMinIn');
  const iMax = document.getElementById('pMaxIn');
  
  if (slider.noUiSlider) { slider.noUiSlider.destroy(); }
  
  noUiSlider.create(slider, {
    start: [cMin, cMax], connect: true,
    range: { 'min': 0, 'max': 1000 },
    step: 10,
    tooltips: [ { to: function(v) { return 'S/ ' + Math.round(v); } }, { to: function(v) { return 'S/ ' + Math.round(v); } } ]
  });
  
  slider.noUiSlider.on('slide', function(values, handle) {
    if(handle === 0) { cMin = Math.round(values[0]); iMin.value = 'S/ ' + cMin; } 
    else { cMax = Math.round(values[1]); iMax.value = 'S/ ' + cMax; }
  });
  
  slider.noUiSlider.on('change', function() { applyCatalogFilters(); });
  
  window.updateFromInputs = function() {
    let min = parseFloat(iMin.value.replace(/[^0-9.]/g, '')) || 0;
    let max = parseFloat(iMax.value.replace(/[^0-9.]/g, '')) || 1000;
    if(min < 0) min = 0;
    if(max > 1000) max = 1000;
    if(min > max) { let temp = min; min = max; max = temp; }
    cMin = min; cMax = max;
    iMin.value = 'S/ ' + min; iMax.value = 'S/ ' + max;
    slider.noUiSlider.set([cMin, cMax]);
    applyCatalogFilters();
  };
}\n\n`;
    html = html.substring(0, startInit) + noUiSliderInit + html.substring(endInit);
}

// Fix the "Ordenar" margin so it's super obvious
html = html.replace('.shop-filter-group {\n    margin-bottom: 35px;\n  }', '.shop-filter-group {\n    margin-bottom: 70px;\n  }');

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log('Done!');
