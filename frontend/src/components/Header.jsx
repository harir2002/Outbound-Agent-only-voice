import { Link, useLocation } from 'react-router-dom'
import './Header.css'

function Header() {
    const location = useLocation()

    const isActive = (path) => location.pathname === path

    return (
        <header className="header">
            <div className="container">
                <div className="header-content">
                    <Link to="/" className="logo">
                        <div className="logo-icon">🏦</div>
                        <div className="logo-text">
                            <span className="logo-title">BFSI AI Platform</span>
                            <span className="logo-subtitle">WhatsApp & Voice AI</span>
                        </div>
                    </Link>

                    <nav className="nav">
                        <Link
                            to="/"
                            className={`nav-link ${isActive('/') ? 'active' : ''}`}
                        >
                            Home
                        </Link>
                        <Link
                            to="/campaign"
                            className={`nav-link ${isActive('/campaign') ? 'active' : ''}`}
                        >
                            Campaign
                        </Link>
                        <Link
                            to="/whatsapp"
                            className={`nav-link ${isActive('/whatsapp') ? 'active' : ''}`}
                        >
                            WhatsApp
                        </Link>
                        <Link
                            to="/voice"
                            className={`nav-link ${isActive('/voice') ? 'active' : ''}`}
                        >
                            Voice AI
                        </Link>
                    </nav>

                    <div className="header-actions">
                        <button className="btn btn-outline">Documentation</button>
                    </div>
                </div>
            </div>
        </header>
    )
}

export default Header
