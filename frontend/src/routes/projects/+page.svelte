<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import { projectStore } from '$lib/projects.svelte';
	import { auth } from '$lib/auth.svelte';
	import { ui } from '$lib/ui.svelte';
	import { apiRequest } from '$lib/api.svelte';
	import { goto } from '$app/navigation';

	let isLoadingUsers = $state(false);
	let showAddMemberModal = $state(false);
	let targetProjectId = $state<number | null>(null);
	let targetProjectName = $state('');
	let targetProjectCreatorId = $state<number | null>(null);
	let userSearchQuery = $state('');
	let projectMembers = $state<any[]>([]);

	const nonMembers = $derived(() => {
		const memberIds = projectMembers.map(m => m.id);
		return auth.users.filter(u => 
			!memberIds.includes(u.id) && 
			(u.name.toLowerCase().includes(userSearchQuery.toLowerCase()) || 
			 u.email.toLowerCase().includes(userSearchQuery.toLowerCase()))
		);
	});

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
		targetProjectId = projectId;
		targetProjectName = projectName;
		
		const project = projectStore.projects.find(p => p.id === projectId);
		targetProjectCreatorId = project?.created_by || null;
		
		showAddMemberModal = true;
		userSearchQuery = '';
		
		if (auth.users.length === 0) await auth.loadUsers();
		
		try {
			projectMembers = await apiRequest(`/projects/${projectId}/members`);
		} catch (err) {
			console.error('Failed to load project members:', err);
		}
	}

	async function submitAddMember(user: any) {
		if (targetProjectId === null) return;
		try {
			await apiRequest(`/projects/${targetProjectId}/members/${user.id}`, 'POST');
			projectMembers = [...projectMembers, { ...user, role: 'MEMBER' }];
			ui.alert(`Added ${user.name} to project`);
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}

	async function handleRemoveMember(userId: number, userName: string) {
		if (targetProjectId === null) return;
		const confirmed = await ui.confirm(`Are you sure you want to remove ${userName} from this project?`, 'Remove Member');
		if (!confirmed) return;

		try {
			await apiRequest(`/projects/${targetProjectId}/members/${userId}`, 'DELETE');
			projectMembers = projectMembers.filter(m => m.id !== userId);
			ui.alert(`Removed ${userName} from project`);
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

	{#if showAddMemberModal}
		<div 
			class="modal-overlay" 
			role="button"
			tabindex="-1"
			onclick={() => showAddMemberModal = false} 
			onkeydown={(e) => (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') && (showAddMemberModal = false)}
			transition:fade
		>
			<div 
				class="people-modal glass" 
				role="dialog"
				aria-modal="true"
				aria-labelledby="modal-title"
				tabindex="0"
				onclick={(e) => e.stopPropagation()} 
				onkeydown={(e) => e.stopPropagation()}
				transition:scale
			>
				<div class="modal-header">
					<h3 id="modal-title">Manage Members: {targetProjectName}</h3>
					<button class="close-modal-btn" onclick={() => showAddMemberModal = false}>×</button>
				</div>
				
				<div class="user-search-box">
					<input 
						type="text" 
						placeholder="Search users to add to project..." 
						bind:value={userSearchQuery}
					/>
				</div>

				{#if userSearchQuery && nonMembers().length > 0}
					<div class="search-results-mini">
						<div class="results-label">ADD TO PROJECT</div>
						{#each nonMembers() as user}
							<button class="member-row search-result" onclick={() => submitAddMember(user)}>
								<div class="user-badge-small">{user.name.split(' ').map((n: any)=>n[0]).join('')}</div>
								<div class="member-info">
									<div class="member-name">{user.name}</div>
									<div class="member-email">{user.email}</div>
								</div>
								<div class="add-icon">+</div>
							</button>
						{/each}
					</div>
				{/if}

				<div class="members-list">
					<div class="results-label">CURRENT MEMBERS</div>
					{#each projectMembers as member}
						<div class="member-row">
							<div class="user-badge">{member.name.split(' ').map((n: any)=>n[0]).join('')}</div>
							<div class="member-info">
								<div class="member-name">{member.name}</div>
								<div class="member-email">{member.email}</div>
							</div>
							<div class="member-role">{member.role}</div>
							{#if targetProjectCreatorId !== member.id && (auth.user?.role === 'ADMIN' || auth.user?.id === targetProjectCreatorId)}
								<button class="remove-member-btn" onclick={() => handleRemoveMember(member.id, member.name)} title="Remove Member">
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
								</button>
							{/if}
						</div>
					{:else}
						<div class="empty-state">No members found.</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
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

	/* Modal Styles */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(8px);
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}

	.people-modal {
		width: 100%;
		max-width: 500px;
		background: rgba(30, 41, 59, 0.8);
		border: 1px solid var(--border-color);
		border-radius: 1.5rem;
		padding: 2rem;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}

	.modal-header h3 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 800;
	}

	.close-modal-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		font-size: 2rem;
		cursor: pointer;
		line-height: 1;
	}

	.user-search-box {
		margin-bottom: 1.5rem;
	}

	.user-search-box input {
		width: 100%;
		background: rgba(15, 23, 42, 0.6);
		border: 1px solid var(--border-color);
		border-radius: 0.75rem;
		padding: 0.75rem 1rem;
		color: white;
		font-size: 1rem;
	}

	.results-label {
		font-size: 0.7rem;
		font-weight: 900;
		color: var(--text-muted);
		letter-spacing: 0.1em;
		margin-bottom: 1rem;
		text-transform: uppercase;
	}

	.members-list, .search-results-mini {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		max-height: 300px;
		overflow-y: auto;
	}

	.search-results-mini {
		margin-bottom: 2rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid var(--border-color);
	}

	.member-row {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.75rem;
		border-radius: 0.75rem;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid transparent;
		transition: all 0.2s;
		width: 100%;
		text-align: left;
	}

	.member-row.search-result {
		cursor: pointer;
	}

	.member-row.search-result:hover {
		background: rgba(59, 130, 246, 0.1);
		border-color: var(--accent-blue);
	}

	.user-badge, .user-badge-small {
		width: 40px;
		height: 40px;
		background: var(--accent-blue);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 0.9rem;
	}

	.user-badge-small {
		width: 32px;
		height: 32px;
		font-size: 0.75rem;
	}

	.member-info {
		flex: 1;
	}

	.member-name {
		font-weight: 700;
		font-size: 0.95rem;
		color: var(--text-primary);
	}

	.member-email {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.member-role {
		font-size: 0.7rem;
		font-weight: 800;
		color: var(--accent-blue);
		background: rgba(59, 130, 246, 0.1);
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
	}

	.add-icon {
		color: var(--accent-blue);
		font-size: 1.25rem;
		font-weight: 700;
	}

	.empty-state {
		text-align: center;
		padding: 2rem;
		color: var(--text-muted);
		font-style: italic;
	}

	.remove-member-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.4rem;
		border-radius: 0.4rem;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.remove-member-btn:hover {
		background: rgba(239, 68, 68, 0.1);
		color: #ef4444;
	}
</style>
