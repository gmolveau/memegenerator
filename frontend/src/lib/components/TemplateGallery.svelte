<script lang="ts">
	import { untrack } from 'svelte';
	import { fetchTemplates } from '$lib/api/templates';
	import type { Template } from '$lib/types';

	interface Props {
		onselect: (template: Template) => void;
	}

	let { onselect }: Props = $props();

	const PAGE_SIZE = 40;

	let search = $state('');
	let templates = $state<Template[]>([]);
	let total = $state(0);
	let page = $state(0);
	let loading = $state(false);
	let error = $state('');

	const totalPages = $derived(Math.ceil(total / PAGE_SIZE));

	const pageWindow = $derived((): (number | '…')[] => {
		if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i);
		const pages: (number | '…')[] = [];
		const addPage = (i: number) => {
			if (pages.at(-1) !== i) pages.push(i);
		};
		addPage(0);
		if (page > 3) pages.push('…');
		for (let i = Math.max(1, page - 2); i <= Math.min(totalPages - 2, page + 2); i++) addPage(i);
		if (page < totalPages - 4) pages.push('…');
		addPage(totalPages - 1);
		return pages;
	});

	async function load() {
		loading = true;
		error = '';
		try {
			({ templates, total } = await fetchTemplates(
				search || undefined,
				PAGE_SIZE,
				page * PAGE_SIZE
			));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load templates';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		page; // track page changes; search changes are handled by the debounced oninput
		untrack(load);
	});

	let debounce: ReturnType<typeof setTimeout>;
	function onSearchInput() {
		page = 0;
		clearTimeout(debounce);
		debounce = setTimeout(load, 300);
	}

	function goToPage(p: number) {
		page = p;
	}
</script>

<div class="flex flex-col gap-4">
	<!-- Search toolbar -->
	<div class="flex gap-2">
		<input
			type="search"
			placeholder="Search templates…"
			bind:value={search}
			oninput={onSearchInput}
			class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
		/>
	</div>

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

		{#if totalPages > 1}
			<div class="mt-4 flex flex-wrap items-center justify-center gap-1">
				<button
					onclick={() => goToPage(page - 1)}
					disabled={page === 0}
					class="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40"
				>
					← Prev
				</button>

				{#each pageWindow() as p}
					{#if p === '…'}
						<span class="px-1 text-sm text-gray-400">…</span>
					{:else}
						<button
							onclick={() => goToPage(p)}
							class="rounded border px-3 py-1.5 text-sm {p === page
								? 'border-indigo-500 bg-indigo-600 text-white'
								: 'border-gray-300 text-gray-600 hover:bg-gray-50'}"
						>
							{p + 1}
						</button>
					{/if}
				{/each}

				<button
					onclick={() => goToPage(page + 1)}
					disabled={page >= totalPages - 1}
					class="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40"
				>
					Next →
				</button>
			</div>
		{/if}
	{/if}
</div>
