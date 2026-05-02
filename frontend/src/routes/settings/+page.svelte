<script lang="ts">
	import { auth } from '../../lib/auth.svelte.ts';
	import { fade } from 'svelte/transition';
	import { ui } from '../../lib/ui.svelte.ts';

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
		<!-- Profile Section -->
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
						<div class="detail-group">
							<span class="detail-label">Member Since</span>
							<div class="value">{new Date(user.created_at).toLocaleDateString()}</div>
						</div>
					</div>
				</div>
			{:else}
				<p style="color: #64748b;">Loading profile...</p>
			{/if}
		</section>

		<!-- Workspace Section -->
		<section class="settings-section glass">
			<h2 class="section-title">Account Security</h2>
			<div class="security-actions">
				<button class="btn-secondary" onclick={() => ui.alert('Change password functionality is coming in the next update.', 'Coming Soon')}>
					Change Password
				</button>
				<div style="height: 1px; background: #1e293b; margin: 1rem 0;"></div>
				<button class="btn-danger" onclick={handleLogout}>
					Logout of Kanvia
				</button>
			</div>
		</section>
	</div>
</div>

<style>
	.settings-container {
		max-width: 1000px;
		margin: 0 auto;
		padding: 2rem 4rem;
	}

	.settings-header {
		margin-bottom: 3rem;
	}

	.title {
		font-size: 2.5rem;
		font-weight: 900;
		color: #ffffff;
		letter-spacing: -0.04em;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: #94a3b8;
		font-size: 1.1rem;
		font-weight: 600;
	}

	.settings-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 2rem;
	}

	.settings-section {
		background: #161e27;
		border: 1.5px solid #1e293b;
		border-radius: 1.5rem;
		padding: 2.5rem;
	}

	.section-title {
		font-size: 1.25rem;
		font-weight: 800;
		color: #ffffff;
		margin-bottom: 2rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.profile-info {
		display: flex;
		gap: 3rem;
		align-items: flex-start;
	}

	.avatar-large {
		width: 100px;
		height: 100px;
		background: #3b82f6;
		color: #ffffff;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2.5rem;
		font-weight: 900;
		flex-shrink: 0;
	}

	.user-details {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 2rem;
		flex: 1;
	}

	.detail-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.detail-label {
		color: #64748b;
		font-size: 0.75rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.value {
		color: #ffffff;
		font-size: 1.1rem;
		font-weight: 700;
	}

	.role-badge {
		background: rgba(59, 130, 246, 0.1);
		color: #3b82f6;
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		display: inline-block;
		font-size: 0.8rem;
		font-weight: 900;
		border: 1px solid rgba(59, 130, 246, 0.2);
	}

	.security-actions {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.btn-secondary {
		background: transparent;
		border: 1.5px solid #1e293b;
		color: #ffffff;
		padding: 0.75rem 1.5rem;
		border-radius: 0.75rem;
		font-weight: 700;
		cursor: pointer;
		transition: background 0.2s;
		width: fit-content;
	}

	.btn-secondary:hover {
		background: #1e293b;
	}

	.btn-danger {
		background: rgba(239, 68, 68, 0.1);
		border: 1.5px solid rgba(239, 68, 68, 0.2);
		color: #ef4444;
		padding: 0.75rem 1.5rem;
		border-radius: 0.75rem;
		font-weight: 800;
		cursor: pointer;
		transition: background 0.2s, transform 0.1s;
		width: fit-content;
	}

	.btn-danger:hover {
		background: rgba(239, 68, 68, 0.2);
		transform: translateY(-1px);
	}

	.btn-danger:active {
		transform: translateY(0);
	}

	.glass {
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}

	@media (max-width: 768px) {
		.profile-info {
			flex-direction: column;
			gap: 2rem;
			align-items: center;
			text-align: center;
		}
		.user-details {
			grid-template-columns: 1fr;
		}
	}
</style>
