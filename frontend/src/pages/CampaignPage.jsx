import { useState } from 'react'
import { voiceAPI } from '../api'
import './CampaignPage.css'

function CampaignPage() {
    const [formData, setFormData] = useState({
        phoneNumber: '',
        customerName: '',
        campaignType: 'sip_debit_reminder',
        sector: 'mutual_funds',
        language: 'en',
        ngrokUrl: 'https://1db819452b10.ngrok-free.app'
    })

    const [loading, setLoading] = useState(false)
    const [status, setStatus] = useState('')
    const [callId, setCallId] = useState('')

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const startCampaign = async () => {
        if (!formData.phoneNumber) {
            alert('Please enter phone number')
            return
        }

        const publicUrl = formData.ngrokUrl || import.meta.env.VITE_API_URL || 'http://localhost:8001'

        try {
            setLoading(true)
            setStatus('📞 Initiating voice call...')

            // Step 1: Make outbound voice call
            const voiceResponse = await voiceAPI.initiateCall({
                phone_number: formData.phoneNumber,
                purpose: formData.campaignType,
                sector: formData.sector,
                language: formData.language,
                customer_data: {
                    name: formData.customerName,
                },
                public_url: publicUrl
            })

            const newCallId = voiceResponse.data.call_id
            setCallId(newCallId)
            setStatus('✅ Voice call initiated! Call ID: ' + newCallId)

        } catch (error) {
            console.error('Campaign error:', error)

            // Extract detailed error message
            let errorMessage = 'Unknown error'
            if (error.response) {
                // Server responded with error
                const data = error.response.data
                if (typeof data === 'string') {
                    errorMessage = data
                } else if (data?.detail) {
                    errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
                } else if (data?.message) {
                    errorMessage = data.message
                } else {
                    errorMessage = `Server error: ${error.response.status} - ${JSON.stringify(data)}`
                }
                console.error('Server error details:', error.response.data)
            } else if (error.request) {
                // Request made but no response
                errorMessage = 'No response from server. Is the backend running?'
            } else {
                // Error in request setup
                errorMessage = error.message || 'Request failed'
            }

            setStatus(`❌ Error: ${errorMessage}`)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="campaign-page container">
            <div className="page-header">
                <h1>📞 Outbound Campaign</h1>
                <p className="text-muted">
                    Make outbound voice calls with AI in your chosen language
                </p>
            </div>

            <div className="campaign-grid">
                {/* Campaign Form */}
                <div className="card campaign-form">


                    <div className="form-group">
                        <label className="form-label">Ngrok / Public URL</label>
                        <input
                            type="text"
                            className="form-input"
                            name="ngrokUrl"
                            placeholder="https://your-ngrok-url.app"
                            value={formData.ngrokUrl}
                            onChange={handleChange}
                        />
                        <small className="text-muted" style={{ display: 'block', marginTop: '0.25rem' }}>
                            Required for Twilio callbacks (must start with https://)
                        </small>
                    </div>

                    <div className="form-group">


                        <label className="form-label">Campaign Type</label>
                        <select
                            className="form-select"
                            name="campaignType"
                            value={formData.campaignType}
                            onChange={handleChange}
                        >
                            <option value="sip_debit_reminder">SIP Debit Reminder</option>
                            <option value="kyc_update_reminder">KYC Update Reminder</option>
                            <option value="sip_failure_notification">SIP Failure Notification</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Sector</label>
                        <div className="form-input" style={{ cursor: 'default' }}>Mutual Funds</div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Language</label>
                        <select
                            className="form-select"
                            name="language"
                            value={formData.language}
                            onChange={handleChange}
                        >
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="ta">Tamil</option>
                        </select>
                    </div>



                    <div className="form-group">
                        <label className="form-label">Customer Name</label>
                        <input
                            type="text"
                            className="form-input"
                            name="customerName"
                            placeholder="Rajesh Kumar"
                            value={formData.customerName}
                            onChange={handleChange}
                        />
                    </div>



                    <div className="form-group">
                        <label className="form-label">Phone Number (with country code)</label>
                        <input
                            type="text"
                            className="form-input"
                            name="phoneNumber"
                            placeholder="+919876543210"
                            value={formData.phoneNumber}
                            onChange={handleChange}
                        />
                    </div>



                    <button
                        className="btn btn-primary btn-large"
                        onClick={startCampaign}
                        disabled={loading}
                    >
                        {loading ? '⏳ Processing...' : '🚀 Start Campaign'}
                    </button>

                    {status && (
                        <div className={`status-message ${status.includes('✅') ? 'success' : status.includes('❌') ? 'error' : 'info'}`}>
                            {status}
                        </div>
                    )}

                    {callId && (
                        <div className="call-id-display">
                            <strong>Call ID:</strong> {callId}
                        </div>
                    )}
                </div>

                {/* Campaign Flow */}
                <div className="card campaign-flow">
                    <h3>Campaign Flow</h3>

                    <div className="flow-steps">
                        <div className="flow-step">
                            <div className="step-number">1</div>
                            <div className="step-content">
                                <h4>📞 Voice Call</h4>
                                <p>AI makes outbound call in selected language</p>
                                <ul>
                                    <li>Personalized greeting</li>
                                    <li>Reminder/offer details</li>
                                    <li>Capture customer response</li>
                                    <li>Call recording (with consent)</li>
                                </ul>
                            </div>
                        </div>

                        <div className="flow-arrow">↓</div>

                        <div className="flow-step">
                            <div className="step-number">2</div>
                            <div className="step-content">
                                <h4>📊 Track Results</h4>
                                <p>Monitor campaign performance</p>
                                <ul>
                                    <li>Call status</li>
                                    <li>Customer response</li>
                                    <li>Analytics</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div className="campaign-benefits">
                        <h4>✨ Benefits</h4>
                        <ul>
                            <li>✅ Automated workflow</li>
                            <li>✅ Multi-channel engagement</li>
                            <li>✅ Multilingual support</li>
                            <li>✅ Higher conversion rates</li>
                            <li>✅ Reduced manual effort</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Quick Examples */}
            <div className="card examples-section">
                <h3>📋 Quick Examples</h3>
                <div className="examples-grid">
                    <div className="example-card">
                        <h5>Campaign 1: SIP Debit Reminder</h5>
                        <p>Remind investors about upcoming SIP debit to avoid failures.</p>
                    </div>
                    <div className="example-card">
                        <h5>Campaign 2: KYC Update Reminder</h5>
                        <p>Ask investors to complete or update KYC to prevent transaction issues.</p>
                    </div>
                    <div className="example-card">
                        <h5>Campaign 3: SIP Failure Notification</h5>
                        <p>Inform investors when a SIP has failed due to insufficient balance.</p>
                    </div>
                </div>
            </div>


        </div>
    )
}

export default CampaignPage
