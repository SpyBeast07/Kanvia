<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api.svelte.ts';
	import { ui } from '$lib/ui.svelte.ts';
	import { projectStore, type Column } from '$lib/projects.svelte.ts';
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
	let columnMenuOpen = $state<number | null>(null);
	let columnHover = $state<number | null>(null);
	let columnDragOver = $state<number | null>(null);

	function findColumnAtPosition(x: number, y: number): Column | null {
		const cols = projectStore.columns;
		if (cols.length === 0) return null;
		const layout = document.querySelector('.fizzy-layout') as HTMLElement;
		if (!layout) return null;
		const rect = layout.getBoundingClientRect();
		const relativeX = x - rect.left;
		if (relativeX < 0 || relativeX > rect.width) return null;
		const colWidth = rect.width / cols.length;
		const colIdx = Math.floor(relativeX / colWidth);
		return cols[colIdx] || null;
	}

	function saveColumnState() {
		if (!projectStore.currentProject) return;
		const projectId = projectStore.currentProject.id;
		const state = {
			activeColumnId,
			gridViewColumn
		};
		localStorage.setItem(`kanvia_col_state_${projectId}`, JSON.stringify(state));
	}

	function loadColumnState() {
		if (!projectStore.currentProject) return;
		const projectId = projectStore.currentProject.id;
		const saved = localStorage.getItem(`kanvia_col_state_${projectId}`);
		if (saved) {
			try {
				const state = JSON.parse(saved);
				activeColumnId = state.activeColumnId;
				gridViewColumn = state.gridViewColumn;
			} catch (e) {
				console.error('Failed to load column state:', e);
			}
		}
	}

	$effect(() => {
		if (projectStore.currentProject) {
			loadColumnState();
		}
	});

	$effect(() => {
		activeColumnId;
		gridViewColumn;
		saveColumnState();
	});

	function isDefaultColumn(columnName: string): boolean {
		const nameLower = columnName.toLowerCase();
		return nameLower === 'maybe?' || nameLower === 'done';
	}

	function getAddedColumns() {
		const maybeIdx = projectStore.columns.findIndex(c => c.name.toLowerCase() === 'maybe?');
		const doneIdx = projectStore.columns.findIndex(c => c.name.toLowerCase() === 'done');
		if (maybeIdx === -1 || doneIdx === -1 || doneIdx <= maybeIdx) return [];
		return projectStore.columns.slice(maybeIdx + 1, doneIdx);
	}

	async function handleMoveColumn(columnId: number, direction: 'left' | 'right') {
		const addedCols = getAddedColumns();
		const currentIdx = addedCols.findIndex(c => c.id === columnId);
		if (currentIdx === -1) return;
		
		if (direction === 'left' && currentIdx > 0) {
			const targetCol = addedCols[currentIdx - 1];
			const currentCol = addedCols[currentIdx];
			await swapColumnOrder(currentCol, targetCol);
		} else if (direction === 'right' && currentIdx < addedCols.length - 1) {
			const targetCol = addedCols[currentIdx + 1];
			const currentCol = addedCols[currentIdx];
			await swapColumnOrder(currentCol, targetCol);
		}
		columnMenuOpen = null;
	}

	async function swapColumnOrder(colA: Column, colB: Column) {
		const tempOrder = colA.order;
		try {
			await apiRequest(`/columns/${colA.id}`, 'PATCH', { order: colB.order });
			await apiRequest(`/columns/${colB.id}`, 'PATCH', { order: tempOrder });
			await projectStore.loadColumns(projectStore.currentProject?.id!);
		} catch (err: any) {
			ui.alert('Failed to reorder column: ' + err.message, 'Error');
		}
	}

	async function handleDeleteColumn(columnId: number, columnName: string) {
		const confirm = await ui.confirm(`Delete column "${columnName}"? All tasks in this column will be lost.`, 'Delete Column');
		if (!confirm) return;
		try {
			await apiRequest(`/columns/${columnId}`, 'DELETE');
			await projectStore.loadColumns(projectStore.currentProject?.id!);
		} catch (err: any) {
			ui.alert('Failed to delete column: ' + err.message, 'Error');
		}
		columnMenuOpen = null;
	}

	async function handleEditColumn(column: Column) {
		const newName = await ui.prompt('Enter new column name:', 'Edit Column', column.name);
		if (!newName || newName === column.name) return;
		try {
			await apiRequest(`/columns/${column.id}`, 'PATCH', { name: newName });
			await projectStore.loadColumns(projectStore.currentProject?.id!);
		} catch (err: any) {
			ui.alert('Failed to rename column: ' + err.message, 'Error');
		}
		columnMenuOpen = null;
	}

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
						class:column-drag-over={columnDragOver === column.id}
						role="region"
						ondragover={(e) => { e.preventDefault(); columnDragOver = column.id; }}
						ondragleave={() => columnDragOver = null}
						ondrop={(e) => { handleDrop(e, column.name); columnDragOver = null; }}
					>
						<div class="center-col-header">
							{#if !isDefaultColumn(column.name)}
								<div class="col-menu-wrapper">
									<button class="col-menu-btn" onclick={() => columnMenuOpen = columnMenuOpen === column.id ? null : column.id} aria-label="Column Menu">
										<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="2"></circle><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="19" r="2"></circle></svg>
									</button>
									{#if columnMenuOpen === column.id}
										<div class="col-menu-dropdown">
											<button class="col-menu-item" onclick={() => handleEditColumn(column)}>Edit column</button>
											<button 
												class="col-menu-item" 
												disabled={getAddedColumns().length <= 1}
												onclick={() => handleMoveColumn(column.id, 'left')}
											>Move to the left</button>
											<button 
												class="col-menu-item" 
												disabled={getAddedColumns().length <= 1}
												onclick={() => handleMoveColumn(column.id, 'right')}
											>Move to the right</button>
											<button class="col-menu-item col-menu-delete" onclick={() => handleDeleteColumn(column.id, column.name)}>Delete column</button>
										</div>
									{/if}
								</div>
							{/if}
							<button 
								class="center-col-title" 
								style={!isMaybe ? 'cursor: pointer;' : ''}
								onclick={() => !isMaybe && toggleColumn(column.id)}
							>
								{column.name}
							</button>
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
						class:column-drag-over={columnDragOver === column.id}
						onclick={() => toggleColumn(column.id)}
						onmouseenter={() => columnHover = column.id}
						onmouseleave={() => columnHover = null}
						ondragenter={(e) => { e.preventDefault(); columnDragOver = column.id; }}
						ondragleave={() => columnDragOver = null}
						ondragover={(e) => { e.preventDefault(); columnDragOver = column.id; }}
						ondrop={(e) => { e.preventDefault(); handleDrop(e, column.name); columnDragOver = null; }}
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
		align-items: flex-start;
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
		position: relative;
	}

	.collapsed-column:hover {
		opacity: 0.8;
	}

	.collapsed-column.column-drag-over::before {
		content: '';
		position: absolute;
		top: 0;
		bottom: 0;
		left: 0;
		right: 0;
		border: 2px dotted var(--text-muted);
		border-radius: 8px;
		pointer-events: none;
		z-index: 10;
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
		margin: 0 0.5rem;
	}

	.center-column {
		flex: 0 1 auto;
		width: 500px;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		padding-bottom: 4rem;
		transition: box-shadow 0.2s;
		position: relative;
	}

	.center-column.column-drag-over::before {
		content: '';
		position: absolute;
		top: 0;
		bottom: 0;
		left: 0;
		right: 0;
		border: 2px dotted var(--text-muted);
		border-radius: 8px;
		pointer-events: none;
		z-index: 10;
	}

	.center-col-header {
		display: grid;
		grid-template-columns: auto 1fr auto;
		align-items: center;
		gap: 0.5rem;
	}

	.center-col-title {
		font-size: 0.85rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-primary);
		margin: 0;
		grid-column: 2;
		justify-self: stretch;
		background: none;
		border: none;
		padding: 0.5rem;
	}

	.grid-view-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		transition: color 0.2s;
		grid-column: 3;
		padding: 0.5rem;
	}

	.grid-view-btn:hover { color: white; }

	.col-menu-wrapper {
		position: relative;
		grid-column: 1;
	}

	.col-menu-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}

	.col-menu-btn:hover { color: white; }

	.col-menu-dropdown {
		position: absolute;
		top: 100%;
		left: 0;
		background: #1e293b;
		border: 1px solid var(--border-color);
		border-radius: 0.5rem;
		min-width: 160px;
		z-index: 100;
		overflow: hidden;
	}

	.col-menu-item {
		width: 100%;
		padding: 0.75rem 1rem;
		background: none;
		border: none;
		color: var(--text-primary);
		text-align: left;
		cursor: pointer;
		font-size: 0.85rem;
		transition: background 0.2s;
	}

	.col-menu-item:hover {
		background: rgba(255,255,255,0.1);
	}

	.col-menu-item:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.col-menu-item:disabled:hover {
		background: none;
	}

	.col-menu-item:hover {
		background: rgba(255,255,255,0.1);
	}

	.col-menu-delete {
		color: #ef4444;
	}

	.col-menu-delete:hover {
		background: rgba(239,68,68,0.1);
	}

	.add-card-wrapper {
		border: 1px solid rgba(59, 130, 246, 0.3);
		border-radius: 0.5rem;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		background: rgba(59, 130, 246, 0.02);
		margin: 0 0.5rem;
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
		margin: 0 0.5rem;
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
