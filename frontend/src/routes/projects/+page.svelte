<script lang="ts">
	let projects = [
		{ name: 'Kanvia', status: 'Active', members: 4 },
		{ name: 'Fizzy Clone', status: 'Completed', members: 2 },
		{ name: 'Marketing Website', status: 'In Review', members: 3 },
	];
</script>

<div style="max-width: 800px; margin: 0 auto; padding: 2rem;">
	<h1 style="font-size: 2.5rem; font-weight: 900; margin-bottom: 2rem;">Projects</h1>
	
	<div style="display: grid; gap: 1rem;">
		{#each projects as project}
			<div class="glass" style="padding: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
				<div>
					<h2 style="font-size: 1.25rem; font-weight: 800;">{project.name}</h2>
					<p style="color: #64748b; font-size: 0.875rem;">{project.members} members</p>
				</div>
				<div style="background: #1e293b; padding: 0.4rem 1rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; color: #94a3b8;">
					{project.status}
				</div>
			</div>
		{/each}
	</div>
</div>
