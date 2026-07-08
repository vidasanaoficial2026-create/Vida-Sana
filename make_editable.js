const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

// Remove readonly
html = html.replace('readonly>', 'onchange="updateFromInputs()">');
html = html.replace('readonly>', 'onchange="updateFromInputs()">');

// Inject the updateFromInputs function
const jsAdd = `
window.updateFromInputs = function() {
  let min = parseFloat(document.getElementById('pMinIn').value.replace(/[^0-9.]/g, '')) || 0;
  let max = parseFloat(document.getElementById('pMaxIn').value.replace(/[^0-9.]/g, '')) || 1000;
  if(min < 0) min = 0;
  if(max > absMax) max = absMax;
  if(min > max) { let temp = min; min = max; max = temp; }
  
  cMin = min;
  cMax = max;
  
  document.getElementById('pMinIn').value = 'S/ ' + min;
  document.getElementById('pMaxIn').value = 'S/ ' + max;
  
  // update slider visuals
  const hL = document.getElementById('pHLeft');
  const hR = document.getElementById('pHRight');
  const bar = document.getElementById('pBar');
  
  hL.style.left = (cMin / absMax * 100) + '%';
  bar.style.left = (cMin / absMax * 100) + '%';
  
  hR.style.left = (cMax / absMax * 100) + '%';
  bar.style.right = (100 - (cMax / absMax * 100)) + '%';
  
  applyCatalogFilters();
}
`;

html = html.replace('document.addEventListener(', jsAdd + '\ndocument.addEventListener(');

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log('done');
