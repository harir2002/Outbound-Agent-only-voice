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
                        <img
                            src="/sba-logo.png"
                            alt="SBA Info Solutions"
                            style={{ height: '45px', objectFit: 'contain' }}
                        />
                        <div className="logo-text">
                            <span className="logo-title">SBA Info Solutions</span>
                            <span className="logo-subtitle">BFSI AI Platform</span>
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
                            to="/voice"
                            className={`nav-link ${isActive('/voice') ? 'active' : ''}`}
                        >
                            Voice AI
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    )
}

export default Header
