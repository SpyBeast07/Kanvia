<script lang="ts">
	import { page } from '$app/state';
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';

	let { children } = $props();

	const menuItems = [
		{ name: 'Dashboard', icon: '📊', path: '/' },
		{ name: 'Tasks', icon: '✅', path: '/tasks' },
		{ name: 'Team', icon: '🤝', path: '/team' },
		{ name: 'Settings', icon: '⚙️', path: '/settings' },
	];
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Kanvia | Task Manager</title>
</svelte:head>

<div style="display: flex; min-height: 100vh;">
	<!-- Sidebar -->
	<aside style="width: var(--sidebar-width); background: var(--sidebar-bg); border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 1000;">
		<div style="padding: 1.5rem; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.05em; background: linear-gradient(to right, #b91c1c, #ef4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
			KANVIA
		</div>
		
		<nav style="flex: 1; padding: 1rem 0;">
			{#each menuItems as item}
				{@const active = page.url.pathname === item.path}
				<a 
					href={item.path} 
					style="display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 1.5rem; font-size: 0.875rem; color: {active ? 'var(--text-primary)' : 'var(--text-secondary)'}; background: {active ? '#f1f5f9' : 'transparent'}; font-weight: {active ? '600' : '400'};"
					class="nav-item"
				>
					<span style="font-size: 1rem;">{item.icon}</span>
					{item.name}
				</a>
			{/each}
		</nav>

		<div style="padding: 1rem 1.5rem; border-top: 1px solid var(--sidebar-border);">
			<a href="/logout" style="display: flex; align-items: center; gap: 0.75rem; color: var(--accent); font-size: 0.875rem; font-weight: 600;">
				<span>🚪</span> Sign out
			</a>
		</div>
	</aside>

	<!-- Main Content Area -->
	<div style="flex: 1; margin-left: var(--sidebar-width); display: flex; flex-direction: column;">
		<!-- Header -->
		<header style="height: var(--header-height); background: white; border-bottom: 1px solid var(--sidebar-border); display: flex; align-items: center; justify-content: space-between; padding: 0 2rem; position: sticky; top: 0; z-index: 900;">
			<div style="display: flex; align-items: center; gap: 1rem;">
				<span style="font-size: 0.875rem; font-weight: 600;">Welcome back, Ishanvi</span>
				<div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
					<span style="width: 8px; height: 8px; background: #fbbf24; border-radius: 50%;"></span>
					Connecting
				</div>
			</div>
			
			<div style="display: flex; align-items: center; gap: 1.5rem;">
				<button style="background: none; border: none; cursor: pointer; font-size: 1.25rem;">🔔</button>
				<button style="background: none; border: none; cursor: pointer; font-size: 1.25rem;">📢</button>
				<div style="width: 32px; height: 32px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600;">I</div>
			</div>
		</header>

		<main style="padding: 2rem;">
			{@render children()}
		</main>
	</div>
</div>

<style>
	.nav-item:hover {
		background: #f8fafc;
		color: var(--text-primary);
	}
</style>
