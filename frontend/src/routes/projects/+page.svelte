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
			<button class="project-card glass" onclick={() => { projectStore.setCurrentProject(project); goto('/'); }}>
				<div class="project-icon">📄</div>
				<div class="project-info">
					<h3 class="project-name">{project.name}</h3>
					<p class="project-meta">Created {new Date(project.created_at).toLocaleDateString()}</p>
				</div>
				<div class="project-chevron">→</div>
			</button>
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
