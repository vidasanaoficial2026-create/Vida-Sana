import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Tienda from './pages/Tienda'
import Login from './pages/Login'
import AdminProductos from './pages/AdminProductos'
import AdminTrabajadores from './pages/AdminTrabajadores'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/tienda" element={<Tienda />} />
      <Route path="/login" element={<Login />} />
      <Route path="/admin" element={<AdminTrabajadores />} />
      <Route path="/admin/productos" element={<AdminProductos />} />
    </Routes>
  )
}

export default App
