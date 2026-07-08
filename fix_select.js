const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

const selectCss = `
  .shop-filter-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
  }
`;

if (!html.includes('.shop-filter-group select')) {
    html = html.replace('</style>', selectCss + '\n</style>');
    fs.writeFileSync('templates/catalogo.html', html, 'utf8');
    console.log('Select CSS added');
}
