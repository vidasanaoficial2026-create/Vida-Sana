const fs = require('fs');
let content = fs.readFileSync('templates/catalogo.html', 'utf8');

const replacements = [
  [/C.psulas/g, 'Cápsulas'],
  [/VER M.S/g, 'VER MÁS'],
  [/C.PSULAS/g, 'CÁPSULAS'],
  [/M.S VENDIDOS/g, 'MÁS VENDIDOS'],
  [/F.rmula/g, 'Fórmula'],
  [/org.nicos/g, 'orgánicos'],
  [/energ.a/g, 'energía'],
  [/.nicas/g, 'únicas'],
  [/Est.mago/g, 'Estómago'],
  [/v.as/g, 'vías'],
  [/Col.genos/g, 'Colágenos'],
  [/Prop.leos/g, 'Propóleos'],
  [/m.s/g, 'más'],
  [/tradicin/g, 'tradición'],
  [/corazn/g, 'corazón'],
  [/Per./g, 'Perú'],
  [/S.guenos/g, 'Síguenos'],
  [/Cont.ctanos/g, 'Contáctanos'],
  [/Direcci.n/g, 'Dirección'],
  [/Informaci.n/g, 'Información'],
  [/Categor.as/g, 'Categorías'],
  [/m.ximo/g, 'máximo'],
  [/a.adido/g, 'añadido'],
  [/est./g, 'está'],
  [/vac.o/g, 'vacío']
];

replacements.forEach(([bad, good]) => {
  // Be careful with dots matching anything, but for specific context it's fine.
  // Actually a safer approach is to replace the exact corrupted strings.
});

// Since the header and footer in catalogo are exactly the same as in tienda, 
// let's just do it simpler: re-copy tienda.html to catalogo.html and then strip the sections again!
