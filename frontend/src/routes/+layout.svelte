<script lang="ts">
	import { page } from '$app/state';
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import { auth } from '../lib/auth.svelte.ts';
	import { apiRequest } from '../lib/api/index.ts';
	import { ui } from '../lib/ui.svelte.ts';
	import { projectStore } from '../lib/projects.svelte.ts';
	import Dialog from '../lib/components/Dialog.svelte';

	let { children } = $props();
	let showNav = $state(false);
	let showProjectMenu = $state(false);

	const menuItems = [
		{ name: 'Dashboard', icon: '📊', path: '/' },
		{ name: 'Tasks', icon: '✅', path: '/tasks' },
		{ name: 'Team', icon: '🤝', path: '/team' },
		{ name: 'Settings', icon: '⚙️', path: '/settings' }
	];

	function toggleNav() {
		showNav = !showNav;
	}

	const isAuthPage = $derived(page.url.pathname === '/login' || page.url.pathname === '/register');

	onMount(() => {
		const init = async () => {
			// If we have a token but no user, fetch user info
			if (auth.token && !auth.user) {
				try {
					const user = await apiRequest('/auth/me');
					auth.setUser(user);
				} catch (err) {
					auth.logout();
					return;
				}
			}

			// Auth Guard
			if (!auth.token && !isAuthPage) {
				goto('/login');
				return;
			}

			// Load projects if authenticated
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
			} else if (key === 'f') {
				e.preventDefault();
				document.querySelector<HTMLInputElement>('input[type="text"]')?.focus();
			} else if (key === 'c') {
				e.preventDefault();
				ui.alert('Add card triggered. Use the button in the "MAYBE?" column.');
			} else if (key === 'p') {
				e.preventDefault();
				ui.alert('Pinned triggered');
			} else if (key === 'k') {
				e.preventDefault();
				ui.alert('Search triggered');
			} else if (key === 'n') {
				e.preventDefault();
				ui.alert('Notifications triggered');
			}
		};
		window.addEventListener('keydown', handleKeydown);
		return () => window.removeEventListener('keydown', handleKeydown);
	});
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" />
	<title>Kanvia | Playground</title>
</svelte:head>

<div style="min-height: 100vh; display: flex; flex-direction: column; background: #0b1219;">
	<!-- Top Bar -->
	{#if !isAuthPage}
		<header
			style="height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; padding: 0 4rem; width: 100%;"
		>
			<!-- Logo Section -->
			<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
				<span style="font-size: 1.25rem;">🎨</span>
				<span style="font-weight: 900; font-size: 1.25rem; color: #ffffff;">Kanvia</span>
				<div
					style="background: #1e293b; color: #94a3b8; font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-weight: 900; margin-left: 0.25rem;"
				>
					J
				</div>
				<span style="font-size: 1rem; color: #475569; margin-left: 0.25rem;">⌄</span>
			</div>

			<!-- Horizontal Line Section -->
			<div style="width: 100%; display: flex; align-items: center; gap: 1.5rem;">
				<a
					href="/projects"
					style="background: #161e27; border: 1.5px solid #232d38; width: 44px; height: 44px; border-radius: 50%; color: white; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;"
					>🌐</a
				>
				<div style="flex: 1; height: 1px; background: #232d38;"></div>
				<h1 style="font-size: 2.25rem; font-weight: 900; color: #ffffff; letter-spacing: -0.04em;">
					{projectStore.currentProject?.name || 'Kanvia'}
				</h1>
				<div style="flex: 1; height: 1px; background: #232d38;"></div>
				<a
					href="/settings"
					style="background: #161e27; border: 1.5px solid #232d38; width: 44px; height: 44px; border-radius: 50%; color: white; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;"
				>
					{#if auth.user}
						<span style="font-size: 0.75rem; font-weight: 900;"
							>{auth.user.name
								.split(' ')
								.map((n) => n[0])
								.join('')}</span
						>
					{:else}
						⚙️
					{/if}
				</a>
			</div>
		</header>
	{/if}

	<!-- Main Content -->
	<main style="flex: 1; padding: 0 0 5rem 0;">
		{@render children()}
	</main>

	<!-- Bottom Bar -->
	{#if !isAuthPage}
		<footer
			style="height: var(--footer-height); position: fixed; bottom: 0; left: 0; right: 0; background: #0b1219; border-top: 1.5px solid #161e27; display: flex; align-items: center; justify-content: space-around; font-size: 0.75rem; font-weight: 900; color: #475569; letter-spacing: 0.1em; z-index: 1000; padding: 0 4rem;"
		>
			<button
				onclick={() => ui.alert('Pinned view')}
				style="background: none; border: none; color: inherit; font: inherit; cursor: pointer; display: flex; align-items: center;"
			>
				PINNED <span
					style="background: #1e293b; padding: 0.2rem 0.5rem; border-radius: 0.25rem; color: #94a3b8; margin-left: 0.75rem;"
					>P</span
				>
			</button>
			<button
				onclick={() => document.querySelector<HTMLInputElement>('input[type="text"]')?.focus()}
				style="background: none; border: none; color: inherit; font: inherit; cursor: pointer; display: flex; align-items: center;"
			>
				SEARCH <span
					style="background: #1e293b; padding: 0.2rem 0.5rem; border-radius: 0.25rem; color: #94a3b8; margin-left: 0.75rem;"
					>K</span
				>
			</button>
			<div style="display: flex; align-items: center; position: relative;">
				<button
					onclick={() => (showProjectMenu = !showProjectMenu)}
					style="background: none; border: none; color: inherit; font: inherit; cursor: pointer; display: flex; align-items: center;"
				>
					PROJECTS <span
						style="background: #1e293b; padding: 0.2rem 0.5rem; border-radius: 0.25rem; color: #94a3b8; margin-left: 0.75rem;"
						>N</span
					>
				</button>

				{#if showProjectMenu}
					<div
						transition:fade={{ duration: 100 }}
						class="glass"
						style="position: absolute; bottom: 3rem; right: 0; width: 220px; padding: 0.5rem; text-align: left; z-index: 1001; background: #161e27; border: 1.5px solid #1e293b;"
					>
						<div
							style="padding: 0.5rem; font-size: 0.65rem; color: #475569; letter-spacing: 0.1em;"
						>
							SWITCH PROJECT
						</div>
						<button
							onclick={() => {
								goto('/');
								showProjectMenu = false;
							}}
							style="width: 100%; text-align: left; padding: 0.75rem; border-radius: 0.35rem; background: transparent; border: none; color: white; cursor: pointer; font-size: 0.85rem; font-weight: 700;"
							class="project-menu-item"
						>
							{projectStore.currentProject?.name || 'Kanvia'}
						</button>
						<div style="height: 1px; background: #1e293b; margin: 0.25rem 0;"></div>
						<button
							onclick={() => {
								goto('/projects');
								showProjectMenu = false;
							}}
							style="width: 100%; text-align: left; padding: 0.75rem; border-radius: 0.35rem; background: transparent; border: none; color: #3b82f6; cursor: pointer; font-size: 0.85rem; font-weight: 800;"
							class="project-menu-item"
						>
							Manage Projects →
						</button>
					</div>
				{/if}
			</div>
		</footer>
	{/if}

	<!-- Global Nav Overlay -->
	{#if showNav}
		<div
			transition:fade={{ duration: 150 }}
			style="position: fixed; inset: 0; background: rgba(0,0,0,0.8); backdrop-filter: blur(4px); z-index: 2000; display: flex; align-items: center; justify-content: center;"
			onclick={() => (showNav = false)}
			onkeydown={(e) => e.key === 'Escape' && (showNav = false)}
			role="button"
			tabindex="0"
			aria-label="Close navigation"
		>
			<div
				class="glass"
				style="width: 350px; padding: 1rem;"
				onclick={(e) => e.stopPropagation()}
				onkeydown={(e) => e.stopPropagation()}
				role="menu"
				tabindex="-1"
			>
				<div
					style="color: var(--text-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem; padding: 0 0.5rem;"
				>
					Navigation
				</div>
				{#each menuItems as item}
					<a
						href={item.path}
						onclick={() => (showNav = false)}
						style="display: flex; align-items: center; gap: 1rem; padding: 1rem; border-radius: 0.5rem; background: {page
							.url.pathname === item.path
							? '#1e293b'
							: 'transparent'};"
						class="nav-overlay-item"
					>
						<span style="font-size: 1.25rem;">{item.icon}</span>
						<span style="font-weight: 600; font-size: 1rem;">{item.name}</span>
					</a>
				{/each}
			</div>
		</div>
	{/if}
</div>

<Dialog />

<style>
	.nav-overlay-item:hover {
		background: #1e293b !important;
	}
</style>
