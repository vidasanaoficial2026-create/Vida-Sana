import os
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    replacements = {
        'CÃ¡psulas': 'Cápsulas',
        'Copsulas': 'Cápsulas',
        'C?PSULAS': 'CÁPSULAS',
        'CÃ\x81PSULAS': 'CÁPSULAS',
        'VER MÃ\x81S': 'VER MÁS',
        'VER MÃ S': 'VER MÁS',
        'VER M?S': 'VER MÁS',
        'MÃ\x81S VENDIDOS': 'MÁS VENDIDOS',
        'MÃ S VENDIDOS': 'MÁS VENDIDOS',
        'M?S VENDIDOS': 'MÁS VENDIDOS',
        'aÃ±adido': 'añadido',
        'aadido': 'añadido',
        'informaciÃ³n': 'información',
        'informacin': 'información',
        'vacÃ\xado': 'vacío',
        'vaco': 'vacío',
        'mÃ¡ximo': 'máximo',
        'moximo': 'máximo',
        'DesintÃ³xicate': 'Desintoxícate',
        'Desintxicate': 'Desintoxícate',
        'Articulaciones': 'Articulaciones',
        'AÃ±adir': 'Añadir',
        'Aadir': 'Añadir'
    }

    original_content = content
    for k, v in replacements.items():
        content = content.replace(k, v)

    # Let's also do a generic decode if we find 'Ã'
    # Actually, better stick to specific replacements to avoid breaking things.

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")

for f in glob.glob('templates/*.html'):
    fix_file(f)
