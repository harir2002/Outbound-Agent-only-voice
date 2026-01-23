import { useState } from 'react'
import { voiceAPI } from '../api'

function VoiceDemo() {
    const [sector, setSector] = useState('banking')
    const [language, setLanguage] = useState('en')
    const [phoneNumber, setPhoneNumber] = useState('')
    const [purpose, setPurpose] = useState('emi_reminder')
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
                language
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
                        </select>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Language</label>
                        <select className="form-select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="ta">Tamil</option>
                            <option value="te">Telugu</option>
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
        </div>
    )
}

export default VoiceDemo
