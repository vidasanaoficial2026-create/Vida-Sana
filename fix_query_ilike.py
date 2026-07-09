import os

file = 'server.py'

if os.path.exists(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We replace LIKE with ILIKE for Postgres
    bad_logic = 'query += " AND (nombre LIKE ? OR descripcion LIKE ?)"'
    good_logic = 'query += " AND (nombre ILIKE ? OR descripcion ILIKE ?)"'
    
    if bad_logic in content:
        content = content.replace(bad_logic, good_logic)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed ILIKE query syntax in server.py")
    else:
        print("bad logic not found")
