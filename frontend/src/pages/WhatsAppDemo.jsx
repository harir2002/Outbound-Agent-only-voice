import { useState } from 'react'
import { whatsappAPI } from '../api'
import './WhatsAppDemo.css'

function WhatsAppDemo() {
    const [sector, setSector] = useState('banking')
    const [phoneNumber, setPhoneNumber] = useState('')
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')

    const sendTestMessage = async () => {
        if (!phoneNumber) {
            alert('Please enter phone number')
            return
        }

        try {
            setLoading(true)
            await whatsappAPI.sendMessage({
                to_number: phoneNumber,
                message: `Hello! This is a test message from BFSI AI Platform for ${sector}.`
            })
            setMessage('Message sent successfully!')
        } catch (error) {
            setMessage('Failed to send message: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="whatsapp-demo container">
            <h1>WhatsApp AI Demo</h1>
            <p className="text-muted">Test WhatsApp messaging with AI-powered responses</p>

            <div className="demo-grid">
                <div className="card">
                    <h3>Send Test Message</h3>
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
                        <label className="form-label">Phone Number (with country code)</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="+919876543210"
                            value={phoneNumber}
                            onChange={(e) => setPhoneNumber(e.target.value)}
                        />
                    </div>
                    <button className="btn btn-primary" onClick={sendTestMessage} disabled={loading}>
                        {loading ? 'Sending...' : 'Send Message'}
                    </button>
                    {message && <p className="mt-md">{message}</p>}
                </div>

                <div className="card">
                    <h3>Features</h3>
                    <ul className="feature-list">
                        <li>Auto-reply with AI context</li>
                        <li>Intent classification</li>
                        <li>Session management</li>
                        <li>Payment links</li>
                        <li>Policy details</li>
                        <li>Loan summaries</li>
                    </ul>
                </div>
            </div>
        </div>
    )
}

export default WhatsAppDemo
