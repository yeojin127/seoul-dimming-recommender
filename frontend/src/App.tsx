import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MapPage } from './pages/MapPage/MapPage'
import { LoginPage } from './pages/LoginPage/LoginPage'
import { ProtectedRoute } from './components/Auth/ProtectedRoute'

function App() {

  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MapPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
