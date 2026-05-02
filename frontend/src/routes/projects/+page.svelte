<script lang="ts">
	import { onMount } from 'svelte';
	import { projectStore } from '../../lib/projects.svelte.ts';
	import { auth } from '../../lib/auth.svelte.ts';
	import { ui } from '../../lib/ui.svelte.ts';
	import { apiRequest } from '../../lib/api/index.ts';
	import { goto } from '$app/navigation';

	let isLoadingUsers = $state(false);
	let allUsers = $state<any[]>([]);

	onMount(async () => {
		await projectStore.loadProjects();
		if (auth.user?.role === 'ADMIN') {
			loadAllUsers();
		}
	});

	async function loadAllUsers() {
		isLoadingUsers = true;
		try {
			allUsers = await apiRequest('/users');
		} catch (err) {
			console.error('Failed to load users');
		} finally {
			isLoadingUsers = false;
		}
	}

	async function handleCreateProject() {
		const name = await ui.prompt('Enter project name:', '', 'New Project');
		if (name) {
			try {
				await projectStore.createProject(name);
				ui.alert('Project created successfully!');
			} catch (err: any) {
				ui.alert(err.message, 'Error');
			}
		}
	}

	async function handleAddMember(projectId: number) {
		const email = await ui.prompt('Enter member email to add:', '', 'Add Member');
		if (email) {
			const userToAdd = allUsers.find(u => u.email === email);
			if (!userToAdd) {
				ui.alert('User not found with this email.', 'Error');
				return;
			}
			try {
				await apiRequest(`/projects/${projectId}/members/${userToAdd.id}`, 'POST');
				ui.alert(`User ${userToAdd.name} added to project!`);
			} catch (err: any) {
				ui.alert(err.message, 'Error');
			}
		}
	}

	function selectProject(project: any) {
		projectStore.setCurrentProject(project);
		goto('/');
	}
</script>

<div class="projects-container">
	<div class="header-row">
		<div>
			<h1 class="title">Projects</h1>
			<p class="subtitle">Manage your team's workspaces</p>
		</div>
		{#if auth.user?.role === 'ADMIN'}
			<button class="btn-primary" onclick={handleCreateProject}>
				+ NEW PROJECT
			</button>
		{/if}
	</div>

	{#if projectStore.isLoading}
		<div class="loading">Loading projects...</div>
	{:else if projectStore.projects.length === 0}
		<div class="empty-state glass">
			<p>No projects found. {auth.user?.role === 'ADMIN' ? 'Create one to get started!' : 'Ask an admin to add you to a project.'}</p>
		</div>
	{:else}
		<div class="projects-grid">
			{#each projectStore.projects as project}
				<div class="project-card glass">
					<div class="card-info" onclick={() => selectProject(project)} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && selectProject(project)}>
						<div class="project-icon">📁</div>
						<div>
							<h2 class="project-name">{project.name}</h2>
							<p class="project-meta">Created {new Date(project.created_at).toLocaleDateString()}</p>
						</div>
					</div>
					
					{#if auth.user?.role === 'ADMIN'}
						<div class="card-actions">
							<button class="btn-secondary" onclick={() => handleAddMember(project.id)}>
								+ ADD MEMBER
							</button>
						</div>
					{/if}

					{#if projectStore.currentProject?.id === project.id}
						<div class="active-badge">ACTIVE</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.projects-container {
		max-width: 1000px;
		margin: 0 auto;
		padding: 2rem 4rem;
	}

	.header-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
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

	.projects-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1.5rem;
	}

	.project-card {
		position: relative;
		background: #161e27;
		border: 1.5px solid #1e293b;
		border-radius: 1.25rem;
		padding: 2rem;
		transition: transform 0.2s, border-color 0.2s;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.project-card:hover {
		transform: translateY(-4px);
		border-color: #3b82f6;
	}

	.card-info {
		display: flex;
		gap: 1.25rem;
		align-items: center;
		cursor: pointer;
	}

	.project-icon {
		width: 50px;
		height: 50px;
		background: #0b1219;
		border-radius: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.5rem;
	}

	.project-name {
		font-size: 1.25rem;
		font-weight: 800;
		color: #ffffff;
		margin-bottom: 0.25rem;
	}

	.project-meta {
		font-size: 0.85rem;
		color: #64748b;
		font-weight: 600;
	}

	.card-actions {
		border-top: 1px solid #1e293b;
		padding-top: 1rem;
	}

	.btn-secondary {
		background: transparent;
		border: 1.5px solid #1e293b;
		color: #94a3b8;
		padding: 0.5rem 1rem;
		border-radius: 0.75rem;
		font-size: 0.75rem;
		font-weight: 900;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-secondary:hover {
		border-color: #3b82f6;
		color: #ffffff;
		background: rgba(59, 130, 246, 0.1);
	}

	.active-badge {
		position: absolute;
		top: 1rem;
		right: 1rem;
		background: #3b82f6;
		color: white;
		font-size: 0.65rem;
		font-weight: 900;
		padding: 0.25rem 0.6rem;
		border-radius: 4px;
		letter-spacing: 0.05em;
	}

	.loading, .empty-state {
		text-align: center;
		padding: 4rem;
		color: #64748b;
		font-weight: 700;
	}

	.glass {
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}
</style>
