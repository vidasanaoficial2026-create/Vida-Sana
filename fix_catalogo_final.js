const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

// Fix double border on select
html = html.replace('style="border-bottom: 2px solid #000; padding-bottom:5px;"', 'style="margin-bottom: 50px;"');

// Remove DOMContentLoaded for initSlider, just call it directly
html = html.replace(/document\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{\s*initSlider\(\);\s*\}\);/, 'initSlider();');
html = html.replace(/document\.addEventListener\([\s\S]*?initSlider\(\);\s*\}\);/, 'initSlider();');

// Also just in case, call initSlider() at the very end of the script block
if (!html.includes('initSlider();\n</script>')) {
  html = html.replace('</script>', 'initSlider();\n</script>');
}

fs.writeFileSync('templates/catalogo.html', html, 'utf8');
console.log("Fixed catalogo");
