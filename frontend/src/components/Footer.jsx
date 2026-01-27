import './Footer.css'

function Footer() {
    const currentYear = new Date().getFullYear()

    return (
        <footer className="footer">
            <div className="container">
                <div className="footer-content">
                    <div className="footer-section">
                        <h4>BFSI AI Platform</h4>
                        <p className="text-muted">
                            Enterprise-grade AI for Banking, Insurance, NBFCs & Mutual Funds
                        </p>
                    </div>

                    <div className="footer-section">
                        <h5>Features</h5>
                        <ul className="footer-links">

                            <li><a href="#voice">Voice AI</a></li>

                            <li><a href="#compliance">Compliance</a></li>
                        </ul>
                    </div>

                    <div className="footer-section">
                        <h5>Technology</h5>
                        <ul className="footer-links">
                            <li><a href="#groq">Groq LLM</a></li>
                            <li><a href="#sarvam">Sarvam AI</a></li>
                            <li><a href="#twilio">Twilio</a></li>
                            <li><a href="#chromadb">ChromaDB</a></li>
                        </ul>
                    </div>

                    <div className="footer-section">
                        <h5>Resources</h5>
                        <ul className="footer-links">
                            <li><a href="#docs">Documentation</a></li>
                            <li><a href="#api">API Reference</a></li>
                            <li><a href="#support">Support</a></li>
                            <li><a href="#contact">Contact</a></li>
                        </ul>
                    </div>
                </div>

                <div className="footer-bottom">
                    <p className="text-muted">
                        © {currentYear} BFSI AI Platform. All rights reserved.
                    </p>
                    <div className="footer-badges">
                        <span className="badge">GDPR Compliant</span>
                        <span className="badge">RBI Aligned</span>
                        <span className="badge">IRDAI Compliant</span>
                    </div>
                </div>
            </div>
        </footer>
    )
}

export default Footer
