with open('templates/tienda.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Append script to open cart if URL has open_cart=1
script_addition = """
<script>
  window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('open_cart') === '1') {
      setTimeout(() => {
        const overlay = document.getElementById('cartOverlay');
        if (overlay) {
          overlay.classList.add('open');
          renderCart();
        }
      }, 500); // small delay to allow products and cart to load
    }
  });
</script>
</body>
"""

content = content.replace("</body>", script_addition)

with open('templates/tienda.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("tienda.html updated with open_cart logic")
