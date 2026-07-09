import os

file = 'server.py'

if os.path.exists(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We replace the bad query logic with the correct one
    bad_logic = 'query += " AND categoria COLLATE NOCASE = ?"'
    good_logic = 'query += " AND categoria = ?"'
    
    if bad_logic in content:
        content = content.replace(bad_logic, good_logic)
        
        # Also, PostgreSQL uses ILIKE instead of LIKE for case-insensitivity,
        # but since we use SQLiteEmulator, it replaces ? with %s. 
        # Let's just change LIKE to ILIKE if it's Postgres. But wait, we can just keep LIKE for 'q' since we lower() it or just let it be.
        # Actually, let's just fix the category error which is the main crasher.
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed query syntax error in server.py")
    else:
        print("bad logic not found")
