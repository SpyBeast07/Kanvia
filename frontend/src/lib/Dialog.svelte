<script lang="ts">
	import { onMount } from 'svelte';
	import { ui } from './ui.svelte.ts';
    import { fade, scale } from 'svelte/transition';

	let inputValue = $state('');

	$effect(() => {
		if (ui.dialog.show && ui.dialog.type === 'prompt') {
			inputValue = ui.dialog.inputValue || '';
		}
	});

    function handleConfirm() {
        if (ui.dialog.onConfirm) {
            ui.dialog.onConfirm(inputValue);
        } else {
            ui.close();
        }
    }

    function handleCancel() {
        if (ui.dialog.onCancel) {
            ui.dialog.onCancel();
        } else {
            ui.close();
        }
    }

	onMount(() => {
		const handleKeydown = (e: KeyboardEvent) => {
			if (!ui.dialog.show) return;

			if (e.key === 'Escape') {
				e.preventDefault();
				handleCancel();
			} else if (e.key === 'Enter' && ui.dialog.type !== 'prompt') {
				e.preventDefault();
				handleConfirm();
			}
		};

		window.addEventListener('keydown', handleKeydown);
		return () => window.removeEventListener('keydown', handleKeydown);
	});

    function focus(node: HTMLElement) {
        node.focus();
    }


</script>



{#if ui.dialog.show}
    <!-- Backdrop -->
    <div 
        class="backdrop" 
        transition:fade={{ duration: 200 }}
        onclick={handleCancel}
        onkeydown={(e) => {
            if (e.key === 'Escape') {
                handleCancel();
            } else if (e.key === 'Enter' || e.key === ' ') {
                handleCancel();
            }
        }}
        role="button"
        tabindex="-1"
        aria-label="Close dialog"
    >
        <!-- Dialog Card -->
        <div 
            class="dialog-card glass" 
            transition:scale={{ duration: 200, start: 0.95 }}
            onclick={(e) => e.stopPropagation()}
            onkeydown={(e) => {
                if (e.key === 'Enter') {
                    e.stopPropagation();
                    handleConfirm();
                } else if (e.key === 'Escape') {
                    e.stopPropagation();
                    handleCancel();
                } else {
                    // Stop other keys from bubbling to backdrop
                    e.stopPropagation();
                }
            }}
            role="dialog"
            aria-modal="true"
            tabindex="-1"
        >
            <div class="dialog-header">
                <h2 class="dialog-title">{ui.dialog.title}</h2>
            </div>
            
            <div class="dialog-body">
                <p class="dialog-message">{ui.dialog.message}</p>
                
                {#if ui.dialog.type === 'prompt'}
                    <input 
                        type="text" 
                        class="dialog-input" 
                        bind:value={inputValue} 
                        use:focus
                        placeholder="Type here..."
                    />
                {/if}
            </div>

            <div class="dialog-footer">
                {#if ui.dialog.type !== 'alert'}
                    <button class="btn-ghost" onclick={handleCancel}>
                        CANCEL
                    </button>
                {/if}
                
                <button class="btn-primary" onclick={handleConfirm}>
                    {ui.dialog.type === 'confirm' ? 'CONFIRM' : 'OK'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(8px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }

    .dialog-card {
        width: 100%;
        max-width: 440px;
        background: #161e27;
        border: 1.5px solid #1e293b;
        border-radius: 1.25rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        overflow: hidden;
    }

    .dialog-header {
        padding: 1.5rem 1.5rem 0.5rem;
    }

    .dialog-title {
        font-size: 0.75rem;
        font-weight: 900;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0;
    }

    .dialog-body {
        padding: 1rem 1.5rem 1.5rem;
    }

    .dialog-message {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        line-height: 1.5;
        margin: 0;
    }

    .dialog-input {
        width: 100%;
        background: #0b1219;
        border: 1.5px solid #1e293b;
        border-radius: 0.75rem;
        padding: 0.875rem 1rem;
        color: #ffffff;
        font-size: 1rem;
        margin-top: 1.25rem;
        transition: border-color 0.2s;
    }

    .dialog-input:focus {
        outline: none;
        border-color: #3b82f6;
    }

    .dialog-footer {
        padding: 1rem 1.5rem 1.5rem;
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
        background: rgba(0, 0, 0, 0.1);
    }

    .btn-ghost {
        background: transparent;
        border: none;
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 900;
        padding: 0.75rem 1.25rem;
        cursor: pointer;
        border-radius: 0.5rem;
        letter-spacing: 0.05em;
    }

    .btn-ghost:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #94a3b8;
    }

    .btn-primary {
        background: #ffffff;
        color: #0b1219;
        border: none;
        font-size: 0.75rem;
        font-weight: 900;
        padding: 0.75rem 1.5rem;
        cursor: pointer;
        border-radius: 0.5rem;
        letter-spacing: 0.05em;
        transition: transform 0.1s;
    }

    .btn-primary:hover {
        background: #f1f5f9;
        transform: translateY(-1px);
    }

    .btn-primary:active {
        transform: translateY(0);
    }

    .glass {
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
</style>
