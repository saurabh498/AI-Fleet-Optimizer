import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './advanced-ui.css'
import './ui/ux-overrides.css'
import "leaflet/dist/leaflet.css";
import "./ui/frontend-refresh.css";
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
