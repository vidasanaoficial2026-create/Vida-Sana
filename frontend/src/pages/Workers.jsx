import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'

function formatDate(d) {
  if (!d) return ''
  return d.split('T')[0]
}

export default function Workers() {
  const [workers, setWorkers] = useState([])
  const [stats, setStats] = useState({ total: 0, activos: 0 })
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null) // null | 'add' | {editId}
  const [credModal, setCredModal] = useState(null)
  const [qrModal, setQrModal] = useState(null)
  const [foto, setFoto] = useState('')

  const formInit = { nombre: '', dni: '', cargo: '', area: '', fecha_ingreso: new Date().toISOString().split('T')[0], telefono: '', direccion: '', email: '', estado: 'Activo' }
  const [form, setForm] = useState({ ...formInit })

  const load = useCallback(async () => {
    try {
      const [wData, cData] = await Promise.all([api.workers.list(search || undefined), api.workers.count()])
      setWorkers(wData.workers)
      setStats(cData)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [search])

  useEffect(() => { load() }, [load])

  const openAdd = () => {
    setForm({ ...formInit, fecha_ingreso: new Date().toISOString().split('T')[0] })
    setFoto('')
    setModal('add')
  }

  const openQr = async (id) => {
    try {
      const data = await api.workers.get(id)
      setQrModal(data.worker)
    } catch (e) { alert(e.message) }
  }

  const handleSubmit = async () => {
    if (!form.nombre || !form.dni || form.dni.length !== 8) return alert('Complete los campos obligatorios (DNI 8 dígitos)')
    const body = { ...form, foto }
    try {
      if (modal === 'add') {
        const data = await api.workers.create(body)
        setCredModal(data)
        setModal(null)
      } else {
        await api.workers.update(modal.editId, body)
        setModal(null)
      }
      load()
    } catch (e) { alert(e.message) }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`¿Eliminar a ${name}?`)) return
    try {
      await api.workers.delete(id)
      load()
    } catch (e) { alert(e.message) }
  }

  const previewPhoto = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const img = new Image()
      img.onload = () => {
        const c = document.createElement('canvas')
        const MAX = 400
        let w = img.width, h = img.height
        if (w > h) { if (w > MAX) { h *= MAX / w; w = MAX } }
        else { if (h > MAX) { w *= MAX / h; h = MAX } }
        c.width = w; c.height = h
        const ctx = c.getContext('2d')
        ctx.drawImage(img, 0, 0, w, h)
        setFoto(c.toDataURL('image/jpeg', 0.7))
      }
      img.src = ev.target.result
    }
    reader.readAsDataURL(file)
  }

  const inactivos = stats.total - stats.activos

  return (
    <div className="pt-24 min-h-screen bg-gray-50 pb-16">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900">Trabajadores</h1>
            <p className="text-sm text-gray-400">Directorio de trabajadores de 4M Nature</p>
          </div>
          <button onClick={openAdd} className="bg-green-700 text-white px-6 py-2.5 rounded-xl font-bold text-sm hover:bg-green-900 transition-all flex items-center gap-2">
            <i className="fas fa-plus" /> REGISTRAR
          </button>
        </div>

        {/* STATS */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: 'Total', value: stats.total, color: 'text-green-900' },
            { label: 'Activos', value: stats.activos, color: 'text-green-600' },
            { label: 'Inactivos', value: inactivos, color: 'text-red-500' },
          ].map(s => (
            <div key={s.label} className="bg-white rounded-2xl p-4 text-center shadow-sm border border-gray-100">
              <p className="text-xs text-gray-400 font-medium">{s.label}</p>
              <p className={`text-3xl font-black ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* SEARCH */}
        <input type="text" placeholder="Buscar por nombre, DNI, cargo..."
          value={search} onChange={e => setSearch(e.target.value)}
          className="w-full max-w-md px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white mb-6" />

        {/* WORKERS GRID */}
        {loading ? (
          <div className="text-center py-20 text-gray-400">
            <div className="inline-block w-8 h-8 border-2 border-green-100 border-t-green-700 rounded-full animate-spin" />
          </div>
        ) : workers.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <i className="fas fa-users text-4xl mb-3" />
            <p>No hay trabajadores registrados</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {workers.map(w => {
              const initial = w.nombre?.charAt(0).toUpperCase() || '?'
              const hasPhoto = w.foto && w.foto.length > 100
              const profileUrl = `${window.location.origin}/worker/${w.id}`
              return (
                <div key={w.id} className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-all">
                  <div className="bg-gradient-to-br from-green-900 to-green-700 p-6 text-center cursor-pointer"
                    onClick={() => window.open(profileUrl, '_blank')}>
                    <div className="w-16 h-16 mx-auto rounded-full bg-white/20 flex items-center justify-center border-2 border-white/30 overflow-hidden mb-2">
                      {hasPhoto
                        ? <img src={w.foto} alt={w.nombre} className="w-full h-full object-cover" />
                        : <span className="text-xl font-bold text-white">{initial}</span>}
                    </div>
                    <p className="text-xs text-white/60 font-medium tracking-wider">{w.username}</p>
                    <p className="font-bold text-white">{w.nombre}</p>
                  </div>
                  <div className="p-4 -mt-4">
                    <div className="bg-white rounded-xl p-3 shadow-sm space-y-2 text-xs">
                      {[
                        { label: 'DNI', value: w.dni || '-' },
                        { label: 'Cargo', value: w.cargo || '-' },
                        { label: 'Área', value: w.area || '-' },
                        { label: 'Estado', value: w.estado || 'Activo' },
                        { label: 'Ingreso', value: formatDate(w.fecha_ingreso) || '-' },
                      ].map(r => (
                        <div key={r.label} className="flex justify-between items-center">
                          <span className="text-gray-400">{r.label}</span>
                          <span className={`font-semibold ${r.label === 'Estado' ? (w.estado === 'Activo' ? 'text-green-600' : 'text-red-500') : 'text-gray-800'}`}>
                            {r.label === 'Estado' ? (
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${w.estado === 'Activo' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>{w.estado}</span>
                            ) : r.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="px-4 pb-4 flex gap-2">
                    <button onClick={() => window.open(profileUrl, '_blank')} className="flex-1 bg-green-700 text-white py-2 rounded-lg text-xs font-semibold hover:bg-green-900 transition-all">
                      <i className="fas fa-eye mr-1" /> PERFIL
                    </button>
                    <button onClick={() => openQr(w.id)} className="w-9 bg-gold text-gray-900 rounded-lg text-xs font-bold hover:bg-yellow-500 transition-all">
                      <i className="fas fa-qrcode" />
                    </button>
                    <button onClick={() => { setForm({ nombre: w.nombre, dni: w.dni, cargo: w.cargo, area: w.area, fecha_ingreso: w.fecha_ingreso || '', telefono: w.telefono, direccion: w.direccion, email: w.email, estado: w.estado }); setFoto(w.foto || ''); setModal({ editId: w.id }) }}
                      className="w-9 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-all text-xs">
                      <i className="fas fa-edit" />
                    </button>
                    <button onClick={() => handleDelete(w.id, w.nombre)} className="w-9 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all text-xs">
                      <i className="fas fa-trash" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* ADD/EDIT MODAL */}
      {modal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setModal(null)}>
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-extrabold text-green-900 mb-5">{modal === 'add' ? 'Registrar Trabajador' : 'Editar Trabajador'}</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Nombre Completo</label>
                <input type="text" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })}
                  className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 block mb-1">DNI</label>
                  <input type="text" maxLength={8} value={form.dni} onChange={e => setForm({ ...form, dni: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 block mb-1">Teléfono</label>
                  <input type="text" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 block mb-1">Cargo</label>
                  <input type="text" value={form.cargo} onChange={e => setForm({ ...form, cargo: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 block mb-1">Área</label>
                  <input type="text" value={form.area} onChange={e => setForm({ ...form, area: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 block mb-1">Fecha Ingreso</label>
                  <input type="date" value={form.fecha_ingreso} onChange={e => setForm({ ...form, fecha_ingreso: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 block mb-1">Estado</label>
                  <select value={form.estado} onChange={e => setForm({ ...form, estado: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50">
                    <option value="Activo">Activo</option>
                    <option value="Inactivo">Inactivo</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Email</label>
                <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
                  className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Dirección</label>
                <input type="text" value={form.direccion} onChange={e => setForm({ ...form, direccion: e.target.value })}
                  className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Foto</label>
                <input type="file" accept="image/*" onChange={previewPhoto} className="text-sm text-gray-400" />
                {foto && <img src={foto} alt="preview" className="w-16 h-16 rounded-full object-cover mt-2 border" />}
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-100">
              <button onClick={() => setModal(null)} className="px-5 py-2.5 rounded-xl text-sm font-semibold text-gray-500 hover:bg-gray-100 transition-all">Cancelar</button>
              <button onClick={handleSubmit} className="px-6 py-2.5 rounded-xl text-sm font-bold bg-green-700 text-white hover:bg-green-900 transition-all">
                {modal === 'add' ? 'REGISTRAR' : 'GUARDAR'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CREDENTIALS MODAL */}
      {credModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setCredModal(null)}>
          <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl p-6 text-center" onClick={e => e.stopPropagation()}>
            <div className="text-4xl mb-3">🔑</div>
            <h2 className="text-lg font-extrabold text-green-900 mb-1">¡Trabajador Creado!</h2>
            <p className="text-sm text-gray-500 mb-4">Credenciales de acceso al sistema:</p>
            <div className="bg-gray-50 rounded-xl p-4 border border-dashed border-green-700 mb-3 space-y-2">
              <div className="flex justify-between text-sm"><strong>Usuario:</strong> <span className="font-bold text-green-700">{credModal.generated_username}</span></div>
              <div className="flex justify-between text-sm"><strong>Contraseña:</strong> <span className="font-bold text-green-700">{credModal.generated_password}</span></div>
            </div>
            <p className="text-xs text-red-500 mb-4">⚠ La contraseña es el DNI del trabajador</p>
            <div className="border-t border-gray-100 pt-4">
              <p className="text-sm font-semibold mb-2">📲 QR de acceso al perfil</p>
              <img src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(window.location.origin + '/worker/' + credModal.worker.id)}`} alt="QR" className="mx-auto rounded-xl border" width="180" />
              <a href={`https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(window.location.origin + '/worker/' + credModal.worker.id)}`} download="credenciales.png"
                className="inline-flex items-center gap-2 mt-3 bg-green-700 text-white px-5 py-2 rounded-xl text-sm font-semibold hover:bg-green-900 transition-all">
                <i className="fas fa-download" /> DESCARGAR QR
              </a>
            </div>
            <button onClick={() => setCredModal(null)} className="mt-4 bg-green-700 text-white px-8 py-2.5 rounded-xl text-sm font-bold hover:bg-green-900 transition-all">ENTENDIDO</button>
          </div>
        </div>
      )}

      {/* QR MODAL */}
      {qrModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setQrModal(null)}>
          <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl p-6 text-center" onClick={e => e.stopPropagation()}>
            <div className="text-4xl mb-3">📲</div>
            <h2 className="text-lg font-extrabold text-green-900 mb-1">QR — {qrModal.username}</h2>
            <p className="text-sm text-gray-500 mb-4">Escanea para ver el perfil</p>
            <img src={`https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(window.location.origin + '/worker/' + qrModal.id)}`} alt="QR" className="mx-auto rounded-xl border" width="220" />
            <div className="mt-3 text-xs text-gray-400 truncate max-w-full px-2">
              <i className="fas fa-link mr-1" /> {window.location.origin}/worker/{qrModal.id}
            </div>
            <div className="flex gap-3 justify-center mt-4">
              <a href={`https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(window.location.origin + '/worker/' + qrModal.id)}`} download={`QR_${qrModal.username}.png`}
                className="bg-green-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-green-900 transition-all flex items-center gap-2">
                <i className="fas fa-download" /> DESCARGAR
              </a>
              <button onClick={() => { navigator.clipboard.writeText(window.location.origin + '/worker/' + qrModal.id); alert('Enlace copiado') }}
                className="border border-green-700 text-green-700 px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-green-50 transition-all flex items-center gap-2">
                <i className="fas fa-copy" /> COPIAR
              </button>
            </div>
            <button onClick={() => setQrModal(null)} className="mt-4 text-sm text-gray-400 hover:text-gray-600 font-semibold">CERRAR</button>
          </div>
        </div>
      )}
    </div>
  )
}
