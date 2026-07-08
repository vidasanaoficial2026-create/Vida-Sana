import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const FEATURES = [
  { icon: 'fas fa-certificate', bg: 'bg-green-50', color: 'text-green-700', title: 'Calidad Garantizada',
    desc: 'Todos nuestros productos cuentan con registros sanitarios y cumplen los más altos estándares.' },
  { icon: 'fas fa-seedling', bg: 'bg-gold-light', color: 'text-amber-800', title: 'Insumos Orgánicos',
    desc: 'Seleccionamos los mejores ingredientes de la naturaleza para cada producto.' },
  { icon: 'fas fa-leaf', bg: 'bg-teal-50', color: 'text-teal-700', title: 'Proceso Natural',
    desc: 'Elaboramos respetando procesos artesanales que preservan todas sus propiedades.' },
]

const TESTIMONIALS = [
  { name: 'María C.', initial: 'MC', text: 'Los productos son de excelente calidad. El Colágeno H. me ha ayudado mucho con mis articulaciones.' },
  { name: 'Pedro L.', initial: 'PL', text: 'Excelente atención y productos de primera. El STEM CELL me ha dado mucha más energía.' },
  { name: 'Lucía G.', initial: 'LG', text: 'Desde que consumo los productos de Vida Sana mi salud ha mejorado notablemente.' },
]

function useReveal() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('opacity-100', 'translate-y-0') }),
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    )
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
    return () => observer.disconnect()
  }, [])
}

function ProdCard({ p }) {
  const out = p.stock <= 0

  const addToCart = () => {
    if (out) return
    const cart = JSON.parse(localStorage.getItem('vid_sana_cart') || '[]')
    const exist = cart.find(c => c.id === p.id)
    const qty = exist ? exist.qty : 0
    if (qty >= p.stock) { alert('Stock máximo alcanzado'); return }
    if (exist) exist.qty += 1
    else cart.push({ id: p.id, nombre: p.nombre, precio: p.precio, qty: 1 })
    localStorage.setItem('vid_sana_cart', JSON.stringify(cart))
    window.dispatchEvent(new Event('cart-update'))
    alert(`${p.nombre} añadido al carrito`)
  }

  return (
    <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md hover:-translate-y-1.5 transition-all duration-300">
      <div className="h-52 bg-cream flex items-center justify-center p-6">
        {p.imagen
          ? <img src={p.imagen} alt={p.nombre} className="max-h-full max-w-full object-contain hover:scale-105 transition-transform duration-500" loading="lazy" />
          : <i className="fas fa-leaf text-5xl text-gray-300" />}
      </div>
      <div className="p-5">
        <p className="text-xs font-bold uppercase tracking-wider text-green-500 mb-1">{p.categoria || 'General'}</p>
        <h3 className="font-bold text-gray-800 mb-1">{p.nombre}</h3>
        <p className="text-2xl font-extrabold text-green-700 mb-3">S/ {p.precio.toFixed(2)}</p>
        <div className="flex gap-2">
          <button onClick={addToCart} disabled={out}
            className="flex-1 bg-green-700 text-white py-2.5 px-4 rounded-xl font-semibold text-sm hover:bg-green-900 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            <i className={`fas ${out ? 'fa-times-circle' : 'fa-cart-plus'}`} /> {out ? 'AGOTADO' : 'AÑADIR'}
          </button>
          <a href={`https://wa.me/51951679585?text=${encodeURIComponent(`Hola, quiero información sobre ${p.nombre} (S/${p.precio.toFixed(2)})`)}`}
            target="_blank" rel="noopener noreferrer"
            className="w-11 bg-green-500 text-white rounded-xl flex items-center justify-center hover:bg-green-600 transition-all">
            <i className="fab fa-whatsapp" />
          </a>
        </div>
      </div>
    </div>
  )
}

export default function Landing() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  useReveal()

  useEffect(() => {
    api.productos.list().then(data => {
      const featured = data.productos.filter(p => p.destacado).slice(0, 6)
      setProducts(featured.length ? featured : data.productos.slice(0, 6))
    }).catch(console.error).finally(() => setLoading(false))
  }, [])

  return (
    <>
      {/* HERO */}
      <section className="relative min-h-screen flex items-center bg-gradient-to-br from-green-900 via-green-700 to-green-500 overflow-hidden">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.03\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }} />
        <div className="absolute w-[500px] h-[500px] rounded-full bg-white/5 -top-24 -right-24" />
        <div className="absolute w-[300px] h-[300px] rounded-full bg-white/5 -bottom-16 -left-16" />

        <div className="max-w-6xl mx-auto px-6 pt-28 pb-20 grid md:grid-cols-2 gap-12 items-center w-full relative z-10">
          <div>
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md border border-white/15 rounded-full pl-1.5 pr-4 py-1 text-xs font-semibold text-gold-light uppercase tracking-wider mb-6">
              <span className="w-7 h-7 bg-gold rounded-full flex items-center justify-center text-gray-900"><i className="fas fa-leaf text-xs" /></span>
              100% Natural
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black leading-tight text-white mb-4">
              Bienestar Natural<br />
              <span className="text-gradient-gold">para tu Vida</span>
            </h1>
            <p className="text-white/70 text-lg max-w-md mb-8 leading-relaxed">
              Descubre nuestra línea completa de suplementos, bebidas y productos naturales elaborados con los mejores insumos orgánicos del Perú.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/tienda" className="inline-flex items-center gap-2 bg-gold text-gray-900 px-8 py-3.5 rounded-xl font-bold text-sm hover:shadow-lg hover:shadow-gold/30 hover:-translate-y-0.5 transition-all">
                <i className="fas fa-shopping-bag" /> VER PRODUCTOS
              </Link>
              <a href="#beneficios" className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md border border-white/20 text-white px-8 py-3.5 rounded-xl font-semibold text-sm hover:bg-white/20 transition-all">
                <i className="fas fa-arrow-down" /> EXPLORAR
              </a>
            </div>
          </div>

          <div className="flex justify-center relative">
            <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/1.png" alt="Productos"
              className="max-h-[420px] object-contain drop-shadow-2xl animate-float" />
            <div className="hidden lg:flex absolute top-8 -right-4 bg-white/95 backdrop-blur-md rounded-2xl p-3.5 shadow-xl items-center gap-2.5 animate-float" style={{ animationDelay: '-2s' }}>
              <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center text-green-700"><i className="fas fa-certificate" /></div>
              <div><strong className="block text-sm text-gray-800">100% Orgánico</strong><span className="text-xs text-gray-400">Registro sanitario</span></div>
            </div>
            <div className="hidden lg:flex absolute bottom-20 -left-8 bg-white/95 backdrop-blur-md rounded-2xl p-3.5 shadow-xl items-center gap-2.5 animate-float" style={{ animationDelay: '-4s' }}>
              <div className="w-10 h-10 bg-gold-light rounded-xl flex items-center justify-center text-amber-800"><i className="fas fa-truck" /></div>
              <div><strong className="block text-sm text-gray-800">Envíos Rápidos</strong><span className="text-xs text-gray-400">A todo el Perú</span></div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="bg-cream py-24 px-6" id="beneficios">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14 reveal opacity-0 translate-y-6 transition-all duration-700">
            <p className="text-xs font-bold uppercase tracking-widest text-green-500 mb-2">Beneficios</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-3">¿Por qué elegir <span className="text-green-500">Vida Sana</span>?</h2>
            <p className="text-gray-400 max-w-lg mx-auto">Calidad, tradición y compromiso con tu bienestar.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-7">
            {FEATURES.map((f, i) => (
              <div key={i} className={`bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-md hover:-translate-y-1.5 transition-all duration-300 reveal opacity-0 translate-y-6 transition-all duration-700 delay-[${i * 100}ms]`}
                style={{ transitionDelay: `${i * 100}ms` }}>
                <div className={`w-13 h-13 ${f.bg} ${f.color} rounded-xl flex items-center justify-center text-xl mb-5`}>
                  <i className={f.icon} />
                </div>
                <h3 className="font-bold text-gray-800 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PRODUCTS */}
      <section className="py-24 px-6" id="productos">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14 reveal opacity-0 translate-y-6 transition-all duration-700">
            <p className="text-xs font-bold uppercase tracking-widest text-green-500 mb-2">Productos</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-3">Nuestros <span className="text-green-500">Destacados</span></h2>
            <p className="text-gray-400 max-w-lg mx-auto">Los favoritos de nuestros clientes, calidad y precio inigualables.</p>
          </div>
          {loading ? (
            <div className="text-center py-16 text-gray-400">
              <div className="inline-block w-8 h-8 border-2 border-green-100 border-t-green-700 rounded-full animate-spin" />
              <p className="mt-3 text-sm">Cargando productos...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map(p => <ProdCard key={p.id} p={p} />)}
            </div>
          )}
          <div className="text-center mt-10">
            <Link to="/tienda" className="inline-flex items-center gap-2 border-2 border-green-700 text-green-700 px-8 py-3 rounded-xl font-bold text-sm hover:bg-green-700 hover:text-white transition-all">
              VER TODOS <i className="fas fa-arrow-right" />
            </Link>
          </div>
        </div>
      </section>

      {/* ABOUT */}
      <section className="bg-green-900 py-24 px-6 text-white">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-14 items-center">
          <div className="text-center reveal opacity-0 translate-y-6 transition-all duration-700">
            <img src="https://naturasanaperu.com/wp-content/uploads/2023/06/MUJER-2-FRASCOSnatura.png" alt="Vida Sana"
              className="max-h-[400px] object-contain mx-auto drop-shadow-lg" />
          </div>
          <div className="reveal opacity-0 translate-y-6 transition-all duration-700" style={{ transitionDelay: '100ms' }}>
            <h2 className="text-3xl md:text-4xl font-extrabold mb-5 leading-tight">Comprometidos con tu <span className="text-gold">Salud y Bienestar</span></h2>
            <p className="text-white/70 leading-relaxed mb-6">
              En Vida Sana llevamos años ofreciendo productos naturales de la más alta calidad. Creemos en el poder de la naturaleza para transformar vidas.
            </p>
            <p className="text-white/70 leading-relaxed mb-8">
              Trabajamos directamente con productores locales para traerte lo mejor de la tierra peruana.
            </p>
            <div className="grid grid-cols-3 gap-5 text-center">
              {[
                { num: '50+', label: 'Productos' },
                { num: '1000+', label: 'Clientes' },
                { num: '5', label: 'Categorías' },
              ].map(s => (
                <div key={s.label}>
                  <div className="text-3xl font-black text-gold">{s.num}</div>
                  <div className="text-xs text-white/50 uppercase tracking-wider font-medium">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="py-24 px-6" id="testimonios">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14 reveal opacity-0 translate-y-6 transition-all duration-700">
            <p className="text-xs font-bold uppercase tracking-widest text-green-500 mb-2">Testimonios</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-3">Lo que dicen <span className="text-green-500">nuestros clientes</span></h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300"
                style={{ transitionDelay: `${i * 100}ms` }}>
                <div className="text-gold text-sm mb-3">{'★'.repeat(5)}</div>
                <p className="text-gray-600 text-sm leading-relaxed italic mb-5">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-full bg-green-50 flex items-center justify-center font-bold text-green-700">{t.initial}</div>
                  <div><strong className="text-sm text-gray-800">{t.name}</strong><span className="block text-xs text-gray-400">Cliente verificada</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-gradient-to-br from-green-700 to-green-500 text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.03\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }} />
        <div className="max-w-xl mx-auto relative z-10 reveal opacity-0 translate-y-6 transition-all duration-700">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-3">¿Listo para empezar tu cambio?</h2>
          <p className="text-white/80 mb-8">Descubre nuestra línea completa de productos naturales y empieza a sentir la diferencia.</p>
          <a href="https://wa.me/51951679585?text=Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20sus%20productos"
            target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-gold text-gray-900 px-10 py-4 rounded-xl font-bold text-base hover:shadow-lg hover:shadow-gold/30 hover:-translate-y-0.5 transition-all">
            <i className="fab fa-whatsapp" /> PEDIR POR WHATSAPP
          </a>
        </div>
      </section>

      <style>{`
        @keyframes float { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-16px); } }
        .animate-float { animation: float 6s ease-in-out infinite; }
        @keyframes pulse-green { 0% { box-shadow: 0 4px 20px rgba(37,211,102,0.4); } 50% { box-shadow: 0 4px 30px rgba(37,211,102,0.6); } 100% { box-shadow: 0 4px 20px rgba(37,211,102,0.4); } }
        .animate-pulse-green { animation: pulse-green 2s infinite; }
      `}</style>
    </>
  )
}
