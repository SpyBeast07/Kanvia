<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api/index';
	import { ui } from '$lib/ui.svelte';

	interface Task {
		id: number;
		title: string;
		status: 'TODO' | 'IN_PROGRESS' | 'DONE';
		project_id: number;
		created_at: string;
		due_date?: string;
		assigned_to?: number;
	}

	interface Project {
		id: number;
		name: string;
	}

	interface BackendInfo {
		backend: string;
		version: string;
	}

	let status = $state('Loading...');
	let backendData = $state<BackendInfo | null>(null);
	let tasks = $state<Task[]>([]);
	let projects = $state<Project[]>([]);
	let currentProjectId = $state<number | null>(null);
	let isLoading = $state(true);

	async function loadData() {
		try {
			// Check backend status
			const health = await apiRequest('/status');
			backendData = health;

			// Load projects and tasks
			projects = await apiRequest('/projects');
			if (projects.length > 0) {
				currentProjectId = projects[0].id;
				tasks = await apiRequest(`/projects/${currentProjectId}/tasks`);
			}
			status = 'Connected';
		} catch (err) {
			status = 'Disconnected';
			console.error('Failed to load data:', err);
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadData();
	});

	async function addTask() {
		if (!currentProjectId) {
			ui.alert('No active project found. Please create a project first.');
			return;
		}
		const title = await ui.prompt('Enter task title:');
		if (!title) return;

		try {
			const newTask = await apiRequest('/tasks', 'POST', {
				title,
				project_id: currentProjectId,
				status: 'IN_PROGRESS'
			});
			tasks = [...tasks, newTask];
		} catch (err: any) {
			ui.alert(err.message, 'Error Adding Task');
		}
	}

	// --- Drag and Drop Logic ---
	let draggingTaskId = $state<number | null>(null);

	function onDragStart(taskId: number) {
		draggingTaskId = taskId;
	}

	async function onDrop(newStatus: 'TODO' | 'IN_PROGRESS' | 'DONE') {
		if (draggingTaskId === null) return;
		
		const taskIndex = tasks.findIndex(t => t.id === draggingTaskId);
		if (taskIndex === -1) return;

		// Optimistic Update
		const originalStatus = tasks[taskIndex].status;
		tasks[taskIndex].status = newStatus;
		const id = draggingTaskId;
		draggingTaskId = null;

		try {
			await apiRequest(`/tasks/${id}`, 'PATCH', { status: newStatus });
		} catch (err) {
			// Rollback on failure
			tasks[taskIndex].status = originalStatus;
			ui.alert('Failed to update task status', 'Sync Error');
		}
	}

	function getTasksByStatus(statusName: 'TODO' | 'IN_PROGRESS' | 'DONE') {
		return tasks.filter(t => t.status === statusName);
	}
</script>

<div style="max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; padding: 0 1rem;">
	<!-- Search/Filter Bar -->
	<div style="width: 100%; max-width: 320px; position: relative; margin-bottom: 2.5rem;">
		<input 
			type="text" 
			placeholder="Filter these cards... [F]" 
			style="width: 100%; background: #0b1219; border: 1.5px solid #1e293b; border-radius: 9999px; padding: 0.6rem 1.5rem; color: #94a3b8; font-size: 0.9rem; text-align: center; font-weight: 600;"
		/>
		<button style="position: absolute; right: 1.25rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: #64748b; cursor: pointer; font-size: 1.25rem;">
			⠿
		</button>
	</div>

	{#if isLoading}
		<div style="color: #475569; font-weight: 900; margin-top: 4rem; letter-spacing: 0.1em;">LOADING YOUR WORKSPACE...</div>
	{:else}
		<!-- Kanban Columns -->
		<div style="width: 100%; display: grid; grid-template-columns: 80px 1fr 80px; gap: 0; align-items: start;">
			
			<!-- Left Column (TODO / NOT NOW) -->
			<div 
				role="presentation"
				ondragover={(e) => e.preventDefault()} 
				ondrop={() => onDrop('TODO')}
				style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem; padding-top: 3.5rem; min-height: 400px;"
			>
				<div style="width: 40px; height: 40px; border: 2.5px solid #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.95rem; font-weight: 900; color: #475569;">
					{getTasksByStatus('TODO').length}
				</div>
				<div class="vertical-label">NOT NOW</div>
				
				{#each getTasksByStatus('TODO') as task, i}
					<div 
						role="listitem"
						draggable="true"
						ondragstart={() => onDragStart(task.id)}
						class="glass" 
						style="padding: 1rem; background: #161e27; border: 1.5px solid #1e293b; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; cursor: grab; transition: transform 0.1s;"
					>
						<span style="color: #ffffff; font-weight: 900;">{i + 1}</span>
					</div>
				{/each}
			</div>

			<!-- Center Column (IN_PROGRESS / MAYBE?) -->
			<div 
				role="presentation"
				ondragover={(e) => e.preventDefault()} 
				ondrop={() => onDrop('IN_PROGRESS')}
				style="display: flex; flex-direction: column; gap: 1rem; min-height: 400px;"
			>
				<div style="text-align: center; color: #ffffff; font-size: 0.85rem; font-weight: 900; letter-spacing: 0.15em; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; padding: 0 0.75rem;">
					<span style="width: 24px;"></span>
					MAYBE?
					<span style="font-size: 1.5rem; color: #475569; cursor: pointer;">⠿</span>
				</div>

				<!-- Add Card Section -->
				<div class="glass" style="padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 120px; border: 1.5px solid #1e293b; background: #0b1219;">
					<button onclick={addTask} class="btn-primary" style="display: flex; align-items: center; gap: 0.75rem;">
						Add a card <span style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 0.35rem; font-size: 0.75rem; font-weight: 900;">C</span>
					</button>
				</div>

				<!-- Tasks -->
				{#each getTasksByStatus('IN_PROGRESS') as task, i (task.id)}
					<div 
						role="listitem"
						draggable="true"
						ondragstart={() => onDragStart(task.id)}
						class="glass" 
						style="padding: 1.75rem; background: #161e27; border: 1.5px solid #1e293b; cursor: grab;"
					>
						<div style="font-size: 0.75rem; color: #475569; font-weight: 900; margin-bottom: 0.75rem; display: flex; gap: 0.75rem;">
							<span>{getTasksByStatus('IN_PROGRESS').length - i}</span>
							<span style="text-transform: uppercase; letter-spacing: 0.05em;">{projects.find(p => p.id === task.project_id)?.name || 'PROJECT'}</span>
						</div>
						<h2 style="font-size: 1.35rem; font-weight: 800; color: #ffffff; margin-bottom: 1.25rem;">{task.title}</h2>
						<div style="display: flex; align-items: center; gap: 1.25rem;">
							<div style="width: 44px; height: 44px; background: #fbbf24; color: #451a03; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 900;">KG</div>
							<div style="font-size: 0.75rem; color: #475569; font-weight: 800; line-height: 1.5;">
								<div style="color: #64748b;">
									{new Date(task.created_at).toLocaleDateString()} 
									{task.due_date ? `• DUE ${new Date(task.due_date).toLocaleDateString()}` : ''}
								</div>
								<div style="color: #94a3b8; font-weight: 900;">KUSHAGRA G.</div>
							</div>
						</div>
					</div>
				{/each}
			</div>

			<!-- Right Column (DONE) -->
			<div 
				role="presentation"
				ondragover={(e) => e.preventDefault()} 
				ondrop={() => onDrop('DONE')}
				style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem; padding-top: 3.5rem; min-height: 400px;"
			>
				<div style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem;">
					<div style="width: 40px; height: 40px; border: 2.5px solid #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.95rem; font-weight: 900; color: #475569;">
						{getTasksByStatus('DONE').length}
					</div>
					<span style="font-size: 2rem; color: #1e293b; font-weight: 900;">+</span>
				</div>
				<div class="vertical-label">DONE</div>

				{#each getTasksByStatus('DONE') as task, i}
					<div 
						role="listitem"
						draggable="true"
						ondragstart={() => onDragStart(task.id)}
						class="glass" 
						style="padding: 1rem; background: #161e27; border: 1.5px solid #1e293b; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; cursor: grab; opacity: 0.5;"
					>
						<span style="color: #ffffff; font-weight: 900;">{i + 1}</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Connection Status -->
<div style="position: fixed; bottom: 4rem; right: 2rem; font-size: 0.6rem; color: #334155; opacity: 0.5;">
	{status} {#if backendData}({backendData.backend} v{backendData.version}){/if}
</div>
