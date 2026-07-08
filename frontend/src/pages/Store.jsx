import { useState, useEffect } from 'react'
import { api } from '../api'

function useCart() {
  const [cart, setCart] = useState(() => JSON.parse(localStorage.getItem('vid_sana_cart') || '[]'))

  useEffect(() => {
    const handler = () => setCart(JSON.parse(localStorage.getItem('vid_sana_cart') || '[]'))
    window.addEventListener('cart-update', handler)
    return () => window.removeEventListener('cart-update', handler)
  }, [])

  const save = (newCart) => {
    setCart(newCart)
    localStorage.setItem('vid_sana_cart', JSON.stringify(newCart))
    window.dispatchEvent(new Event('cart-update'))
  }

  const add = (p) => {
    if (p.stock <= 0) return alert('Producto agotado')
    const exist = cart.find(c => c.id === p.id)
    const qty = exist ? exist.qty : 0
    if (qty >= p.stock) return alert('Stock máximo alcanzado')
    if (exist) exist.qty += 1
    else cart.push({ id: p.id, nombre: p.nombre, precio: p.precio, qty: 1 })
    save([...cart])
    showToast(`${p.nombre} añadido`)
  }

  const changeQty = (id, d) => {
    const item = cart.find(c => c.id === id)
    if (!item) return
    item.qty += d
    if (item.qty <= 0) {
      const filtered = cart.filter(c => c.id !== id)
      save(filtered)
    } else {
      save([...cart])
    }
  }

  const remove = (id) => save(cart.filter(c => c.id !== id))

  const total = cart.reduce((s, c) => s + c.precio * c.qty, 0)
  const count = cart.reduce((s, c) => s + c.qty, 0)

  const checkout = () => {
    if (!cart.length) return alert('Carrito vacío')
    let msg = 'Hola, quiero hacer el siguiente pedido:%0A%0A'
    cart.forEach(c => { msg += `• ${c.nombre} x${c.qty} - S/${(c.precio * c.qty).toFixed(2)}%0A` })
    msg += `%0ATotal: S/${total.toFixed(2)}%0A%0ADatos de entrega:`
    window.open(`https://wa.me/51951679585?text=${msg}`, '_blank')
  }

  return { cart, count, total, add, changeQty, remove, checkout }
}

function showToast(msg) {
  const el = document.getElementById('toast')
  if (!el) return
  const span = document.getElementById('toastText')
  if (span) span.textContent = msg
  el.classList.remove('opacity-0', 'translate-y-4')
  el.classList.add('opacity-100', 'translate-y-0')
  setTimeout(() => {
    el.classList.remove('opacity-100', 'translate-y-0')
    el.classList.add('opacity-0', 'translate-y-4')
  }, 2000)
}

export default function Store() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [search, setSearch] = useState('')
  const [cartOpen, setCartOpen] = useState(false)
  const { cart, count, total, add, changeQty, remove, checkout } = useCart()

  useEffect(() => {
    const params = {}
    if (filter) params.categoria = filter
    if (search) params.q = search
    api.productos.list(params).then(data => {
      setProducts(data.productos)
    }).catch(console.error).finally(() => setLoading(false))
  }, [filter, search])

  const handleSearch = (e) => {
    if (e.key === 'Enter') setSearch(e.target.value.trim())
  }

  const whatsappProduct = (p) => {
    window.open(`https://wa.me/51951679585?text=${encodeURIComponent(`Hola, quiero información sobre ${p.nombre} (S/${p.precio.toFixed(2)})`)}`, '_blank')
  }

  const categories = ['Todas', ...new Set(products.map(p => p.categoria).filter(Boolean))]

  return (
    <div className="pt-24 min-h-screen bg-gray-50">
      {/* TOAST */}
      <div id="toast" className="fixed bottom-24 right-5 z-50 bg-green-700 text-white px-5 py-3 rounded-xl font-semibold text-sm shadow-lg flex items-center gap-2 opacity-0 translate-y-4 transition-all duration-300">
        <i className="fas fa-check-circle" /> <span id="toastText" />
      </div>

      <div className="max-w-6xl mx-auto px-6">
        {/* HEADER */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900">Tienda</h1>
            <p className="text-sm text-gray-400">{products.length} productos disponibles</p>
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <input type="text" placeholder="Buscar productos..."
              onKeyDown={handleSearch}
              className="flex-1 sm:w-52 px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white" />
            <button onClick={() => setCartOpen(true)} className="relative bg-white border border-gray-200 px-4 py-2.5 rounded-xl hover:border-green-500 transition-all">
              <i className="fas fa-shopping-cart text-gray-600" />
              {count > 0 && <span className="absolute -top-1.5 -right-1.5 bg-gold text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">{count}</span>}
            </button>
          </div>
        </div>

        {/* CATEGORIES */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
          {categories.map(cat => (
            <button key={cat}
              onClick={() => setFilter(cat === 'Todas' ? '' : cat)}
              className={`whitespace-nowrap px-5 py-2 rounded-full text-sm font-semibold transition-all ${
                (cat === 'Todas' && !filter) || filter === cat
                  ? 'bg-green-700 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:border-green-500'
              }`}>
              {cat}
            </button>
          ))}
        </div>

        {/* PRODUCTS */}
        {loading ? (
          <div className="text-center py-20 text-gray-400">
            <div className="inline-block w-8 h-8 border-2 border-green-100 border-t-green-700 rounded-full animate-spin" />
            <p className="mt-3 text-sm">Cargando...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <i className="fas fa-box-open text-4xl mb-3" />
            <p>No se encontraron productos</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 pb-16">
            {products.map(p => {
              const out = p.stock <= 0
              return (
                <div key={p.id} className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md hover:-translate-y-1 transition-all duration-300">
                  <div className="h-48 bg-cream flex items-center justify-center p-5">
                    {p.imagen
                      ? <img src={p.imagen} alt={p.nombre} className="max-h-full max-w-full object-contain hover:scale-105 transition-transform duration-500" loading="lazy" />
                      : <i className="fas fa-leaf text-4xl text-gray-300" />}
                  </div>
                  <div className="p-4">
                    <p className="text-[10px] font-bold uppercase tracking-widest text-green-500 mb-1">{p.categoria}</p>
                    <h3 className="font-bold text-gray-800 text-sm mb-1">{p.nombre}</h3>
                    <p className="text-xl font-extrabold text-green-700 mb-3">S/ {p.precio.toFixed(2)}</p>
                    <p className="text-xs mb-3">
                      {out
                        ? <span className="text-red-500 font-bold">SIN STOCK</span>
                        : <span className="text-green-600">Stock: {p.stock}</span>}
                    </p>
                    <div className="flex gap-2">
                      <button onClick={() => add(p)} disabled={out}
                        className="flex-1 bg-green-700 text-white py-2.5 px-3 rounded-xl font-semibold text-xs hover:bg-green-900 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-1.5">
                        <i className={`fas ${out ? 'fa-times-circle' : 'fa-cart-plus'}`} /> {out ? 'AGOTADO' : 'AÑADIR'}
                      </button>
                      <button onClick={() => whatsappProduct(p)}
                        className="w-10 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-all flex items-center justify-center">
                        <i className="fab fa-whatsapp" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* CART MODAL */}
      {cartOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setCartOpen(false)}>
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[80vh] overflow-y-auto shadow-2xl p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-xl font-extrabold text-gray-900"><i className="fas fa-shopping-cart mr-2" />Carrito</h2>
              <button onClick={() => setCartOpen(false)} className="text-gray-400 hover:text-gray-600 text-xl"><i className="fas fa-times" /></button>
            </div>
            {cart.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <i className="fas fa-shopping-bag text-4xl mb-3" />
                <p>Tu carrito está vacío</p>
              </div>
            ) : (
              <>
                <div className="space-y-3 mb-4">
                  {cart.map(item => (
                    <div key={item.id} className="flex items-center gap-3 pb-3 border-b border-gray-100">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm text-gray-800 truncate">{item.nombre}</p>
                        <p className="text-xs font-bold text-green-700">S/ {(item.precio * item.qty).toFixed(2)}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button onClick={() => changeQty(item.id, -1)} className="w-7 h-7 border border-gray-300 rounded-lg font-bold text-sm hover:border-green-500 hover:text-green-700 transition-all">−</button>
                        <span className="font-bold text-sm w-5 text-center">{item.qty}</span>
                        <button onClick={() => changeQty(item.id, 1)} className="w-7 h-7 border border-gray-300 rounded-lg font-bold text-sm hover:border-green-500 hover:text-green-700 transition-all">+</button>
                      </div>
                      <button onClick={() => remove(item.id)} className="text-red-400 hover:text-red-600 text-sm"><i className="fas fa-trash-alt" /></button>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between items-center py-3 border-t-2 border-gray-100 font-extrabold text-lg text-gray-900">
                  Total: <span className="text-green-700">S/ {total.toFixed(2)}</span>
                </div>
                <button onClick={checkout} className="w-full bg-green-500 text-white py-3.5 rounded-xl font-bold text-sm hover:bg-green-600 transition-all flex items-center justify-center gap-2 mt-2">
                  <i className="fab fa-whatsapp" /> PEDIR POR WHATSAPP
                </button>
                <button onClick={() => setCartOpen(false)} className="w-full mt-2 py-3 rounded-xl text-sm font-semibold text-gray-400 hover:text-gray-600 transition-all border border-gray-200">
                  SEGUIR COMPRANDO
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
