<script lang="ts">
	import { onMount } from 'svelte';
	import { projectStore } from '$lib/projects.svelte';
	import { auth } from '$lib/auth.svelte';
	import { ui } from '$lib/ui.svelte';
	import { apiRequest } from '$lib/api.svelte';
	import { goto } from '$app/navigation';

	let isLoadingUsers = $state(false);

	onMount(async () => {
		if (auth.token && auth.users.length === 0) {
			isLoadingUsers = true;
			try {
				await auth.loadUsers();
			} finally {
				isLoadingUsers = false;
			}
		}
	});

	async function handleAddProject() {
		const name = await ui.prompt('Enter project name:');
		if (!name) return;
		try {
			const newProject = await projectStore.createProject(name);
			projectStore.setCurrentProject(newProject);
			goto('/');
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}

	async function handleDeleteProject(e: MouseEvent, projectId: number, projectName: string) {
		e.stopPropagation();
		const confirmed = await ui.confirm(`Are you sure you want to delete project "${projectName}"? This action cannot be undone.`, 'Delete Project');
		if (confirmed) {
			try {
				await projectStore.deleteProject(projectId);
			} catch (err: any) {
				ui.alert(err.message, 'Error');
			}
		}
	}
	async function handleAddMember(e: MouseEvent, projectId: number, projectName: string) {
		e.stopPropagation();
		if (auth.users.length === 0) await auth.loadUsers();
		
		const userList = auth.users
			.filter(u => u.id !== auth.user?.id)
			.map(u => `${u.id}: ${u.name} (${u.email})`)
			.join('\n');
		
		const userIdStr = await ui.prompt(`Enter User ID to add to "${projectName}":\n\n${userList}`, 'Add Project Member');
		if (!userIdStr) return;
		
		const userId = parseInt(userIdStr.split(':')[0]);
		if (isNaN(userId)) {
			ui.alert('Invalid User ID', 'Error');
			return;
		}

		try {
			await apiRequest(`/projects/${projectId}/members/${userId}`, 'POST');
			ui.alert('Member added successfully', 'Success');
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}
</script>

<div class="projects-page">
	<div class="header-section">
		<div>
			<h1 class="title">Projects</h1>
			<p class="subtitle">Overview of all active workspace boards</p>
		</div>
		<button class="create-btn" onclick={handleAddProject}>
			<span class="icon">+</span> Create Project
		</button>
	</div>

	<div class="projects-grid">
		{#each projectStore.projects as project}
			<div 
				class="project-card glass" 
				role="button"
				tabindex="0"
				onclick={() => { projectStore.setCurrentProject(project); goto('/'); }}
				onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { projectStore.setCurrentProject(project); goto('/'); } }}
			>
				<div class="project-icon">📄</div>
				<div class="project-info">
					<h3 class="project-name">{project.name}</h3>
					<p class="project-meta">Created {new Date(project.created_at).toLocaleDateString()}</p>
				</div>
				<div class="project-actions">
					<button class="add-member-btn" onclick={(e) => handleAddMember(e, project.id, project.name)} title="Add Member">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
					</button>
					<button class="delete-project-btn" onclick={(e) => handleDeleteProject(e, project.id, project.name)} title="Delete Project">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
					</button>
					<div class="project-chevron">→</div>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.projects-page {
		padding: 4rem;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}

	.header-section {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
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

	.create-btn {
		background: var(--accent-blue);
		color: white;
		border: none;
		padding: 0.85rem 1.5rem;
		border-radius: 0.75rem;
		font-size: 0.85rem;
		font-weight: 900;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		transition: all 0.2s;
	}

	.create-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
	}

	.projects-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: 1.5rem;
	}

	.project-card {
		background: var(--bg-secondary);
		border: 1.5px solid var(--border-color);
		border-radius: 1.25rem;
		padding: 1.5rem;
		display: flex;
		align-items: center;
		gap: 1.5rem;
		cursor: pointer;
		text-align: left;
		transition: all 0.2s;
		width: 100%;
	}

	.project-card:hover {
		border-color: var(--accent-blue);
		transform: scale(1.02);
		background: rgba(30, 41, 59, 0.6);
	}

	.project-icon {
		width: 48px;
		height: 48px;
		background: var(--bg-primary);
		border-radius: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.5rem;
		border: 1px solid var(--border-color);
	}

	.project-info {
		flex: 1;
	}

	.project-name {
		font-size: 1.1rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 0.25rem 0;
	}

	.project-meta {
		font-size: 0.8rem;
		color: var(--text-muted);
		margin: 0;
	}

	.project-actions {
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}

	.delete-project-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0;
	}

	.project-card:hover .delete-project-btn,
	.project-card:hover .add-member-btn {
		opacity: 1;
	}

	.delete-project-btn:hover {
		background: rgba(239, 68, 68, 0.1);
		color: #ef4444;
	}

	.add-member-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0;
	}

	.add-member-btn:hover {
		background: rgba(59, 130, 246, 0.1);
		color: var(--accent-blue);
	}

	.project-chevron {
		color: var(--text-muted);
		font-size: 1.25rem;
		transition: transform 0.2s;
	}

	.project-card:hover .project-chevron {
		color: var(--accent-blue);
		transform: translateX(4px);
	}

	.glass {
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}
</style>
