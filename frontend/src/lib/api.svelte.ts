import { auth } from './auth.svelte.ts';

const API_BASE_URL = 'http://localhost:8000/api';

export async function apiRequest(endpoint: string, method = 'GET', body?: any) {
    const token = auth.token;
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });

    if (response.status === 401) {
        if (auth.token) {
            auth.logout();
        }
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'API request failed' }));
        throw new Error(error.detail || 'API request failed');
    }

    return response.json();
}
