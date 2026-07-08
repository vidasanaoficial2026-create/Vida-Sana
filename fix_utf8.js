const fs = require('fs');

const replacements = {
  'Colǟgenos': 'Colágenos',
  'Propǟleos': 'Propóleos',
  'Estmago': 'Estómago',
  'vas': 'vías',
  'Cǭpsulas': 'Cápsulas',
  'VER M?S': 'VER MÁS',
  'Frmula': 'Fórmula',
  'orgǭnicos': 'orgánicos',
  'energa': 'energía',
  'ǧnicas': 'únicas',
  'C?PSULAS': 'CÁPSULAS',
  'mǭs': 'más',
  'tradicin': 'tradición',
  'corazn': 'corazón',
  'Perǧ': 'Perú',
  'Sguenos': 'Síguenos',
  'Contǭctanos': 'Contáctanos',
  'Direccin': 'Dirección',
  'Informacin': 'Información',
  'Categoras': 'Categorías',
  'mǭximo': 'máximo',
  'aadido': 'añadido',
  'estǭ': 'está',
  'vaco': 'vacío',
  'informacin': 'información'
};

const files = ['templates/tienda.html', 'templates/catalogo.html'];

files.forEach(file => {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf8');
    
    // Fallback: replace using buffer search if characters are too weird
    // But let's try direct string replace first
    for (const [bad, good] of Object.entries(replacements)) {
      content = content.split(bad).join(good);
    }
    
    fs.writeFileSync(file, content, 'utf8');
    console.log('Fixed ' + file);
  }
});
