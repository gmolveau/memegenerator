<script lang="ts">
	import { untrack } from 'svelte';
	import { fetchTemplates, updateTemplate } from '$lib/api/templates';
	import type { Template } from '$lib/types';
	import TemplateCard from '$lib/components/TemplateCard.svelte';
	import PaginationBar from '$lib/components/PaginationBar.svelte';

	const PAGE_SIZE = 40;

	let search = $state('');
	let templates = $state<Template[]>([]);
	let total = $state(0);
	let page = $state(0);
	let loading = $state(false);
	let error = $state('');

	const totalPages = $derived(Math.ceil(total / PAGE_SIZE));

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
		editingId = null;
		page = p;
	}

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
		if (kw && !editKeywords.includes(kw)) editKeywords = [...editKeywords, kw];
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
					<TemplateCard
						{template}
						{editingId}
						bind:editName
						{editKeywords}
						bind:keywordInput
						{saving}
						{saveError}
						{canSave}
						showId
						onstartEdit={startEdit}
						oncancelEdit={cancelEdit}
						onremoveKeyword={removeKeyword}
						onkeywordKeydown={onKeywordKeydown}
						onaddKeyword={addKeyword}
						onhandleSave={handleSave}
					/>
				{/each}
			</div>

			<PaginationBar {page} {totalPages} ongotoPage={goToPage} />
		{/if}
	</main>
</div>
