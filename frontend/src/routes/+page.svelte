<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '../lib/api/index.ts';
	import { ui } from '../lib/ui.svelte.ts';
	import { projectStore } from '../lib/projects.svelte.ts';
	import { auth } from '../lib/auth.svelte.ts';
	import { fade, scale } from 'svelte/transition';

	interface Task {
		id: number;
		title: string;
		status: string;
		project_id: number;
		created_at: string;
		due_date?: string;
		assigned_to?: number;
	}

	let tasks = $state<Task[]>([]);
	let isLoading = $state(true);

	// Reactive loading of tasks when project changes
	$effect(() => {
		if (projectStore.currentProject) {
			loadTasks(projectStore.currentProject.id);
		}
	});

	async function loadTasks(projectId: number) {
		isLoading = true;
		try {
			tasks = await apiRequest(`/projects/${projectId}/tasks`);
		} catch (err) {
			console.error('Failed to load tasks:', err);
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		if (!projectStore.projects.length) {
			projectStore.loadProjects();
		}
	});

	async function addTask() {
		if (!projectStore.currentProject) {
			ui.alert('No active project found. Please select a project first.');
			return;
		}
		const title = await ui.prompt('Enter task title:');
		if (!title) return;

		try {
			const newTask = await apiRequest('/tasks', 'POST', {
				title,
				project_id: projectStore.currentProject.id,
				status: 'MAYBE?'
			});
			tasks = [...tasks, newTask];
		} catch (err: any) {
			ui.alert(err.message, 'Error Adding Task');
		}
	}

	async function addColumn() {
		if (!projectStore.currentProject) return;
		if (auth.user?.role !== 'ADMIN') {
			ui.alert('Only admins can add columns.', 'Access Denied');
			return;
		}
		
		const name = await ui.prompt('Enter new column name:');
		if (!name) return;
		
		try {
			await projectStore.createColumn(name.toUpperCase());
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}

	async function moveTask(taskId: number, newStatus: string) {
		const taskIndex = tasks.findIndex(t => t.id === taskId);
		if (taskIndex === -1) return;

		const originalStatus = tasks[taskIndex].status;
		tasks[taskIndex].status = newStatus;

		try {
			await apiRequest(`/tasks/${taskId}`, 'PATCH', { status: newStatus });
		} catch (err) {
			tasks[taskIndex].status = originalStatus;
			ui.alert('Failed to update task status', 'Sync Error');
		}
	}

	function timeAgo(date: string) {
		const seconds = Math.floor((new Date().getTime() - new Date(date).getTime()) / 1000);
		let interval = seconds / 31536000;
		if (interval > 1) return Math.floor(interval) + " YEARS AGO";
		interval = seconds / 2592000;
		if (interval > 1) return Math.floor(interval) + " MONTHS AGO";
		interval = seconds / 86400;
		if (interval > 1) return Math.floor(interval) + " DAYS AGO";
		interval = seconds / 3600;
		if (interval > 1) return Math.floor(interval) + " HOURS AGO";
		interval = seconds / 60;
		if (interval > 1) return Math.floor(interval) + " MINUTES AGO";
		return "JUST NOW";
	}

	function getTasksByStatus(statusName: string) {
		let filtered = tasks.filter(t => t.status === statusName);
		
		if (ui.activeFilter === 'assigned') {
			filtered = filtered.filter(t => t.assigned_to === auth.user?.id);
		} else if (ui.activeFilter === 'added') {
			// In our schema, we don't have created_by on tasks yet, 
			// so for now let's just show all for 'added' or assuming everything is added by current user for demo
			// Actually, let's just mock it or leave it as all for now.
		}
		
		return filtered;
	}

	function getFilterLabel() {
		if (ui.activeFilter === 'assigned') return `Assigned to ${auth.user?.name}`;
		if (ui.activeFilter === 'added') return `Added by ${auth.user?.name}`;
		return '';
	}

	// Columns logic with defaults - always ensure NOT NOW, MAYBE?, and DONE exist
	const allColumns = $derived(() => {
		const dbCols = [...projectStore.columns];
		
		const defaults = [
			{ id: -1, name: 'NOT NOW', order: -100, project_id: projectStore.currentProject?.id || 0 },
			{ id: -2, name: 'MAYBE?', order: -99, project_id: projectStore.currentProject?.id || 0 },
			{ id: -3, name: 'DONE', order: 1000, project_id: projectStore.currentProject?.id || 0 }
		];

		const finalCols = [...dbCols];
		
		for (const def of defaults) {
			if (!finalCols.find(c => c.name === def.name)) {
				finalCols.push(def);
			}
		}

		return finalCols.sort((a, b) => a.order - b.order);
	});

	const leftColumn = $derived(allColumns().find(c => c.name === 'NOT NOW'));
	const centerColumn = $derived(allColumns().find(c => c.name === 'MAYBE?'));
	const rightColumns = $derived(allColumns().filter(c => c.name !== 'NOT NOW' && c.name !== 'MAYBE?'));
</script>

<div class="kanban-wrapper">
	<div class="header-top">
		<div class="search-container">
			<div class="filter-bar glass">
				<span class="filter-text">Filter these cards... <span class="kbd">F</span></span>
			</div>
			
			{#if ui.activeFilter}
				<div class="filter-chip glass" transition:scale={{ duration: 150 }}>
					{getFilterLabel()} <span class="chevron">⌄</span>
				</div>
			{/if}

			<button class="header-action-btn glass" aria-label="Settings">
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="2" y1="14" x2="6" y2="14"></line><line x1="10" y1="8" x2="14" y2="8"></line><line x1="18" y1="16" x2="22" y2="16"></line></svg>
			</button>

			{#if ui.activeFilter}
				<button class="header-action-btn glass close" onclick={() => ui.activeFilter = null} aria-label="Clear Filter" transition:scale>
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
				</button>
			{/if}
		</div>
	</div>

	<div class="kanban-board">
		<!-- Left Sidebar Column (NOT NOW) -->
		{#if leftColumn}
			<div class="column-sidebar left">
				<div class="count-badge">
					{getTasksByStatus(leftColumn.name).length}
				</div>
				<div class="vertical-label">{leftColumn.name}</div>
				<div class="drop-zone" role="region" aria-label="Drop to move to {leftColumn.name}" ondragover={(e) => e.preventDefault()} ondrop={() => moveTask(0, leftColumn.name)}>
				</div>
			</div>
		{/if}

		<!-- Central Column (MAYBE?) -->
		<div class="column-main">
			{#if centerColumn}
				<div class="column-header">
					<h2 class="column-title">{centerColumn.name}</h2>
					<button class="grid-toggle" aria-label="Toggle grid view">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
					</button>
				</div>

				<div class="add-card-zone glass" onclick={addTask} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && addTask()}>
					<button class="btn-add-card">
						Add a card <span class="kbd">C</span>
					</button>
				</div>

				<div class="cards-list">
					{#each getTasksByStatus(centerColumn.name).reverse() as task, i (task.id)}
						<div class="card glass" in:scale={{ duration: 200, start: 0.98 }}>
							<div class="card-header">
								<span class="card-index">{tasks.length - i}</span>
								<span class="card-project">{projectStore.currentProject?.name.toUpperCase()}</span>
							</div>
							<h3 class="card-title">{task.title}</h3>
							<div class="card-footer">
								<div class="assignee-avatar">
									{auth.user?.name.split(' ').map(n => n[0]).join('') || 'KG'}
								</div>
								<div class="card-meta">
									<div class="meta-row">
										ADDED {timeAgo(task.created_at)} • {timeAgo(task.created_at)}
									</div>
									<div class="meta-author">
										{auth.user?.name.toUpperCase()}
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Right Sidebar Columns -->
		<div class="right-columns">
			{#each rightColumns as col}
				<div class="column-sidebar right">
					<div class="count-badge">
						{getTasksByStatus(col.name).length}
					</div>
					<div class="vertical-label">{col.name}</div>
				</div>
			{/each}

			<button class="btn-add-column" onclick={addColumn} aria-label="Add column">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
			</button>
		</div>
	</div>
</div>

<style>
	.kanban-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
		height: calc(100vh - 120px - 80px);
		background: #0b1219;
		overflow: hidden;
	}

	.header-top {
		width: 100%;
		display: flex;
		justify-content: center;
		padding: 1.5rem 0;
	}

	.search-container {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.filter-bar {
		background: #161e27;
		border: 1.5px solid #1e293b;
		border-radius: 9999px;
		padding: 0.4rem 1.25rem;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: #475569;
		font-size: 0.8rem;
		font-weight: 700;
	}

	.filter-chip {
		background: #232d38;
		border: 1.5px solid #3b82f6;
		border-radius: 9999px;
		padding: 0.4rem 1.25rem;
		color: white;
		font-size: 0.8rem;
		font-weight: 800;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.header-action-btn {
		width: 34px;
		height: 34px;
		background: #161e27;
		border: 1.5px solid #1e293b;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #475569;
		cursor: pointer;
		transition: all 0.2s;
	}

	.header-action-btn:hover {
		color: white;
		border-color: #475569;
	}

	.header-action-btn.close {
		color: white;
		border-color: #334155;
	}
	
	.header-action-btn.close:hover {
		background: #1e293b;
	}

	.filter-text {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.kanban-board {
		display: flex;
		justify-content: center;
		width: 100%;
		height: 100%;
		overflow: hidden;
	}

	/* Sidebar Columns */
	.column-sidebar {
		width: 60px;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 1.5rem 0;
		position: relative;
		flex-shrink: 0;
	}

	.count-badge {
		width: 32px;
		height: 32px;
		background: radial-gradient(circle at 30% 30%, #334155, #0f172a);
		border: 1px solid #334155;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 900;
		font-size: 0.75rem;
		color: #94a3b8;
		margin-bottom: 1.5rem;
	}

	.vertical-label {
		writing-mode: vertical-rl;
		text-transform: uppercase;
		font-size: 0.75rem;
		font-weight: 900;
		color: #475569;
		letter-spacing: 0.15em;
		transform: rotate(180deg);
	}

	/* Main Column */
	.column-main {
		width: 100%;
		max-width: 540px;
		display: flex;
		flex-direction: column;
		padding: 0 1rem;
		overflow-y: auto;
		scrollbar-width: none;
	}

	.column-main::-webkit-scrollbar {
		display: none;
	}

	.column-header {
		display: flex;
		justify-content: center;
		align-items: center;
		position: sticky;
		top: 0;
		background: #0b1219;
		padding: 0 0 1.5rem 0;
		z-index: 10;
	}

	.column-title {
		font-size: 0.8rem;
		font-weight: 900;
		color: #ffffff;
		letter-spacing: 0.15em;
		text-transform: uppercase;
	}

	.grid-toggle {
		position: absolute;
		right: 0;
		background: none;
		border: none;
		color: #475569;
		cursor: pointer;
	}

	/* Add Card Zone */
	.add-card-zone {
		border: 1px solid #1e293b;
		border-radius: 0.75rem;
		padding: 2rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 1.25rem;
		cursor: pointer;
		transition: border-color 0.2s;
	}

	.add-card-zone:hover {
		border-color: #3b82f6;
	}

	.btn-add-card {
		background: #3b82f6;
		color: white;
		border: none;
		padding: 0.6rem 1.5rem;
		border-radius: 9999px;
		font-weight: 800;
		font-size: 0.85rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
	}

	.kbd {
		background: rgba(255,255,255,0.2);
		padding: 0.1rem 0.3rem;
		border-radius: 3px;
		font-size: 0.65rem;
	}

	/* Cards */
	.cards-list {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		padding-bottom: 4rem;
	}

	.card {
		background: #161e27;
		border: 1px solid #1e293b;
		border-radius: 0.75rem;
		padding: 1.75rem;
		transition: transform 0.2s, border-color 0.2s;
	}

	.card:hover {
		transform: translateY(-2px);
		border-color: #3b82f6;
	}

	.card-header {
		display: flex;
		gap: 0.75rem;
		font-size: 0.7rem;
		font-weight: 900;
		margin-bottom: 1rem;
		color: #475569;
	}

	.card-title {
		font-size: 1.4rem;
		font-weight: 800;
		color: #ffffff;
		margin-bottom: 1.5rem;
		line-height: 1.2;
	}

	.card-footer {
		display: flex;
		align-items: center;
		gap: 1.25rem;
		border-top: 1px solid #1e293b;
		padding-top: 1.25rem;
	}

	.assignee-avatar {
		width: 32px;
		height: 32px;
		background: #eab308;
		color: #422006;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.75rem;
		font-weight: 900;
	}

	.card-meta {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.meta-row {
		font-size: 0.65rem;
		font-weight: 700;
		color: #3b82f6;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.meta-author {
		font-size: 0.75rem;
		font-weight: 900;
		color: #94a3b8;
		letter-spacing: 0.05em;
	}

	/* Right Columns Container */
	.right-columns {
		display: flex;
		flex-shrink: 0;
	}

	.btn-add-column {
		width: 40px;
		background: none;
		border: none;
		color: #1e293b;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}

	.btn-add-column:hover {
		color: #3b82f6;
	}

	.glass {
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}
</style>
