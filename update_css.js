const fs = require('fs');
let content = fs.readFileSync('templates/catalogo.html', 'utf8');

const extraCss = `
  .shop-cats { list-style: none; padding: 0; margin: 0; }
  .shop-cats li { margin-bottom: 8px; }
  .shop-cats li a { color: #555; text-decoration: none; font-size: 15px; display: block; padding: 5px 0; transition: 0.2s; }
  .shop-cats li a:hover { color: #2e7d32; padding-left: 5px; }
  .shop-cats li.active a { color: #2e7d32; font-weight: bold; }
  .shop-pagination { display: flex; justify-content: center; gap: 10px; margin-top: 40px; }
  .shop-pagination span { width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: #f0f0f0; color: #333; cursor: pointer; font-weight: bold; transition: 0.3s; }
  .shop-pagination span:hover { background: #ddd; }
  .shop-pagination span.active { background: #2e7d32; color: #fff; }
`;

content = content.replace('/* NEW SHOP LAYOUT */', '/* NEW SHOP LAYOUT */' + extraCss);
fs.writeFileSync('templates/catalogo.html', content, 'utf8');
