<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api.svelte.ts';
	import { ui } from '$lib/ui.svelte.ts';
	import { projectStore } from '$lib/projects.svelte.ts';
	import { auth } from '$lib/auth.svelte.ts';
	import { fade, scale } from 'svelte/transition';

	interface Task {
		id: number;
		title: string;
		description: string;
		status: string;
		project_id: number;
		assigned_to: number | null;
		created_by: number;
		created_at: string;
		updated_at?: string;
	}

	let tasks = $state<Task[]>([]);
	let isLoading = $state(true);
	let activeColumnId = $state<number | null>(null);
	let draggedTaskId = $state<number | null>(null);
	let gridViewColumn = $state<string | null>(null);

	function toggleColumn(columnId: number) {
		activeColumnId = activeColumnId === columnId ? null : columnId;
	}

	function handleDragStart(e: DragEvent, taskId: number) {
		draggedTaskId = taskId;
		e.dataTransfer?.setData('text/plain', taskId.toString());
	}

	async function handleDrop(e: DragEvent, columnName: string) {
		e.preventDefault();
		const taskIdStr = e.dataTransfer?.getData('text/plain');
		if (!taskIdStr) return;
		const taskId = parseInt(taskIdStr, 10);
		
		const taskIndex = tasks.findIndex(t => t.id === taskId);
		if (taskIndex === -1) return;
		
		const previousStatus = tasks[taskIndex].status;
		if (previousStatus === columnName) {
			draggedTaskId = null;
			return;
		}

		tasks[taskIndex] = { ...tasks[taskIndex], status: columnName };
		
		try {
			await apiRequest(`/tasks/${taskId}`, 'PATCH', { status: columnName });
		} catch (err: any) {
			ui.alert('Failed to move task: ' + err.message, 'Error');
			tasks[taskIndex] = { ...tasks[taskIndex], status: previousStatus };
		}
		draggedTaskId = null;
	}

	const filteredTasks = $derived(() => {
		let result = tasks;
		if (ui.activeFilter === 'assigned' && auth.user) {
			result = result.filter(t => t.assigned_to === auth.user?.id);
		} else if (ui.activeFilter === 'added' && auth.user) {
			result = result.filter(t => t.created_by === auth.user?.id);
		}
		if (ui.taskSearchQuery) {
			const q = ui.taskSearchQuery.toLowerCase();
			result = result.filter(t => t.title.toLowerCase().includes(q) || t.description.toLowerCase().includes(q));
		}
		return result;
	});

	let searchInput: HTMLInputElement;

	$effect(() => {
		const handleKeydown = (e: KeyboardEvent) => {
			if (e.key === 'Escape' && gridViewColumn) {
				e.preventDefault();
				gridViewColumn = null;
			} else if (e.key === 'f' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
				e.preventDefault();
				searchInput?.focus();
			} else if (e.key === 'c' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
				e.preventDefault();
				const maybeCol = projectStore.columns.find(c => c.name.toLowerCase() === 'maybe?');
				if (maybeCol) handleAddTask(maybeCol.id);
			}
		};
		window.addEventListener('keydown', handleKeydown);
		return () => window.removeEventListener('keydown', handleKeydown);
	});

	async function loadTasks() {
		if (!projectStore.currentProject) return;
		isLoading = true;
		try {
			tasks = await apiRequest(`/projects/${projectStore.currentProject.id}/tasks`);
		} catch (err) {
			console.error('Failed to load tasks:', err);
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (projectStore.currentProject) {
			loadTasks();
		}
	});

	onMount(() => {
		if (projectStore.currentProject) {
			loadTasks();
		}
	});

	async function handleAddTask(columnName: string) {
		const title = await ui.prompt('Enter task title:');
		if (!title) return;
		try {
			const newTask = await apiRequest(`/tasks`, 'POST', {
				title,
				description: '',
				status: columnName,
				project_id: projectStore.currentProject?.id
			});
			tasks = [...tasks, newTask];
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}

	async function handleAddColumn() {
		const name = await ui.prompt('Enter column name:');
		if (!name) return;
		try {
			await projectStore.createColumn(name);
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}
</script>

<div class="board-container" in:fade>
	{#if gridViewColumn}
		{@const colTasks = filteredTasks().filter(t => t.status.toLowerCase() === gridViewColumn.toLowerCase())}
		<div class="grid-view-overlay">
			<div class="grid-view-header">
				<button class="back-btn" onclick={() => gridViewColumn = null}>
					Back to Playground <span class="kbd-shortcut">ESC</span>
				</button>
				<h2 class="grid-view-title">Column: {gridViewColumn}</h2>
				<div class="header-right-spacer"></div>
			</div>
			
			<div class="grid-cards-container">
				{#each colTasks as task, index}
					<div class="task-card">
						<div class="task-card-header">
							<span class="task-id">{colTasks.length - index}</span>
							<span class="task-project">{projectStore.currentProject?.name}</span>
						</div>
						<h4 class="task-title">{task.title}</h4>
						<div class="task-meta">
							<div class="user-badge-small">{auth.users.find(u => u.id === task.created_by)?.name.split(' ').map((n: string)=>n[0]).join('') || '?'}</div>
							<span class="meta-item">ADDED {new Date(task.created_at).toLocaleDateString()}</span>
							<span class="meta-item">↻ {new Date(task.updated_at || task.created_at).toLocaleDateString()}</span>
							<div class="meta-divider"></div>
							<span class="meta-item author">{auth.users.find(u => u.id === task.created_by)?.name.toUpperCase()}</span>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{:else}
		<div class="board-header">
			<div class="search-wrapper">
				<input 
					bind:this={searchInput}
					type="text" 
					class="task-search-input" 
					bind:value={ui.taskSearchQuery} 
					placeholder="Filter these cards... [F]" 
				/>
				<div class="filter-icon">
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
				</div>
			</div>
		</div>

		<div class="fizzy-layout">
			{#each projectStore.columns as column}
				{@const isMaybe = column.name.toLowerCase() === 'maybe?'}
				{@const isExpanded = isMaybe || column.id === activeColumnId}
				{@const colTasks = filteredTasks().filter(t => t.status.toLowerCase() === column.name.toLowerCase())}
				
				{#if isExpanded}
					<div 
						class="center-column"
						role="region"
						ondragover={(e) => e.preventDefault()}
						ondrop={(e) => handleDrop(e, column.name)}
					>
						<div class="center-col-header">
							<h3 
								class="center-col-title" 
								style={!isMaybe ? 'cursor: pointer;' : ''}
								onclick={() => !isMaybe && toggleColumn(column.id)}
							>
								{column.name}
							</h3>
							<button class="grid-view-btn" aria-label="Grid View" onclick={() => gridViewColumn = column.name}>
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
							</button>
						</div>
						
						{#if isMaybe}
							<div class="add-card-wrapper">
								<button class="add-card-btn" onclick={() => handleAddTask(column.name)}>
									Add a card <span class="kbd">C</span>
								</button>
							</div>
						{/if}

						<div class="tasks-list">
							{#if colTasks.length === 0}
								<div class="empty-dropzone">
									Drag cards here
								</div>
							{:else}
								{#each colTasks as task, index}
									<div 
										class="task-card"
										draggable="true"
										role="button"
										tabindex="0"
										ondragstart={(e) => handleDragStart(e, task.id)}
										style={draggedTaskId === task.id ? 'opacity: 0.5;' : ''}
									>
										<div class="task-card-header">
											<span class="task-id">{colTasks.length - index}</span>
											<span class="task-project">{projectStore.currentProject?.name}</span>
										</div>
										<h4 class="task-title">{task.title}</h4>
										<div class="task-meta">
											<div class="user-badge-small">{auth.users.find(u => u.id === task.created_by)?.name.split(' ').map((n: string)=>n[0]).join('') || '?'}</div>
											<span class="meta-item">ADDED {new Date(task.created_at).toLocaleDateString()}</span>
											<span class="meta-item">↻ {new Date(task.updated_at || task.created_at).toLocaleDateString()}</span>
											<div class="meta-divider"></div>
											<span class="meta-item author">{auth.users.find(u => u.id === task.created_by)?.name.toUpperCase()}</span>
										</div>
									</div>
								{/each}
							{/if}
						</div>
					</div>
				{:else}
					<button 
						class="collapsed-column" 
						onclick={() => toggleColumn(column.id)}
						ondragover={(e) => e.preventDefault()}
						ondrop={(e) => handleDrop(e, column.name)}
					>
						<div class="collapsed-count">{colTasks.length}</div>
						<div class="vertical-title">{column.name}</div>
					</button>
				{/if}
			{/each}

			<div class="add-col-wrapper">
				<button class="add-col-mini" onclick={handleAddColumn}>+</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.board-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		background: var(--bg-primary);
		height: calc(100vh - 120px); /* Account for header */
	}

	.board-header {
		display: flex;
		justify-content: center;
		padding: 1rem 0;
		margin-bottom: 0.5rem;
	}

	.search-wrapper {
		position: relative;
		width: 400px;
	}

	.task-search-input {
		width: 100%;
		background: transparent;
		border: 1px solid var(--border-color);
		border-radius: 20px;
		padding: 0.6rem 1rem;
		color: var(--text-primary);
		font-size: 0.85rem;
		outline: none;
		transition: border-color 0.2s;
	}

	.task-search-input:focus {
		border-color: var(--text-secondary);
	}

	.filter-icon {
		position: absolute;
		right: 1rem;
		top: 50%;
		transform: translateY(-50%);
		color: var(--text-muted);
		pointer-events: none;
	}

	.fizzy-layout {
		display: flex;
		flex: 1;
		justify-content: center;
		gap: 2rem;
		padding: 0 1rem;
		overflow: hidden;
	}

	.collapsed-column {
		width: 48px;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 2.5rem;
		background: none;
		border: none;
		cursor: pointer;
		padding-left: 0;
		padding-right: 0;
		transition: opacity 0.2s;
	}

	.collapsed-column:hover {
		opacity: 0.8;
	}

	.collapsed-count {
		width: 32px;
		height: 32px;
		background: rgba(255,255,255,0.08);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.8rem;
		font-weight: 700;
		color: var(--text-primary);
		margin-bottom: 2rem;
	}

	.vertical-title {
		writing-mode: vertical-rl;
		text-transform: uppercase;
		font-size: 0.75rem;
		font-weight: 800;
		letter-spacing: 0.1em;
		color: var(--text-secondary);
		transform: rotate(180deg);
		white-space: nowrap;
	}

	.add-col-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 2.5rem;
	}

	.add-col-mini {
		background: none;
		border: none;
		color: var(--text-secondary);
		font-size: 1.5rem;
		cursor: pointer;
		margin: 0;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}

	.add-col-mini:hover { color: white; }

	.empty-dropzone {
		border: 2px dashed rgba(255,255,255,0.1);
		border-radius: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100px;
		color: var(--text-secondary);
		font-weight: 700;
	}

	.center-column {
		flex: 0 1 auto;
		width: 500px;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		overflow-y: auto;
		padding-bottom: 4rem;
	}

	.center-col-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.center-col-title {
		font-size: 0.85rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-primary);
		margin: 0;
	}

	.grid-view-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		transition: color 0.2s;
	}

	.grid-view-btn:hover { color: white; }

	.add-card-wrapper {
		border: 1px solid rgba(59, 130, 246, 0.3);
		border-radius: 0.5rem;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		background: rgba(59, 130, 246, 0.02);
	}

	.add-card-btn {
		background: var(--accent-blue);
		color: white;
		border: none;
		padding: 0.5rem 1.25rem;
		border-radius: 20px;
		font-size: 0.85rem;
		font-weight: 700;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		transition: opacity 0.2s;
	}

	.add-card-btn:hover { opacity: 0.9; }

	.kbd {
		background: rgba(255,255,255,0.2);
		padding: 0.1rem 0.3rem;
		border-radius: 4px;
		font-size: 0.7rem;
	}

	.tasks-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.task-card {
		background: rgba(22, 30, 39, 0.4);
		border: 1px solid var(--accent-blue);
		border-radius: 0.5rem;
		padding: 1rem 1.25rem;
		transition: all 0.2s;
	}

	.task-card:hover {
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
	}

	.task-card-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--text-muted);
		margin-bottom: 0.5rem;
	}

	.task-project {
		text-transform: uppercase;
	}

	.task-title {
		font-size: 1.1rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 1rem 0;
	}

	.task-meta {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.65rem;
		font-weight: 700;
		color: var(--text-muted);
	}

	.user-badge-small {
		width: 20px;
		height: 20px;
		background: #ca8a04;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
	}

	.meta-item {
		display: flex;
		align-items: center;
	}

	.meta-divider {
		width: 1px;
		height: 10px;
		background: var(--border-color);
	}

	.author {
		color: var(--text-secondary);
	}

	.grid-view-overlay {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100%;
		padding: 0 4rem;
	}

	.grid-view-header {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		padding: 1.5rem 0;
		border-bottom: 1px solid var(--border-color);
		margin-bottom: 2rem;
		width: 100%;
		max-width: 1400px;
		margin-left: auto;
		margin-right: auto;
	}

	.back-btn {
		background: none;
		border: none;
		color: white;
		font-weight: 800;
		font-size: 1rem;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		transition: opacity 0.2s;
		text-transform: none;
		justify-self: start;
	}

	.header-right-spacer {
		justify-self: end;
	}

	.back-btn:hover {
		opacity: 0.8;
	}

	.grid-view-title {
		font-size: 1.5rem;
		font-weight: 900;
		color: white;
		margin: 0;
		justify-self: center;
	}

	.grid-cards-container {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 1.5rem;
		overflow-y: auto;
		padding-bottom: 4rem;
		max-width: 1400px;
		width: 100%;
		margin: 0 auto;
	}

	.grid-cards-container .task-card {
		width: 380px;
		flex: 0 0 auto;
	}
</style>
