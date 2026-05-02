<script lang="ts">
	import { page } from '$app/state';
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade, scale, slide } from 'svelte/transition';
	import { auth } from '$lib/auth.svelte';
	import { apiRequest } from '$lib/api/index';
	import { ui } from '$lib/ui.svelte';
	import { projectStore } from '$lib/projects.svelte';
	import Dialog from '$lib/components/Dialog.svelte';

	let { children } = $props();
 	let showNav = $state(false);

	let searchQuery = $state('');

	function toggleNav() {
		showNav = !showNav;
		if (showNav) searchQuery = '';
	}

	const filteredProjects = $derived(
		projectStore.projects.filter(p => 
			p.name.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);

	function handleSearchKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && filteredProjects.length > 0) {
			projectStore.setCurrentProject(filteredProjects[0]);
			goto('/');
			showNav = false;
		}
	}

	const isAuthPage = $derived(page.url.pathname === '/login' || page.url.pathname === '/register');

	onMount(() => {
		const init = async () => {
			if (auth.token && !auth.user) {
				try {
					const user = await apiRequest('/auth/me');
					auth.setUser(user);
				} catch (err) {
					auth.logout();
					return;
				}
			}

			if (!auth.token && !isAuthPage) {
				goto('/login');
				return;
			}

			if (auth.token) {
				projectStore.loadProjects();
			}
		};

		init();

		const handleKeydown = (e: KeyboardEvent) => {
			const isInput = ['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName);
			if (isInput && e.key !== 'Escape') return;

			const key = e.key.toLowerCase();
			if (key === 'j') {
				e.preventDefault();
				toggleNav();
			} else if (key === 'escape') {
				showNav = false;
			} else if (showNav) {
				if (key === '1') {
					e.preventDefault();
					ui.activeFilter = null;
					goto('/');
					showNav = false;
				} else if (key === '2') {
					e.preventDefault();
					ui.activeFilter = 'assigned';
					goto('/');
					showNav = false;
				} else if (key === '3') {
					e.preventDefault();
					ui.activeFilter = 'added';
					goto('/');
					showNav = false;
				}
			}
		};
		window.addEventListener('keydown', handleKeydown);
		return () => window.removeEventListener('keydown', handleKeydown);
	});

	async function handleAddProject() {
		const name = await ui.prompt('Enter project name:');
		if (!name) return;
		try {
			await apiRequest('/projects', 'POST', { name });
			projectStore.loadProjects();
			ui.alert('Project created successfully!');
		} catch (err: any) {
			ui.alert(err.message, 'Error');
		}
	}
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" />
	<title>Kanvia | Playground</title>
</svelte:head>

<div class="app-container">
	{#if !isAuthPage}
	<header class="main-header">
		<!-- Logo Section -->
		<button class="logo-btn" onclick={toggleNav}>
			<span class="logo-icon">🎨</span>
			<span class="logo-text">Kanvia</span>
			<div class="kbd-shortcut">J</div>
			<span class="chevron">⌄</span>
		</button>

		<!-- Horizontal Line Section -->
		<div class="header-nav">
			<a href="/projects" class="nav-circle-btn" aria-label="View Projects">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
			</a>
			<div class="header-line"></div>
			<h1 class="project-title">
				{projectStore.currentProject?.name || 'Kanvia'}
			</h1>
			<div class="header-line"></div>
			<a href="/settings" class="nav-circle-btn">
				{#if auth.user}
					<span class="initials">{auth.user.name.split(' ').map(n => n[0]).join('')}</span>
				{:else}
					⚙️
				{/if}
			</a>
		</div>
	</header>
	{/if}

	<!-- Main Content -->
	<main class="main-content">
		{@render children()}
	</main>

	<!-- Global Nav Overlay (Fizzy Style) -->
	{#if showNav}
		<div 
			transition:fade={{ duration: 150 }}
			class="overlay"
			onclick={() => showNav = false}
			role="button"
			tabindex="0"
			onkeydown={(e) => e.key === 'Escape' && (showNav = false)}
		>
			<div 
				class="nav-panel glass" 
				onclick={(e) => e.stopPropagation()}
				onkeydown={(e) => e.stopPropagation()}
				role="menu"
				tabindex="-1"
				in:scale={{ duration: 200, start: 0.95 }}
			>
				<div class="panel-search">
					<input 
						type="text" 
						bind:value={searchQuery}
						onkeydown={handleSearchKeydown}
						placeholder="Type to jump to a Projects, person, place, or tag..." 
						autofocus
					/>
				</div>

				<div class="action-grid">
					<button class="action-btn" onclick={() => { ui.activeFilter = null; goto('/'); showNav = false; }}>
						<div class="action-icon-box">
							<span class="icon">🏠</span>
							<span class="shortcut">1</span>
						</div>
						<span class="action-label">Home</span>
					</button>
					<button class="action-btn" onclick={() => { ui.activeFilter = 'assigned'; goto('/'); showNav = false; }}>
						<div class="action-icon-box">
							<span class="icon">📋</span>
							<span class="shortcut">2</span>
						</div>
						<span class="action-label">Assigned to me</span>
					</button>
					<button class="action-btn" onclick={() => { ui.activeFilter = 'added'; goto('/'); showNav = false; }}>
						<div class="action-icon-box">
							<span class="icon">👤+</span>
							<span class="shortcut">3</span>
						</div>
						<span class="action-label">Added by me</span>
					</button>
				</div>

				<div class="section-divider"></div>

				<div class="panel-sections">
					<div class="section">
						<div class="section-header">
							<span class="chevron">⌄</span> PROJECTS
						</div>
						{#if auth.user?.role === 'ADMIN'}
							<button class="section-item add" onclick={handleAddProject}>
								<span class="item-icon">+</span> Add a project
							</button>
						{/if}
						<div class="items-list">
							{#each filteredProjects as project}
								<button class="section-item" onclick={() => { projectStore.setCurrentProject(project); goto('/'); showNav = false; }}>
									<span class="item-icon">📄</span> {project.name}
								</button>
							{/each}
						</div>
					</div>

					<div class="section-divider"></div>

					<div class="section">
						<div class="section-header">
							<span class="chevron">⌄</span> SETTINGS
						</div>
						<a href="/settings" class="section-item" onclick={() => showNav = false}>
							<span class="item-icon">⚙️</span> Account Settings
						</a>
						<button class="section-item" onclick={() => { auth.logout(); showNav = false; }}>
							<span class="item-icon">🚪</span> Sign out
						</button>
					</div>
				</div>

				<div class="panel-footer">
					<div class="footer-brand">
						<strong>Kanvia™</strong> is designed, built, and backed by our team.
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<Dialog />

<style>
	:root {
		--bg-primary: #0b1219;
		--bg-secondary: #161e27;
		--border-color: #1e293b;
		--text-primary: #ffffff;
		--text-secondary: #94a3b8;
		--text-muted: #475569;
		--accent-blue: #3b82f6;
	}

	.app-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg-primary);
	}

	/* Header */
	.main-header {
		height: 120px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0 4rem;
		width: 100%;
	}

	.logo-btn {
		background: none;
		border: none;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1rem;
		cursor: pointer;
		color: var(--text-primary);
	}

	.logo-icon { font-size: 1.25rem; }
	.logo-text { font-weight: 900; font-size: 1.25rem; }
	
	.kbd-shortcut {
		background: #1e293b;
		color: var(--text-secondary);
		font-size: 0.7rem;
		padding: 0.2rem 0.5rem;
		border-radius: 0.25rem;
		font-weight: 900;
	}

	.header-nav {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}

	.nav-circle-btn {
		background: var(--bg-secondary);
		border: 1.5px solid #232d38;
		width: 44px;
		height: 44px;
		border-radius: 50%;
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.25rem;
		text-decoration: none;
	}

	.initials { font-size: 0.75rem; font-weight: 900; }

	.header-line { flex: 1; height: 1px; background: #232d38; }

	.project-title {
		font-size: 2.25rem;
		font-weight: 900;
		color: var(--text-primary);
		letter-spacing: -0.04em;
	}

	/* Overlay Panel */
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.85);
		backdrop-filter: blur(4px);
		z-index: 2000;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.nav-panel {
		width: 580px;
		background: #111827;
		border: 1px solid var(--border-color);
		border-radius: 1.5rem;
		padding: 1.5rem;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
	}

	.panel-search input {
		width: 100%;
		background: #030712;
		border: 1.5px solid var(--accent-blue);
		border-radius: 0.75rem;
		padding: 0.85rem 1.25rem;
		color: white;
		font-size: 0.95rem;
		margin-bottom: 1.5rem;
	}

	.action-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.action-btn {
		background: #1f2937;
		border: 1px solid transparent;
		border-radius: 0.75rem;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.action-btn:hover {
		background: #374151;
		border-color: var(--accent-blue);
	}

	.action-icon-box {
		position: relative;
		font-size: 1.5rem;
	}

	.shortcut {
		position: absolute;
		top: -0.5rem;
		right: -1rem;
		background: #030712;
		color: var(--text-secondary);
		font-size: 0.65rem;
		padding: 0.1rem 0.4rem;
		border-radius: 4px;
		border: 1px solid var(--border-color);
	}

	.action-label {
		font-size: 0.9rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.panel-sections {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		padding: 0 0.5rem;
	}

	.section-header {
		font-size: 0.75rem;
		font-weight: 900;
		color: var(--text-muted);
		letter-spacing: 0.1em;
		margin-bottom: 0.75rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.section-item {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.6rem 0.75rem;
		border-radius: 0.5rem;
		background: none;
		border: none;
		color: var(--text-secondary);
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		text-align: left;
		text-decoration: none;
	}

	.section-item:hover {
		background: #1f2937;
		color: white;
	}

	.items-list {
		max-height: 200px;
		overflow-y: auto;
		scrollbar-width: none;
	}

	.items-list::-webkit-scrollbar { display: none; }

	.section-divider {
		height: 1px;
		background: #1f2937;
		margin: 1rem 0;
	}

	.section-item.add { color: var(--accent-blue); }

	.panel-footer {
		margin-top: 2.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid var(--border-color);
		text-align: center;
	}

	.footer-brand {
		font-size: 0.75rem;
		color: var(--text-muted);
		line-height: 1.5;
	}

	.glass {
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}
</style>
