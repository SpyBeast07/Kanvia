<script lang="ts">
	import { apiRequest } from '$lib/api.svelte.ts';
	import { auth } from '$lib/auth.svelte.ts';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let isLoading = $state(false);

	onMount(() => {
		if (auth.token) goto('/');
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		isLoading = true;

		try {
			const data = await apiRequest('/auth/login', 'POST', { email, password });
			auth.setToken(data.access_token);
			auth.setUser(data.user);
			goto('/');
		} catch (err: any) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="auth-page">
	<div class="auth-card glass">
		<div class="auth-header">
			<span class="logo-icon">🎨</span>
			<h1 class="title">Welcome Back</h1>
			<p class="subtitle">Log in to your Kanvia workspace</p>
		</div>

		<form onsubmit={handleSubmit} class="auth-form">
			{#if error}
				<div class="error-msg">{error}</div>
			{/if}

			<div class="input-group">
				<label for="email">Email</label>
				<input type="email" id="email" bind:value={email} required placeholder="name@company.com" />
			</div>

			<div class="input-group">
				<label for="password">Password</label>
				<input type="password" id="password" bind:value={password} required placeholder="••••••••" />
			</div>

			<button type="submit" class="submit-btn" disabled={isLoading}>
				{isLoading ? 'Signing in...' : 'Sign in'}
			</button>
		</form>

		<div class="auth-footer">
			Don't have an account? <a href="/register">Create one</a>
		</div>
	</div>
</div>

<style>
	.auth-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background: radial-gradient(circle at top right, #1e293b, #0b1219);
	}

	.auth-card {
		width: 100%;
		max-width: 420px;
		background: rgba(22, 30, 39, 0.6);
		border: 1.5px solid var(--border-color);
		border-radius: 2rem;
		padding: 3rem;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
	}

	.auth-header {
		text-align: center;
		margin-bottom: 2.5rem;
	}

	.logo-icon { font-size: 2.5rem; display: block; margin-bottom: 1rem; }

	.title {
		font-size: 2rem;
		font-weight: 900;
		color: white;
		margin: 0 0 0.5rem 0;
		letter-spacing: -0.02em;
	}

	.subtitle {
		font-size: 0.95rem;
		color: var(--text-secondary);
		margin: 0;
	}

	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.error-msg {
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #ef4444;
		padding: 0.75rem;
		border-radius: 0.75rem;
		font-size: 0.85rem;
		font-weight: 600;
	}

	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.input-group label {
		font-size: 0.75rem;
		font-weight: 900;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.input-group input {
		background: #0b1219;
		border: 1.5px solid var(--border-color);
		border-radius: 0.75rem;
		padding: 0.85rem 1rem;
		color: white;
		font-size: 1rem;
		transition: all 0.2s;
	}

	.input-group input:focus {
		outline: none;
		border-color: var(--accent-blue);
		box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
	}

	.submit-btn {
		background: white;
		color: #0b1219;
		border: none;
		border-radius: 0.75rem;
		padding: 1rem;
		font-size: 0.85rem;
		font-weight: 900;
		cursor: pointer;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		transition: all 0.2s;
		margin-top: 0.5rem;
	}

	.submit-btn:hover:not(:disabled) {
		background: #f1f5f9;
		transform: translateY(-2px);
	}

	.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

	.auth-footer {
		margin-top: 2rem;
		text-align: center;
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.auth-footer a {
		color: white;
		font-weight: 700;
		text-decoration: none;
	}

	.auth-footer a:hover { text-decoration: underline; }

	.glass {
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}
</style>
