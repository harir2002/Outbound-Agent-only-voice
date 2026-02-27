import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Voice API
export const voiceAPI = {
    initiateCall: (data) => api.post('/api/voice/outbound', data),
    textToSpeech: (data) => api.post('/api/voice/tts', data),
    speechToText: (formData) => api.post('/api/voice/stt', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    processQuery: (data) => api.post('/api/voice/query', data),
    getCallDetails: (callId) => api.get(`/api/voice/call/${callId}`),
    completeCall: (callId, outcome) => api.post(`/api/voice/call/${callId}/complete`, { outcome }),
    getVoices: (language) => api.get('/api/voice/voices', { params: { language } })
}

// Health check
export const healthCheck = () => api.get('/health')

export default api
