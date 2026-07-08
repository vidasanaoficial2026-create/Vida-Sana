import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { label: 'Inicio', path: '/' },
  { label: 'Tienda', path: '/tienda' },
  { label: 'Trabajadores', path: '/trabajadores' },
]

export default function Layout({ children }) {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => { setMenuOpen(false) }, [location])

  const headerBg = scrolled
    ? 'bg-white/90 backdrop-blur-md shadow-sm'
    : 'bg-transparent'
  const textColor = location.pathname === '/'
    ? (scrolled ? 'text-gray-800' : 'text-white/85')
    : 'text-gray-800'

  return (
    <div className="min-h-screen flex flex-col">
      <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${headerBg}`}>
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-3">
          <Link to="/" className="flex items-center gap-2 font-extrabold text-xl">
            <img src="/LOGO.jpg" alt="Vida Sana" className="h-11 rounded-lg" />
          </Link>

          <button className="lg:hidden text-2xl p-1" onClick={() => setMenuOpen(!menuOpen)} aria-label="Menú">
            <i className={`fas ${menuOpen ? 'fa-times' : 'fa-bars'} ${textColor}`} />
          </button>

          <nav className={`${menuOpen ? 'flex' : 'hidden'} lg:flex absolute lg:relative top-full left-0 right-0 lg:top-auto flex-col lg:flex-row items-center gap-1 p-4 lg:p-0 bg-white/98 lg:bg-transparent backdrop-blur-md lg:backdrop-blur-none shadow-lg lg:shadow-none rounded-b-2xl lg:rounded-none`}>
            {NAV.map(nav => {
              const isActive = location.pathname === nav.path
              return (
                <Link
                  key={nav.path}
                  to={nav.path}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-green-700 text-white'
                      : `${textColor} hover:bg-green-50 hover:text-green-700`
                  }`}
                >
                  {nav.label}
                </Link>
              )
            })}
            <a
              href="https://wa.me/51951679585"
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2 rounded-xl text-sm font-bold bg-gold text-gray-900 hover:bg-yellow-500 transition-all ml-2"
            >
              <i className="fab fa-whatsapp mr-1.5" />
              Contacto
            </a>
          </nav>
        </div>
      </header>

      <main className="flex-1">{children}</main>

      <footer className="bg-gray-900 text-white/80 pt-14 pb-0" id="contacto">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 pb-10">
            <div>
              <div className="text-xl font-extrabold text-white mb-3">Vida <span className="text-gold">Sana</span></div>
              <p className="text-sm text-white/55 leading-relaxed mb-5">
                Tu tienda de productos naturales, comprometida con tu bienestar y salud integral.
              </p>
              <div className="flex gap-3">
                {[
                  { icon: 'fab fa-facebook-f', url: 'https://www.facebook.com/profile.php?id=61574949386722' },
                  { icon: 'fab fa-instagram', url: 'https://www.instagram.com/4mnature' },
                  { icon: 'fab fa-whatsapp', url: 'https://wa.me/51951679585' },
                  { icon: 'fab fa-tiktok', url: 'https://www.tiktok.com/@4m_nature' },
                ].map(s => (
                  <a key={s.icon} href={s.url} target="_blank" rel="noopener noreferrer"
                    className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-gold hover:text-gray-900 transition-all">
                    <i className={s.icon} />
                  </a>
                ))}
              </div>
            </div>
            <div>
              <h5 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">Enlaces</h5>
              <ul className="space-y-2 text-sm">
                {[
                  { label: 'Inicio', to: '/' },
                  { label: 'Tienda', to: '/tienda' },
                  { label: 'Trabajadores', to: '/trabajadores' },
                ].map(l => (
                  <li key={l.label}>
                    <Link to={l.to} className="text-white/55 hover:text-gold transition-colors">{l.label}</Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">Contacto</h5>
              <div className="space-y-3 text-sm text-white/55">
                <p className="flex items-center gap-2"><i className="fas fa-phone text-gold w-4" /> +51 951 679 585</p>
                <p className="flex items-center gap-2"><i className="fas fa-envelope text-gold w-4" /> 4Mnatureinfo@gmail.com</p>
                <p className="flex items-center gap-2"><i className="fas fa-map-marker-alt text-gold w-4" /> Av Aviacion 338 Int. 114, La Victoria, Lima</p>
                <p className="flex items-center gap-2"><i className="fas fa-clock text-gold w-4" /> Lun-Sab: 08:00 - 20:00</p>
              </div>
            </div>
            <div>
              <h5 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">Horario</h5>
              <div className="text-sm space-y-3 text-white/55">
                <p><strong className="text-white">Lunes a Sábado</strong><br />08:00 — 20:00</p>
                <p><strong className="text-white">Domingo</strong><br />Cerrado</p>
              </div>
            </div>
          </div>
        </div>
        <div className="border-t border-white/10 py-5 text-center text-xs text-white/35">
          &copy; 2026 Vida Sana &mdash; Powered by <strong className="text-gold">4M Nature</strong>
        </div>
      </footer>

      <a href="https://wa.me/51951679585?text=Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20sus%20productos"
        target="_blank" rel="noopener noreferrer"
        className="fixed bottom-5 right-5 z-50 w-14 h-14 bg-green-500 rounded-full flex items-center justify-center text-white text-3xl shadow-lg hover:scale-110 transition-transform animate-pulse-green"
        aria-label="WhatsApp">
        <i className="fab fa-whatsapp" />
      </a>
    </div>
  )
}
