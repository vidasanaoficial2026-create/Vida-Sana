const fs = require('fs');
let html = fs.readFileSync('templates/catalogo.html', 'utf8');

const sliderCss = `
  /* CUSTOM SLIDER CSS */
  .price-slider-wrap {
    position: relative;
    height: 4px;
    background: #e0e0e0;
    border-radius: 2px;
    margin: 35px 0 25px;
  }
  .price-slider-bar {
    position: absolute;
    left: 0; right: 0;
    top: 0; bottom: 0;
    background: #008000;
  }
  .price-slider-handle {
    width: 22px; height: 22px;
    background: #fff;
    border: 2px solid #111;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    cursor: grab;
    z-index: 2;
  }
  .price-slider-handle:active {
    cursor: grabbing;
  }
  .price-slider-handle.left { left: 0; }
  .price-slider-handle.right { right: 0; }
  .price-inputs {
    display: flex;
    justify-content: space-between;
    gap: 15px;
  }
  .price-inputs input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    text-align: center;
    font-size: 14px;
  }
`;

if (!html.includes('.price-slider-wrap {')) {
    html = html.replace('</style>', sliderCss + '\n</style>');
    fs.writeFileSync('templates/catalogo.html', html, 'utf8');
    console.log('CSS restored');
} else {
    console.log('CSS already exists');
}
