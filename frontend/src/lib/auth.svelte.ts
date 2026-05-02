import { goto } from '$app/navigation';
import { apiRequest } from './api.svelte.ts';

interface User {
    id: number;
    name: string;
    email: string;
    role: string;
    created_at: string;
}

function createAuth() {
    let _token = $state(typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null);
    let _user = $state<User | null>(null);
    let _users = $state<User[]>([]);

    return {
        get token() { return _token; },
        get user() { return _user; },
        get users() { return _users; },
        setToken(val: string | null) {
            _token = val;
            if (typeof localStorage !== 'undefined') {
                if (val) localStorage.setItem('token', val);
                else localStorage.removeItem('token');
            }
        },
        setUser(val: User | null) {
            _user = val;
        },
        async loadUsers() {
            if (!_token) return;
            try {
                _users = await apiRequest('/users');
            } catch (err) {
                console.error('Failed to load users:', err);
            }
        },
        logout() {
            this.setToken(null);
            this.setUser(null);
            _users = [];
            goto('/login');
        }
    };
}

export const auth = createAuth();
