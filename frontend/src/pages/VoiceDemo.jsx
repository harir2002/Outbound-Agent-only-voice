import { useState } from 'react'
import { voiceAPI } from '../api'

function VoiceDemo() {
    const sector = 'mutual_funds'
    const [language, setLanguage] = useState('en')
    const [phoneNumber, setPhoneNumber] = useState('')
    const [purpose, setPurpose] = useState('sip_debit_reminder')
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
                customer_data: {}
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
                        <div className="form-input" style={{ cursor: 'default' }}>Mutual Funds</div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Purpose</label>
                        <select className="form-select" value={purpose} onChange={(e) => setPurpose(e.target.value)}>
                            <option value="sip_debit_reminder">SIP Debit Reminder</option>
                            <option value="kyc_update_reminder">KYC Update Reminder</option>
                            <option value="sip_failure_notification">SIP Failure Notification</option>
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
