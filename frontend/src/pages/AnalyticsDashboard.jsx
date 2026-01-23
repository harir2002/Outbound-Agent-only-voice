import { useState, useEffect } from 'react'
import { analyticsAPI } from '../api'

function AnalyticsDashboard() {
    const [overview, setOverview] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadAnalytics()
    }, [])

    const loadAnalytics = async () => {
        try {
            const response = await analyticsAPI.getOverview()
            setOverview(response.data.data)
        } catch (error) {
            console.error('Failed to load analytics:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div className="container"><p>Loading analytics...</p></div>

    return (
        <div className="analytics-dashboard container">
            <h1>Analytics Dashboard</h1>
            <p className="text-muted">Real-time insights and metrics</p>

            {overview && (
                <div className="analytics-grid">
                    <div className="card">
                        <h3>Total Calls</h3>
                        <div className="metric-value">{overview.total_calls}</div>
                    </div>
                    <div className="card">
                        <h3>Total Messages</h3>
                        <div className="metric-value">{overview.total_messages}</div>
                    </div>
                    <div className="card">
                        <h3>Success Rate</h3>
                        <div className="metric-value">{overview.success_rate}%</div>
                    </div>
                    <div className="card">
                        <h3>Avg Call Duration</h3>
                        <div className="metric-value">{overview.avg_call_duration}s</div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AnalyticsDashboard
