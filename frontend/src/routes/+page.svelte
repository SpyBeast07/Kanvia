<script lang="ts">
	import { onMount } from 'svelte';

	interface BackendInfo {
		backend: string;
		version: string;
	}

	let status = $state('Loading...');
	let backendData = $state<BackendInfo | null>(null);

	onMount(async () => {
		try {
			const res = await fetch('/api/status');
			if (res.ok) {
				backendData = await res.json();
				status = 'Connected';
			} else {
				status = 'Backend Error';
			}
		} catch (e) {
			status = 'Disconnected';
		}
	});
</script>

<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem;">
	<div>
		<h1 style="font-size: 1.75rem; color: var(--text-primary); margin-bottom: 0.25rem;">Task Board</h1>
		<p style="color: var(--text-secondary); font-size: 0.875rem;">Manage and track your team's progress in real-time.</p>
	</div>
	<button class="btn-primary">
		<span style="font-size: 1.25rem; font-weight: 400;">+</span>
		New Task
	</button>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
	<!-- To Do -->
	<div class="glass" style="padding: 1.25rem; min-height: 500px; display: flex; flex-direction: column; gap: 1rem;">
		<h3 style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
			<span style="width: 10px; height: 10px; background: #64748b; border-radius: 50%;"></span>
			To Do
		</h3>
		
		<div 
			role="button"
			tabindex="0"
			style="background: #f8fafc; border: 1px solid var(--border-color); padding: 1rem; border-radius: 0.5rem; cursor: pointer; transition: transform 0.1s;" 
			onmouseenter={(e) => e.currentTarget.style.transform='translateY(-2px)'} 
			onmouseleave={(e) => e.currentTarget.style.transform='translateY(0)'}
		>
			<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem;">Initialize Database Schema</div>
			<div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Setup PostgreSQL tables for tasks and users.</div>
			<div style="display: flex; justify-content: space-between; align-items: center;">
				<span style="background: #fee2e2; color: #991b1b; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.7rem; font-weight: 700;">HIGH</span>
				<div style="width: 24px; height: 24px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 800;">JS</div>
			</div>
		</div>
	</div>

	<!-- In Progress -->
	<div class="glass" style="padding: 1.25rem; min-height: 500px; display: flex; flex-direction: column; gap: 1rem;">
		<h3 style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
			<span style="width: 10px; height: 10px; background: #b91c1c; border-radius: 50%;"></span>
			In Progress
		</h3>
		
		<div 
			role="button"
			tabindex="0"
			style="background: #f8fafc; border: 1px solid var(--border-color); padding: 1rem; border-radius: 0.5rem; cursor: pointer;"
		>
			<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem;">UI/UX Implementation</div>
			<div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Applying the new premium design system.</div>
			<div style="display: flex; justify-content: space-between; align-items: center;">
				<span style="background: #fef3c7; color: #92400e; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.7rem; font-weight: 700;">MEDIUM</span>
				<div style="width: 24px; height: 24px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 800;">AK</div>
			</div>
		</div>
	</div>

	<!-- Done -->
	<div class="glass" style="padding: 1.25rem; min-height: 500px; display: flex; flex-direction: column; gap: 1rem;">
		<h3 style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
			<span style="width: 10px; height: 10px; background: #10b981; border-radius: 50%;"></span>
			Done
		</h3>
		
		<div style="background: #f8fafc; border: 1px solid var(--border-color); padding: 1rem; border-radius: 0.5rem; opacity: 0.7;">
			<div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem;">Project Initialization</div>
			<div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">FastAPI and SvelteKit boilerplate setup.</div>
			<div style="display: flex; justify-content: space-between; align-items: center;">
				<span style="background: #dcfce7; color: #166534; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.7rem; font-weight: 700;">LOW</span>
				<div style="width: 24px; height: 24px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 800;">AK</div>
			</div>
		</div>
	</div>
</div>

<!-- Connection Status (Bottom corner for debug) -->
<div style="position: fixed; bottom: 1rem; right: 1rem; font-size: 0.7rem; color: var(--text-secondary); opacity: 0.5;">
	Backend: {status} {#if backendData}({backendData.backend} v{backendData.version}){/if}
</div>
