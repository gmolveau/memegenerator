<script lang="ts">
	import { untrack } from 'svelte';
	import { fetchTemplates } from '$lib/api/templates';
	import type { Template } from '$lib/types';
	import TemplateUploadForm from './TemplateUploadForm.svelte';

	interface Props {
		onselect: (template: Template) => void;
	}

	let { onselect }: Props = $props();

	let search = $state('');
	let templates = $state<Template[]>([]);
	let loading = $state(false);
	let error = $state('');
	let showUpload = $state(false);

	async function load() {
		loading = true;
		error = '';
		try {
			({ templates } = await fetchTemplates(search || undefined));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load templates';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		untrack(load); // run once on mount; search changes are handled by the debounced oninput
	});

	let debounce: ReturnType<typeof setTimeout>;
	function onSearchInput() {
		clearTimeout(debounce);
		debounce = setTimeout(load, 300);
	}

	function onUploaded(template: Template) {
		templates = [template, ...templates];
		showUpload = false;
	}
</script>

<div class="flex flex-col gap-4">
	<!-- Search + Upload toolbar -->
	<div class="flex gap-2">
		<input
			type="search"
			placeholder="Search templates…"
			bind:value={search}
			oninput={onSearchInput}
			class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
		/>
		<button
			onclick={() => (showUpload = !showUpload)}
			class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
		>
			{showUpload ? 'Cancel' : '+ Upload'}
		</button>
	</div>

	{#if showUpload}
		<TemplateUploadForm onuploaded={onUploaded} />
	{/if}

	{#if error}
		<p class="text-sm text-red-600">{error}</p>
	{/if}

	<!-- Grid -->
	{#if loading}
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
			{#each Array(8) as _}
				<div class="aspect-square animate-pulse rounded-lg bg-gray-200"></div>
			{/each}
		</div>
	{:else if templates.length === 0}
		<div class="py-16 text-center text-gray-500">
			<p class="text-lg">No templates found.</p>
			<p class="text-sm">Upload one to get started!</p>
		</div>
	{:else}
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
			{#each templates as template (template.id)}
				<button
					onclick={() => onselect(template)}
					class="group overflow-hidden rounded-lg border-2 border-transparent bg-gray-100 transition hover:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
				>
					<img
						src={template.image_url}
						alt={template.name}
						loading="lazy"
						class="aspect-square w-full object-cover"
					/>
					<p class="truncate px-2 py-1.5 text-xs font-medium text-gray-700">{template.name}</p>
				</button>
			{/each}
		</div>
	{/if}
</div>
