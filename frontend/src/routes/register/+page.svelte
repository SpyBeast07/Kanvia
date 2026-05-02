<script lang="ts">
	import { apiRequest } from '$lib/api/index';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let name = $state('');
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
			// 1. Sign up
			await apiRequest('/auth/signup', 'POST', { name, email, password });
			
			// 2. Automatically log in after signup
			const loginData = await apiRequest('/auth/login', 'POST', { email, password });
			auth.setToken(loginData.access_token);
			
			// 3. Fetch user info
			const user = await apiRequest('/auth/me');
			auth.setUser(user);
			
			goto('/');
		} catch (err: any) {
			error = err.message || 'Registration failed. Please try again.';
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
		
		<p class="subtitle">Create your new workspace</p>

		<form onsubmit={handleSubmit} class="auth-form">
			{#if error}
				<div class="error-banner">
					{error}
				</div>
			{/if}

			<div class="input-group">
				<label for="name">Full Name</label>
				<input 
					type="text" 
					id="name" 
					bind:value={name} 
					placeholder="Alex Johnson" 
					required 
				/>
			</div>

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
				<label for="password">Password</label>
				<input 
					type="password" 
					id="password" 
					bind:value={password} 
					placeholder="Min. 8 characters" 
					minlength="8"
					required 
				/>
			</div>

			<button type="submit" class="btn-primary" disabled={isLoading}>
				{isLoading ? 'CREATING ACCOUNT...' : 'GET STARTED'}
			</button>
		</form>

		<div class="auth-footer">
			Already have an account? <a href="/login">Sign in instead</a>
		</div>
	</div>
</div>

<style>
	/* Sharing styles with login for consistency */
	.auth-container {
		min-height: calc(100vh - 120px - 80px);
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

	label {
		color: #94a3b8;
		font-size: 0.75rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
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
