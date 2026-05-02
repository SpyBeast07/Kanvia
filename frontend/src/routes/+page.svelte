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

<div style="max-width: 700px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; padding: 0 1rem;">
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

	<!-- Kanban Columns -->
	<div style="width: 100%; display: grid; grid-template-columns: 80px 1fr 80px; gap: 0; align-items: start;">
		<!-- Left Vertical Label -->
		<div style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem; padding-top: 3.5rem;">
			<div style="width: 40px; height: 40px; border: 2.5px solid #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.95rem; font-weight: 900; color: #475569;">0</div>
			<div class="vertical-label">NOT NOW</div>
		</div>

		<!-- Main Center Column -->
		<div style="display: flex; flex-direction: column; gap: 1rem;">
			<div style="text-align: center; color: #ffffff; font-size: 0.85rem; font-weight: 900; letter-spacing: 0.15em; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; padding: 0 0.75rem;">
				<span style="width: 24px;"></span>
				MAYBE?
				<span style="font-size: 1.5rem; color: #475569; cursor: pointer;">⠿</span>
			</div>

			<!-- Add Card Section -->
			<div class="glass" style="padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 120px; border: 1.5px solid #1e293b; background: #0b1219;">
				<button class="btn-primary" style="display: flex; align-items: center; gap: 0.75rem;">
					Add a card <span style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 0.35rem; font-size: 0.75rem; font-weight: 900;">C</span>
				</button>
			</div>

			<!-- Tasks -->
			<div class="glass" style="padding: 1.75rem; background: #161e27; border: 1.5px solid #1e293b;">
				<div style="font-size: 0.75rem; color: #475569; font-weight: 900; margin-bottom: 0.75rem; display: flex; gap: 0.75rem;">
					<span>11</span>
					<span style="text-transform: uppercase; letter-spacing: 0.05em;">PLAYGROUND</span>
				</div>
				<h2 style="font-size: 1.35rem; font-weight: 800; color: #ffffff; margin-bottom: 1.25rem;">First, rename this card</h2>
				<div style="display: flex; align-items: center; gap: 1.25rem;">
					<div style="width: 44px; height: 44px; background: #fbbf24; color: #451a03; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 900;">KG</div>
					<div style="font-size: 0.75rem; color: #475569; font-weight: 800; line-height: 1.5;">
						<div style="color: #64748b;">ADDED 2 DAYS AGO • 🔄 2 DAYS AGO</div>
						<div style="color: #94a3b8; font-weight: 900;">KUSHAGRA G.</div>
					</div>
				</div>
			</div>

			<div class="glass" style="padding: 1.75rem; background: #161e27; border: 1.5px solid #1e293b;">
				<div style="font-size: 0.75rem; color: #475569; font-weight: 900; margin-bottom: 0.75rem; display: flex; gap: 0.75rem;">
					<span>10</span>
					<span style="text-transform: uppercase; letter-spacing: 0.05em;">PLAYGROUND</span>
				</div>
				<h2 style="font-size: 1.35rem; font-weight: 800; color: #ffffff; margin-bottom: 1.25rem;">Second, move this card to NOT NOW</h2>
				<div style="display: flex; align-items: center; gap: 1.25rem;">
					<div style="width: 44px; height: 44px; background: #fbbf24; color: #451a03; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 900;">KG</div>
					<div style="font-size: 0.75rem; color: #475569; font-weight: 800; line-height: 1.5;">
						<div style="color: #64748b;">ADDED 2 DAYS AGO • 🔄 2 DAYS AGO</div>
						<div style="color: #94a3b8; font-weight: 900;">KUSHAGRA G.</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Right Vertical Label -->
		<div style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem; padding-top: 3.5rem;">
			<div style="display: flex; flex-direction: column; align-items: center; gap: 1.5rem;">
				<div style="width: 40px; height: 40px; border: 2.5px solid #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.95rem; font-weight: 900; color: #475569;">0</div>
				<span style="font-size: 2rem; color: #1e293b; font-weight: 900;">+</span>
			</div>
			<div class="vertical-label">DONE</div>
		</div>
	</div>
</div>

<!-- Connection Status -->
<div style="position: fixed; bottom: 4rem; right: 2rem; font-size: 0.6rem; color: #334155; opacity: 0.5;">
	{status} {#if backendData}({backendData.backend} v{backendData.version}){/if}
</div>
