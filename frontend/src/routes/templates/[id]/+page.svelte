<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { fetchTemplate } from '$lib/api/templates';
	import MemeEditor from '$lib/components/MemeEditor.svelte';
	import AppHeader from '$lib/components/AppHeader.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import { onMount } from 'svelte';

	const templateId = $derived(Number($page.params.id));

	onMount(async () => {
		try {
			const template = await fetchTemplate(templateId);
			editor.setTemplate(template);
		} catch {
			goto('/');
		}
	});
</script>

{#if editor.template}
	<div class="min-h-screen bg-gray-50">
		<AppHeader />
		<main class="mx-auto max-w-6xl px-4 py-6">
			<div class="overflow-x-auto">
				<MemeEditor />
			</div>
		</main>
	</div>
{:else}
	<div class="flex min-h-screen items-center justify-center bg-gray-50">
		<p class="text-gray-500">Loading…</p>
	</div>
{/if}
