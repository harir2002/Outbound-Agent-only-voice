import { useState } from 'react'
import { voiceAPI } from '../api'

function VoiceDemo() {
    const [sector, setSector] = useState('banking')
    const [language, setLanguage] = useState('en')
    const [phoneNumber, setPhoneNumber] = useState('')
    const [email, setEmail] = useState('')
    const [purpose, setPurpose] = useState('emi_reminder')
    const [publicUrl, setPublicUrl] = useState('https://1db819452b10.ngrok-free.app')
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')

    const initiateCall = async () => {
        if (!phoneNumber) {
            alert('Please enter phone number')
            return
        }

        try {
            setLoading(true)
            const response = await voiceAPI.initiateCall({
                phone_number: phoneNumber,
                purpose,
                sector,
                language,
                public_url: publicUrl,
                customer_data: { email }
            })
            setMessage(`Call initiated! Call ID: ${response.data.call_id}`)
        } catch (error) {
            setMessage('Failed to initiate call: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="voice-demo container">
            <h1>Voice AI Demo</h1>
            <p className="text-muted">Test outbound voice calls with multilingual AI</p>

            <div className="demo-grid">
                <div className="card">
                    <h3>Initiate Outbound Call</h3>
                    <div className="form-group">
                        <label className="form-label">Ngrok / Public URL</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="https://your-ngrok-url.app"
                            value={publicUrl}
                            onChange={(e) => setPublicUrl(e.target.value)}
                        />
                        <small className="text-muted" style={{ display: 'block', marginTop: '0.25rem' }}>
                            Required for Twilio callbacks (must start with https://)
                        </small>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Sector</label>
                        <select className="form-select" value={sector} onChange={(e) => setSector(e.target.value)}>
                            <option value="banking">Banking</option>
                            <option value="insurance">Insurance</option>
                            <option value="nbfc">NBFC</option>
                            <option value="mutual_funds">Mutual Funds</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Purpose</label>
                        <select className="form-select" value={purpose} onChange={(e) => setPurpose(e.target.value)}>
                            <option value="emi_reminder">EMI Reminder</option>
                            <option value="policy_renewal">Policy Renewal</option>
                            <option value="loan_offer">Loan Offer</option>
                            <option value="claim_update">Claim Update</option>
                            <option value="debt_recovery">Debt Recovery (Resolution Offer)</option>
                            <option value="lead_generation">Lead Generation (Pre-Approved Loan)</option>
                            <option value="credit_repair">Credit Repair (Health Check)</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Language</label>
                        <select className="form-select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="ta">Tamil</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Phone Number</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="+919876543210"
                            value={phoneNumber}
                            onChange={(e) => setPhoneNumber(e.target.value)}
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Email Address</label>
                        <input
                            type="email"
                            className="form-input"
                            placeholder="user@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <small className="text-muted" style={{ display: 'block', marginTop: '0.25rem' }}>
                            Optional: Enter email to receive call summary and links
                        </small>
                    </div>
                    <button className="btn btn-primary" onClick={initiateCall} disabled={loading}>
                        {loading ? 'Initiating...' : 'Initiate Call'}
                    </button>
                    {message && <p className="mt-md">{message}</p>}
                </div>

                <div className="card">
                    <h3>Features</h3>
                    <ul className="feature-list">
                        <li>Multilingual TTS/STT</li>
                        <li>Intent capture</li>
                        <li>Call recording</li>
                        <li>Consent tracking</li>
                        <li>Analytics</li>
                    </ul>
                </div>
            </div>
        </div >
    )
}

export default VoiceDemo
