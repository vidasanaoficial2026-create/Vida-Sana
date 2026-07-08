import os

files = ['templates/tienda.html', 'templates/catalogo.html']

google_script = """  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <script src="https://accounts.google.com/gsi/client" async defer></script>
"""

google_btn = """      <h2>Acceder</h2>
      
      <!-- Google Sign In Button -->
      <div id="g_id_onload"
         data-client_id="REEMPLAZA_ESTO_CON_TU_GOOGLE_CLIENT_ID"
         data-context="signin"
         data-ux_mode="popup"
         data-callback="handleGoogleLogin"
         data-auto_prompt="false">
      </div>
      <div class="g_id_signin"
         data-type="standard"
         data-shape="rectangular"
         data-theme="outline"
         data-text="signin_with"
         data-size="large"
         data-logo_alignment="left"
         style="margin-bottom: 20px; display: flex; justify-content: center;">
      </div>
      
      <div style="text-align:center; font-size:12px; color:#999; margin-bottom:15px;">O inicia sesión con tu correo</div>
      
      <div class="login-field">"""

google_js = """async function handleGoogleLogin(response) {
  try {
    const res = await fetch('/api/google-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential: response.credential })
    });
    if (res.ok) {
      showToast('Inicio de sesión exitoso');
      setTimeout(() => window.location.reload(), 1500);
    } else {
      const data = await res.json();
      showToast(data.error || 'Error con Google');
    }
  } catch(e) {
    showToast('Error de conexión');
  }
}

async function handleLogin() {"""


for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Insert script
        content = content.replace('  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">', google_script)
        
        # Insert button
        content = content.replace('      <h2>Acceder</h2>\n      <div class="login-field">', google_btn)
        
        # Insert JS
        content = content.replace('async function handleLogin() {', google_js)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file} for Google Auth")
