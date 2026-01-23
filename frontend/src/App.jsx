import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CampaignPage from './pages/CampaignPage'
import WhatsAppDemo from './pages/WhatsAppDemo'
import VoiceDemo from './pages/VoiceDemo'
import Header from './components/Header'
import Footer from './components/Footer'

function App() {
    return (
        <Router>
            <div className="app">
                <Header />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/campaign" element={<CampaignPage />} />
                        <Route path="/whatsapp" element={<WhatsAppDemo />} />
                        <Route path="/voice" element={<VoiceDemo />} />
                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    )
}

export default App
