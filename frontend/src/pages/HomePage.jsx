import { Link } from 'react-router-dom'
import { useState } from 'react'
import './HomePage.css'

function HomePage() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)



    return (
        <div className="home-page">
            {/* Hero Section */}
            <section className="hero">
                <div className="container">
                    <div className="hero-content fade-in">
                        <h1 className="hero-title">
                            Enterprise AI for <span className="text-primary">BFSI</span>
                        </h1>
                        <p className="hero-subtitle">
                            Automate customer engagement with Voice AI + SMS
                            <br />
                            Powered by Groq, Sarvam AI, and Twilio
                        </p>
                        <div className="hero-actions">
                            <Link to="/campaign" className="btn btn-primary">
                                Start Campaign
                            </Link>

                        </div>


                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="container">
                    <div className="cta-card card">
                        <h2>Ready to Get Started?</h2>
                        <p className="text-muted mb-lg">
                            Start your first campaign: Voice call + SMS follow-up
                        </p>
                        <div className="cta-actions">
                            <Link to="/campaign" className="btn btn-primary">
                                Start Campaign
                            </Link>

                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}

export default HomePage
