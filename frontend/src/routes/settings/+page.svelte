<script lang="ts">
	import { auth } from '$lib/auth.svelte';
	import { fade } from 'svelte/transition';
	import { ui } from '$lib/ui.svelte';

	async function handleLogout() {
		const confirmed = await ui.confirm('Are you sure you want to log out?', 'Logout Confirmation');
		if (confirmed) {
			auth.logout();
		}
	}
</script>

<div class="settings-container">
	<div class="settings-header">
		<h1 class="title">Settings</h1>
		<p class="subtitle">Manage your account and workspace preferences</p>
	</div>

	<div class="settings-grid">
		<section class="settings-section glass">
			<h2 class="section-title">Profile</h2>
			
			{#if auth.user}
				{@const user = auth.user}
				<div class="profile-info">
					<div class="avatar-large">
						{user.name.split(' ').map((n: string) => n[0]).join('')}
					</div>
					<div class="user-details">
						<div class="detail-group">
							<span class="detail-label">Full Name</span>
							<div class="value">{user.name}</div>
						</div>
						<div class="detail-group">
							<span class="detail-label">Email Address</span>
							<div class="value">{user.email}</div>
						</div>
						<div class="detail-group">
							<span class="detail-label">Role</span>
							<div class="value role-badge">{user.role}</div>
						</div>
					</div>
				</div>
			{/if}
		</section>

		<section class="settings-section glass">
			<h2 class="section-title">Account Actions</h2>
			<div class="actions-list">
				<button class="action-item danger" onclick={handleLogout}>
					<div class="action-icon">🚪</div>
					<div class="action-content">
						<span class="action-name">Sign Out</span>
						<span class="action-desc">Log out of your current session</span>
					</div>
				</button>
			</div>
		</section>
	</div>
</div>

<style>
	.settings-container {
		padding: 4rem;
		max-width: 1000px;
		margin: 0 auto;
		width: 100%;
	}

	.settings-header {
		margin-bottom: 3rem;
	}

	.title {
		font-size: 3.5rem;
		font-weight: 900;
		color: var(--text-primary);
		margin: 0 0 0.5rem 0;
		letter-spacing: -0.04em;
	}

	.subtitle {
		font-size: 1.1rem;
		color: var(--text-secondary);
		margin: 0;
	}

	.settings-grid {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.settings-section {
		background: var(--bg-secondary);
		border: 1.5px solid var(--border-color);
		border-radius: 1.5rem;
		padding: 2.5rem;
	}

	.section-title {
		font-size: 0.75rem;
		font-weight: 900;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		margin: 0 0 2rem 0;
	}

	.profile-info {
		display: flex;
		gap: 2.5rem;
		align-items: center;
	}

	.avatar-large {
		width: 100px;
		height: 100px;
		background: var(--accent-blue);
		border-radius: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2rem;
		font-weight: 900;
		color: white;
	}

	.user-details {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		flex: 1;
	}

	.detail-group {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.detail-label {
		font-size: 0.7rem;
		font-weight: 900;
		color: var(--text-muted);
		text-transform: uppercase;
	}

	.value {
		font-size: 1.1rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.role-badge {
		display: inline-block;
		background: #1e293b;
		padding: 0.2rem 0.6rem;
		border-radius: 0.5rem;
		font-size: 0.75rem;
		width: fit-content;
	}

	.actions-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.action-item {
		width: 100%;
		background: #0b1219;
		border: 1px solid var(--border-color);
		border-radius: 1rem;
		padding: 1.25rem;
		display: flex;
		align-items: center;
		gap: 1.25rem;
		cursor: pointer;
		text-align: left;
		transition: all 0.2s;
	}

	.action-item:hover {
		border-color: var(--text-secondary);
		background: #161e27;
	}

	.action-item.danger:hover {
		border-color: #ef4444;
		background: rgba(239, 68, 68, 0.05);
	}

	.action-icon {
		font-size: 1.5rem;
	}

	.action-content {
		display: flex;
		flex-direction: column;
	}

	.action-name {
		font-weight: 700;
		color: var(--text-primary);
	}

	.action-desc {
		font-size: 0.85rem;
		color: var(--text-muted);
	}

	.glass {
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}
</style>
