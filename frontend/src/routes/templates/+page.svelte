<script lang="ts">
	import { untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { getMe, loginUrl, logout, type User } from '$lib/api/auth';
	import { fetchMyTemplates, updateTemplate } from '$lib/api/templates';
	import type { Template } from '$lib/types';
	import TemplateCard from '$lib/components/TemplateCard.svelte';
	import PaginationBar from '$lib/components/PaginationBar.svelte';

	const PAGE_SIZE = 40;

	let user = $state<User | null>(null);
	let authChecked = $state(false);

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

	$effect(() => {
		getMe().then((u) => {
			user = u;
			authChecked = true;
			if (!u) goto(loginUrl('/templates'));
		});
	});

	async function load() {
		loading = true;
		error = '';
		try {
			({ templates, total } = await fetchMyTemplates(PAGE_SIZE, page * PAGE_SIZE));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load templates';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		page;
		if (authChecked && user) untrack(load);
	});

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
	<header class="border-b bg-white shadow-sm">
		<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
			<h1 class="text-xl font-bold tracking-tight text-indigo-700">My Templates</h1>
			<div class="flex items-center gap-4">
				{#if user}
					{#if user.role === 'admin' || user.role === 'superadmin'}
						<a href="/admin" class="text-sm text-gray-500 hover:text-indigo-600">Admin</a>
					{/if}
					<span class="text-sm font-medium text-gray-700">{user.name}</span>
					<button
						onclick={() => logout().then(() => goto('/'))}
						class="text-sm text-gray-400 hover:text-red-500">(logout)</button
					>
				{/if}
				<a href="/" class="text-sm text-indigo-600 hover:underline">← Back</a>
			</div>
		</div>
	</header>

	<main class="mx-auto max-w-6xl px-4 py-8">
		{#if !authChecked}
			<!-- waiting for auth check -->
		{:else if error}
			<p class="mb-4 text-sm text-red-600">{error}</p>
		{:else if loading}
			<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
				{#each Array(PAGE_SIZE) as _}
					<div class="aspect-square animate-pulse rounded-lg bg-gray-200"></div>
				{/each}
			</div>
		{:else if templates.length === 0}
			<div class="py-16 text-center text-gray-500">
				<p class="text-lg">You haven't uploaded any templates yet.</p>
				<a href="/" class="mt-3 inline-block text-sm text-indigo-600 hover:underline"
					>Go to the gallery to upload one</a
				>
			</div>
		{:else}
			<div class="mb-4 text-sm text-gray-400">{total} template{total === 1 ? '' : 's'}</div>

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
