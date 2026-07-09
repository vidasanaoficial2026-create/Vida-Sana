import os

file = 'templates/admin_productos.html'

old_select = """        <select id="fCategoria">
          <option value="Bebidas">Bebidas</option>
          <option value="Capsulas">Cápsulas</option>
          <option value="Harinas">Harinas</option>
          <option value="Otros">Otros</option>
        </select>"""

new_select = """        <select id="fCategoria">
          <option value="Bebidas">Bebidas</option>
          <option value="Capsulas">Cápsulas</option>
          <option value="Extractos">Extractos</option>
          <option value="Nutrientes">Nutrientes</option>
          <option value="Vitaminas">Vitaminas</option>
          <option value="Gomitas">Gomitas</option>
          <option value="Harinas">Harinas</option>
          <option value="Aceites">Aceites</option>
          <option value="Colágenos">Colágenos</option>
          <option value="Frotaciones">Frotaciones</option>
          <option value="Jarabes">Jarabes</option>
          <option value="Propóleos">Propóleos</option>
          <option value="Packs">Packs</option>
          <option value="Otros">Otros</option>
        </select>"""

if os.path.exists(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Let's do a more robust replace in case the encoding caused 'Cápsulas' to fail matching
    # We will just split at `<select id="fCategoria">` and `</select>`
    
    start_tag = '<select id="fCategoria">'
    end_tag = '</select>'
    
    if start_tag in content and end_tag in content:
        start_idx = content.find(start_tag)
        end_idx = content.find(end_tag, start_idx) + len(end_tag)
        
        content = content[:start_idx] + new_select + content[end_idx:]
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated categories in admin_productos.html")
    else:
        print("Could not find select tags")
