const fs = require('fs');

const originalHtml = `<!-- NEW SHOP LAYOUT (FROM SCREENSHOTS) -->
<div class="shop-section">
  <!-- SIDEBAR -->
  <div class="shop-sidebar">
    <div class="shop-filter-group" style="border-bottom: 2px solid #000; padding-bottom:5px;">
      <select>
        <option>Ordenar por los últimos</option>
        <option>Ordenar por precio: bajo a alto</option>
        <option>Ordenar por precio: alto a bajo</option>
      </select>
    </div>
    
    <div class="shop-filter-group">
      <div class="shop-filter-title">Filtrar por precio</div>
      <div class="price-slider-wrap">
        <div class="price-slider-bar"></div>
        <div class="price-slider-handle left"></div>
        <div class="price-slider-handle right"></div>
      </div>
      <div class="price-inputs">
        <div>
          <input type="text" value="S/ 18" readonly>
          <span>Precio mínimo</span>
        </div>
        <div>
          <input type="text" value="S/ 584" readonly>
          <span>Precio máximo</span>
        </div>
      </div>
    </div>

    <div class="shop-filter-group">
      <ul class="shop-cats">
        <li><a href="#">Aceites</a></li>
        <li><a href="#">Bebidas y concentrados <i class="fas fa-chevron-down" style="color:#ccc; font-size:10px;"></i></a></li>
        <li><a href="#">Cocina Natural <i class="fas fa-chevron-down" style="color:#ccc; font-size:10px;"></i></a></li>
        <li><a href="#">Colágenos</a></li>
        <li><a href="#">Cuidado del cabello</a></li>
        <li><a href="#">Día del Padre</a></li>
        <li><a href="#">Favoritos de la semana</a></li>
        <li><a href="#">Frotaciones</a></li>
        <li><a href="#">Jarabes naturales <i class="fas fa-chevron-down" style="color:#ccc; font-size:10px;"></i></a></li>
        <li><a href="#">Packs <i class="fas fa-chevron-down" style="color:#ccc; font-size:10px;"></i></a></li>
        <li><a href="#">Para el Estómago</a></li>
        <li><a href="#">Para el Sistema Nervioso</a></li>
        <li><a href="#">Para las Defensas</a></li>
        <li><a href="#">Para las Vías Urinarias</a></li>
        <li><a href="#">Para los Huesos</a></li>
        <li><a href="#">Para los Pulmones</a></li>
        <li><a href="#">Peso / Grasa</a></li>
        <li><a href="#">Propóleos</a></li>
        <li><a href="#">Refuerzos <i class="fas fa-chevron-down" style="color:#ccc; font-size:10px;"></i></a></li>
        <li><a href="#">Top Ventas <i class="fas fa-chevron-down" style="color:#ccc; font-size:10px;"></i></a></li>
      </ul>
    </div>
  </div>

  <!-- CONTENT -->
  <div class="shop-content">
    <div class="shop-grid">
      <div class="shop-card">
        <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/1.png" alt="ReZZZet">
        <div class="shop-card-title">ReZZZet</div>
        <div class="shop-card-price">S/ 99.00</div>
        <div class="shop-card-desc">Características Tradicionales ReZZZet es una bebida en polvo que combina magnesio, manzanilla y toronjil peruano para......</div>
        <button class="shop-card-btn">Añadir al carrito</button>
      </div>
      <div class="shop-card">
        <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/2-2.png" alt="EnfoK+">
        <div class="shop-card-title">EnfoK+</div>
        <div class="shop-card-price">S/ 99.00</div>
        <div class="shop-card-desc">Características Tradicionales EnfoK+ es una mezcla en polvo que combina cuatro superalimentos peruanos seleccionados para contribuir......</div>
        <button class="shop-card-btn">Añadir al carrito</button>
      </div>
      <div class="shop-card">
        <div class="shop-card-badge">-30%</div>
        <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/3-2.png" alt="Pack Liviano por Dentro">
        <div class="shop-card-title">PACK LIVIANO POR DENTRO</div>
        <div class="shop-card-price"><strike>S/ 180.00</strike> S/ 126.00</div>
        <div class="shop-card-desc">PACK LIVIANO POR DENTRO Sentirse liviano por dentro no es solo una sensación: es el resultado......</div>
        <button class="shop-card-btn">Añadir al carrito</button>
      </div>
      <div class="shop-card">
        <div class="shop-card-badge">-30%</div>
        <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/4-2.png" alt="Pack Articulaciones">
        <div class="shop-card-title">PACK ARTICULACIONES PRO MARACUYA</div>
        <div class="shop-card-price"><strike>S/ 394.00</strike> S/ 275.80</div>
        <div class="shop-card-desc">PACK ARTICULACIONES PRO MARACUYA Eleva tu bienestar articular con el Pack Articulaciones Pro Maracuya, una selección......</div>
        <button class="shop-card-btn">Añadir al carrito</button>
      </div>
      <div class="shop-card">
        <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/5-2.png" alt="Supertrim 150 GR">
        <div class="shop-card-title">SUPERTRIM 150 GR</div>
        <div class="shop-card-price">S/ 99.00</div>
        <div class="shop-card-desc">Supertrim Santa Natura: tu aliado natural para depurar y sentirte liviano El Supertrim de Santa Natura......</div>
        <button class="shop-card-btn">Añadir al carrito</button>
      </div>
      <div class="shop-card">
        <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/6-2.png" alt="Pack Huesos Sanos">
        <div class="shop-card-title">PACK HUESOS SANOS</div>
        <div class="shop-card-price"><strike>S/ 608.00</strike> S/ 428.00</div>
        <div class="shop-card-desc">Cuida tu estructura ósea de forma completa con el PACK HUESOS SANOS, una poderosa combinación natural......</div>
        <button class="shop-card-btn">Añadir al carrito</button>
      </div>
    </div>
    
    <div class="shop-pagination">
      <span class="active">1</span>
      <span>2</span>
      <span>3</span>
      <span>4</span>
      <span>5</span>
      <span>6</span>
      <span>7</span>
    </div>
  </div>
</div>`;

let content = fs.readFileSync('templates/catalogo.html', 'utf8');

// Replace everything between <!-- NEW SHOP LAYOUT (FROM SCREENSHOTS) --> and <!-- INSUMOS CAROUSEL -->
content = content.replace(/<!-- NEW SHOP LAYOUT \(FROM SCREENSHOTS\) -->[\s\S]*?<!-- INSUMOS CAROUSEL -->/, originalHtml + '\n\n<!-- INSUMOS CAROUSEL -->');

// Also, the JavaScript I added for filtering might break the layout or throw errors if the IDs don't match, or they don't want it.
// The user wants it exactly "como antes". Before, there was no JS for this specific layout, just the old renderProducts which was deleted in catalogo.
// I will just leave the JS out or restore the old JS block.
// To be safe, I'll remove my new JS block.
content = content.replace(/let currentFilterCat = 'all';[\s\S]*?(?=function addToCart)/, '');

fs.writeFileSync('templates/catalogo.html', content, 'utf8');
