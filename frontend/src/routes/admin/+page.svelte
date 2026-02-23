<script lang="ts">
	import { untrack } from 'svelte';
	import { fetchTemplates, updateTemplate } from '$lib/api/templates';
	import type { Template } from '$lib/types';

	const PAGE_SIZE = 40;

	let search = $state('');
	let templates = $state<Template[]>([]);
	let total = $state(0);
	let page = $state(0);
	let loading = $state(false);
	let error = $state('');

	const totalPages = $derived(Math.ceil(total / PAGE_SIZE));

	// Windowed page numbers: first, ellipsis, current±2, ellipsis, last
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

	// Editing state
	let editingId = $state<number | null>(null);
	let editName = $state('');
	let editKeywords = $state<string[]>([]);
	let keywordInput = $state('');
	let saving = $state(false);
	let saveError = $state('');

	async function load() {
		loading = true;
		error = '';
		try {
			({ templates, total } = await fetchTemplates(search || undefined, PAGE_SIZE, page * PAGE_SIZE));
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
		page = 0; // reset to first page on new search
		clearTimeout(debounce);
		debounce = setTimeout(load, 300);
	}

	function goToPage(p: number) {
		editingId = null;
		page = p;
	}

	// Edit helpers
	function startEdit(template: Template) {
		editingId = template.id;
		editName = template.name;
		editKeywords = [...template.keywords];
		keywordInput = '';
		saveError = '';
	}

	function cancelEdit() {
		editingId = null;
		saveError = '';
	}

	function addKeyword() {
		const kw = keywordInput.trim();
		if (kw && !editKeywords.includes(kw)) {
			editKeywords = [...editKeywords, kw];
		}
		keywordInput = '';
	}

	function removeKeyword(kw: string) {
		editKeywords = editKeywords.filter((k) => k !== kw);
	}

	function onKeywordKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ',') {
			e.preventDefault();
			addKeyword();
		} else if (e.key === 'Backspace' && keywordInput === '' && editKeywords.length > 0) {
			editKeywords = editKeywords.slice(0, -1);
		}
	}

	const canSave = $derived(editName.trim().length > 0 && editKeywords.length > 0);

	async function handleSave() {
		if (!canSave || editingId === null) return;
		saving = true;
		saveError = '';
		try {
			const updated = await updateTemplate(editingId, editName.trim(), editKeywords);
			templates = templates.map((t) => (t.id === updated.id ? updated : t));
			editingId = null;
		} catch (e) {
			saveError = e instanceof Error ? e.message : 'Save failed';
		} finally {
			saving = false;
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<header class="border-b border-gray-200 bg-white px-6 py-4">
		<div class="mx-auto flex max-w-5xl items-center justify-between">
			<h1 class="text-xl font-semibold text-gray-900">Template Admin</h1>
			<a href="/" class="text-sm text-indigo-600 hover:underline">← Back to editor</a>
		</div>
	</header>

	<main class="mx-auto max-w-5xl px-6 py-8">
		<!-- Search + count -->
		<div class="mb-6 flex items-center gap-4">
			<input
				type="search"
				placeholder="Search templates…"
				bind:value={search}
				oninput={onSearchInput}
				class="w-full max-w-sm rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
			/>
			{#if !loading}
				<span class="text-sm text-gray-400">{total} template{total === 1 ? '' : 's'}</span>
			{/if}
		</div>

		{#if error}
			<p class="mb-4 text-sm text-red-600">{error}</p>
		{/if}

		{#if loading}
			<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
				{#each Array(PAGE_SIZE) as _}
					<div class="aspect-square animate-pulse rounded-lg bg-gray-200"></div>
				{/each}
			</div>
		{:else if templates.length === 0}
			<div class="py-16 text-center text-gray-500">
				<p class="text-lg">No templates found.</p>
			</div>
		{:else}
			<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
				{#each templates as template (template.id)}
					<div
						class="overflow-hidden rounded-lg border-2 bg-white shadow-sm transition {editingId === template.id ? 'border-indigo-500' : 'border-transparent hover:border-gray-300'}"
					>
						<button
							onclick={() => (editingId === template.id ? cancelEdit() : startEdit(template))}
							class="group relative w-full overflow-hidden"
						>
							<img
								src={template.image_url}
								alt={template.name}
								loading="lazy"
								class="aspect-square w-full object-cover"
							/>
							<div
								class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition group-hover:opacity-100"
							>
								<span class="rounded bg-white px-2 py-1 text-xs font-medium text-gray-800">
									{editingId === template.id ? 'Cancel' : 'Edit'}
								</span>
							</div>
						</button>

						<div class="p-3">
							{#if editingId === template.id}
								<div class="flex flex-col gap-2">
									<input
										type="text"
										bind:value={editName}
										placeholder="Name *"
										class="rounded border px-2 py-1 text-sm focus:ring-2 focus:outline-none {editName.trim().length === 0 ? 'border-red-400 focus:ring-red-400' : 'border-gray-300 focus:ring-indigo-500'}"
									/>

									<div
										class="flex min-h-[2.25rem] flex-wrap items-center gap-1 rounded border bg-white px-2 py-1 text-sm focus-within:ring-2 focus-within:ring-indigo-500 {editKeywords.length === 0 && keywordInput === '' ? 'border-red-400' : 'border-gray-300'}"
									>
										{#each editKeywords as kw}
											<span
												class="flex items-center gap-0.5 rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700"
											>
												{kw}
												<button
													type="button"
													onclick={() => removeKeyword(kw)}
													class="leading-none text-indigo-400 hover:text-indigo-700"
													aria-label="Remove {kw}">&times;</button
												>
											</span>
										{/each}
										<input
											type="text"
											bind:value={keywordInput}
											onkeydown={onKeywordKeydown}
											onblur={addKeyword}
											placeholder={editKeywords.length === 0 ? 'Keywords *' : ''}
											class="min-w-[4rem] flex-1 border-none bg-transparent text-xs outline-none placeholder:text-gray-400"
										/>
									</div>

									{#if saveError}
										<p class="text-xs text-red-600">{saveError}</p>
									{/if}

									<div class="flex gap-2">
										<button
											onclick={handleSave}
											disabled={!canSave || saving}
											class="flex-1 rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
										>
											{saving ? 'Saving…' : 'Save'}
										</button>
										<button
											onclick={cancelEdit}
											class="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
										>
											Cancel
										</button>
									</div>
								</div>
							{:else}
								<p class="truncate text-sm font-medium text-gray-800">{template.name}</p>
								{#if template.keywords.length > 0}
									<div class="mt-1 flex flex-wrap gap-1">
										{#each template.keywords as kw}
											<span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500"
												>{kw}</span
											>
										{/each}
									</div>
								{/if}
							{/if}
						</div>
					</div>
				{/each}
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="mt-8 flex flex-wrap items-center justify-center gap-1">
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
								class="rounded border px-3 py-1.5 text-sm {p === page ? 'border-indigo-500 bg-indigo-600 text-white' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}"
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
	</main>
</div>
