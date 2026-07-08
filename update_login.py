import os

files_to_update = ['templates/tienda.html', 'templates/catalogo.html']

old_login_func = """function handleLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pw    = document.getElementById('loginPassword').value.trim();
  if (!email || !pw) { showToast('Por favor completa todos los campos'); return; }
  showToast('Inicio de sesión próximamente');
}"""

new_login_func = """async function handleLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pw    = document.getElementById('loginPassword').value.trim();
  if (!email || !pw) { showToast('Por favor completa todos los campos'); return; }
  
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: email, password: pw })
    });
    
    if (res.ok) {
      showToast('Inicio de sesión exitoso');
      setTimeout(() => window.location.reload(), 1500);
    } else {
      const data = await res.json();
      showToast(data.error || 'Credenciales inválidas');
    }
  } catch(e) {
    showToast('Error de conexión');
  }
}"""

for file in files_to_update:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace(old_login_func, new_login_func)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file}")
