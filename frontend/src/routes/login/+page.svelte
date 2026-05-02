<script lang="ts">
	import { apiRequest } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let isLoading = $state(false);

	onMount(() => {
		if (auth.token) {
			goto('/');
		}
	});

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = '';
		isLoading = true;

		try {
			const data = await apiRequest('/auth/login', 'POST', { email, password });
			auth.setToken(data.access_token);
			
			// Fetch user info
			const user = await apiRequest('/auth/me');
			auth.setUser(user);
			
			goto('/');
		} catch (err: any) {
			error = err.message || 'Login failed. Please check your credentials.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="auth-container">
	<div class="auth-card glass">
		<div class="logo-section">
			<span class="logo-emoji">🎨</span>
			<h1 class="logo-text">Kanvia</h1>
		</div>
		
		<p class="subtitle">Welcome back to your workspace</p>

		<form onsubmit={handleSubmit} class="auth-form">
			{#if error}
				<div class="error-banner">
					{error}
				</div>
			{/if}

			<div class="input-group">
				<label for="email">Email Address</label>
				<input 
					type="email" 
					id="email" 
					bind:value={email} 
					placeholder="name@company.com" 
					required 
				/>
			</div>

			<div class="input-group">
				<div class="label-row">
					<label for="password">Password</label>
					<a href="/forgot-password" class="forgot-link">Forgot?</a>
				</div>
				<input 
					type="password" 
					id="password" 
					bind:value={password} 
					placeholder="••••••••" 
					required 
				/>
			</div>

			<button type="submit" class="btn-primary" disabled={isLoading}>
				{isLoading ? 'SIGNING IN...' : 'SIGN IN'}
			</button>
		</form>

		<div class="auth-footer">
			Don't have an account? <a href="/register">Sign up for free</a>
		</div>
	</div>
</div>

<style>
	.auth-container {
		min-height: calc(100vh - 120px - 80px); /* Adjust for header/footer if they are still visible, but usually they shouldn't be for login */
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}

	.auth-card {
		width: 100%;
		max-width: 440px;
		padding: 3rem;
		border-radius: 1.5rem;
		background: #161e27;
		border: 1.5px solid #1e293b;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
	}

	.logo-section {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		margin-bottom: 0.5rem;
	}

	.logo-emoji {
		font-size: 2rem;
	}

	.logo-text {
		font-size: 2rem;
		font-weight: 900;
		color: #ffffff;
		letter-spacing: -0.04em;
	}

	.subtitle {
		text-align: center;
		color: #94a3b8;
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: 2.5rem;
	}

	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.error-banner {
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #ef4444;
		padding: 0.75rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		text-align: center;
	}

	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.label-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	label {
		color: #94a3b8;
		font-size: 0.75rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.forgot-link {
		color: #3b82f6;
		font-size: 0.75rem;
		font-weight: 700;
		text-decoration: none;
	}

	input {
		background: #0b1219;
		border: 1.5px solid #1e293b;
		border-radius: 0.75rem;
		padding: 0.875rem 1rem;
		color: #ffffff;
		font-size: 1rem;
		transition: border-color 0.2s, box-shadow 0.2s;
	}

	input:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
	}

	.btn-primary {
		background: #ffffff;
		color: #0b1219;
		border: none;
		border-radius: 0.75rem;
		padding: 1rem;
		font-size: 0.875rem;
		font-weight: 900;
		letter-spacing: 0.05em;
		cursor: pointer;
		transition: transform 0.1s, background 0.2s;
		margin-top: 0.5rem;
	}

	.btn-primary:hover {
		background: #f1f5f9;
		transform: translateY(-1px);
	}

	.btn-primary:active {
		transform: translateY(0);
	}

	.btn-primary:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.auth-footer {
		margin-top: 2rem;
		text-align: center;
		color: #64748b;
		font-size: 0.875rem;
		font-weight: 600;
	}

	.auth-footer a {
		color: #ffffff;
		text-decoration: none;
		font-weight: 800;
	}

	.auth-footer a:hover {
		text-decoration: underline;
	}

	.glass {
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}
</style>
