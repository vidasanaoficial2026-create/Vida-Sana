import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'

export default function WorkerProfile() {
  const { id } = useParams()
  const [worker, setWorker] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!id) { setError(true); return }
    api.workers.get(id).then(data => {
      setWorker(data.worker)
    }).catch(() => setError(true))
    .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 pt-20">
      <div className="text-center text-gray-400">
        <div className="inline-block w-8 h-8 border-2 border-green-100 border-t-green-700 rounded-full animate-spin" />
        <p className="mt-3 text-sm">Cargando perfil...</p>
      </div>
    </div>
  )

  if (error || !worker) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 pt-20">
      <div className="text-center">
        <div className="text-5xl mb-4">😕</div>
        <h2 className="text-xl font-bold text-gray-800 mb-2">Trabajador no encontrado</h2>
        <p className="text-sm text-gray-400 mb-4">El enlace podría ser incorrecto o el trabajador ya no existe.</p>
        <Link to="/" className="inline-flex items-center gap-2 bg-green-700 text-white px-6 py-2.5 rounded-xl font-semibold text-sm hover:bg-green-900 transition-all">
          <i className="fas fa-arrow-left" /> Volver al inicio
        </Link>
      </div>
    </div>
  )

  const w = worker
  const initial = w.nombre?.charAt(0).toUpperCase() || '?'
  const hasPhoto = w.foto && w.foto.length > 100
  const profileUrl = window.location.href
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(profileUrl)}`

  const copyLink = () => {
    navigator.clipboard.writeText(profileUrl).then(() => alert('Enlace copiado')).catch(() => {
      const input = document.getElementById('profileLink')
      if (input) { input.select(); document.execCommand('copy') }
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-24 pb-12">
      <div className="max-w-2xl mx-auto px-4">
        <Link to="/" className="inline-flex items-center gap-1.5 text-green-700 font-semibold text-sm mb-4 hover:text-green-900 transition-all">
          <i className="fas fa-arrow-left" /> Volver
        </Link>

        <div className="bg-white rounded-2xl overflow-hidden shadow-md">
          {/* COVER */}
          <div className="bg-gradient-to-br from-green-900 to-green-700 px-8 pt-12 pb-8 text-center">
            <div className="w-28 h-28 mx-auto rounded-full border-4 border-white/30 overflow-hidden bg-white/15 flex items-center justify-center mb-4">
              {hasPhoto
                ? <img src={w.foto} alt={w.nombre} className="w-full h-full object-cover" />
                : <span className="text-4xl font-bold text-white">{initial}</span>}
            </div>
            <h1 className="text-2xl font-extrabold text-white">{w.nombre}</h1>
            <p className="text-sm text-white/60 font-medium tracking-wider mt-1">{w.username}</p>
            <div className="mt-3">
              <span className={`inline-block px-4 py-1 rounded-full text-xs font-bold uppercase ${
                (w.estado || 'Activo') === 'Activo' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'
              }`}>
                {w.estado || 'Activo'}
              </span>
            </div>
          </div>

          {/* BODY */}
          <div className="p-6 sm:p-8">
            {/* Personal */}
            <div className="flex items-center gap-2 text-green-900 font-bold text-sm mb-4 pb-2 border-b-2 border-green-50">
              <i className="fas fa-id-card" /> Datos Personales
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
              {[
                { label: 'DNI', value: w.dni },
                { label: 'Teléfono', value: w.telefono },
                { label: 'Email', value: w.email },
                { label: 'Dirección', value: w.direccion },
              ].map(r => (
                <div key={r.label}>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-0.5">{r.label}</p>
                  <p className="font-semibold text-gray-800 bg-gray-50 rounded-lg px-3 py-2 text-sm">{r.value || '-'}</p>
                </div>
              ))}
            </div>

            {/* Laboral */}
            <div className="flex items-center gap-2 text-green-900 font-bold text-sm mb-4 pb-2 border-b-2 border-green-50">
              <i className="fas fa-briefcase" /> Datos Laborales
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
              {[
                { label: 'Cargo', value: w.cargo },
                { label: 'Área', value: w.area },
                { label: 'Fecha Ingreso', value: w.fecha_ingreso ? w.fecha_ingreso.split('T')[0] : '' },
              ].map(r => (
                <div key={r.label}>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-0.5">{r.label}</p>
                  <p className="font-semibold text-gray-800 bg-gray-50 rounded-lg px-3 py-2 text-sm">{r.value || '-'}</p>
                </div>
              ))}
            </div>

            {/* QR */}
            <div className="bg-gray-50 rounded-2xl p-6 text-center">
              <h5 className="text-sm font-bold text-green-900 mb-3"><i className="fas fa-qrcode mr-1" /> Código QR de Acceso</h5>
              <img src={qrUrl} alt="QR" width="200" className="mx-auto rounded-xl border-2 border-white shadow-sm" />
              <input id="profileLink" type="text" readOnly value={profileUrl}
                className="w-full max-w-sm mt-3 mx-auto block px-3 py-2 rounded-lg border border-gray-200 text-xs text-center font-medium text-green-700 bg-white" />
              <div className="flex gap-3 justify-center mt-3">
                <a href={qrUrl} download="QR_Acceso.png"
                  className="bg-green-700 text-white px-5 py-2 rounded-lg text-xs font-semibold hover:bg-green-900 transition-all flex items-center gap-1.5">
                  <i className="fas fa-download" /> DESCARGAR QR
                </a>
                <button onClick={copyLink}
                  className="border border-green-700 text-green-700 px-5 py-2 rounded-lg text-xs font-semibold hover:bg-green-50 transition-all flex items-center gap-1.5">
                  <i className="fas fa-copy" /> COPIAR ENLACE
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
