import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import Admin from './pages/Admin'
import Search from './pages/Search'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <header className="topbar">
        <span className="brand">Guidely</span>
        <nav>
          <NavLink to="/">Search</NavLink>
          <NavLink to="/admin">Admin</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Search />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
