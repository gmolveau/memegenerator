<script lang="ts">
	import { fetchTemplates, uploadTemplate } from '$lib/api/templates';
	import type { Template } from '$lib/types';

	interface Props {
		onselect: (template: Template) => void;
	}

	let { onselect }: Props = $props();

	let search = $state('');
	let templates = $state<Template[]>([]);
	let loading = $state(false);
	let error = $state('');

	// Upload state
	let uploadName = $state('');
	let uploadKeywords = $state<string[]>([]);
	let keywordInput = $state('');
	let uploadFile = $state<File | null>(null);
	let uploading = $state(false);
	let showUpload = $state(false);

	function addKeyword() {
		const kw = keywordInput.trim();
		if (kw && !uploadKeywords.includes(kw)) {
			uploadKeywords = [...uploadKeywords, kw];
		}
		keywordInput = '';
	}

	function removeKeyword(kw: string) {
		uploadKeywords = uploadKeywords.filter((k) => k !== kw);
	}

	function onKeywordKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ',') {
			e.preventDefault();
			addKeyword();
		} else if (e.key === 'Backspace' && keywordInput === '' && uploadKeywords.length > 0) {
			uploadKeywords = uploadKeywords.slice(0, -1);
		}
	}

	async function load() {
		loading = true;
		error = '';
		try {
			templates = await fetchTemplates(search || undefined);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load templates';
		} finally {
			loading = false;
		}
	}

	async function handleUpload() {
		if (!uploadFile || !uploadName.trim()) return;
		uploading = true;
		error = '';
		try {
			const t = await uploadTemplate(uploadName.trim(), uploadKeywords, uploadFile);
			templates = [t, ...templates];
			uploadName = '';
			uploadKeywords = [];
			keywordInput = '';
			uploadFile = null;
			showUpload = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Upload failed';
		} finally {
			uploading = false;
		}
	}

	$effect(() => {
		load();
	});

	let debounce: ReturnType<typeof setTimeout>;
	function onSearchInput() {
		clearTimeout(debounce);
		debounce = setTimeout(load, 300);
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

	<!-- Upload form -->
	{#if showUpload}
		<div class="rounded-lg border border-dashed border-indigo-300 bg-indigo-50 p-4">
			<h3 class="mb-3 text-sm font-semibold text-indigo-800">Upload a template</h3>
			<div class="flex flex-col gap-2">
				<input
					type="text"
					placeholder="Template name *"
					bind:value={uploadName}
					class="rounded border border-gray-300 px-3 py-2 text-sm"
				/>
				<!-- Tag input -->
				<div
					class="flex min-h-[2.5rem] flex-wrap items-center gap-1.5 rounded border border-gray-300 bg-white px-2 py-1.5 focus-within:ring-2 focus-within:ring-indigo-500"
				>
					{#each uploadKeywords as kw}
						<span
							class="flex items-center gap-1 rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700"
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
						placeholder={uploadKeywords.length === 0 ? 'Keywords — press Enter or , to add' : ''}
						class="min-w-[8rem] flex-1 border-none bg-transparent text-sm outline-none placeholder:text-gray-400"
					/>
				</div>
				<label
					class="flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed px-4 py-5 transition
						{uploadFile
						? 'border-indigo-400 bg-indigo-50'
						: 'border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-50'}"
				>
					{#if uploadFile}
						<span class="text-2xl">🖼️</span>
						<span class="max-w-full truncate text-xs font-medium text-indigo-700"
							>{uploadFile.name}</span
						>
						<span class="text-xs text-gray-400">{(uploadFile.size / 1024).toFixed(0)} KB</span>
					{:else}
						<span class="text-2xl text-gray-400">↑</span>
						<span class="text-xs text-gray-500">Click to choose an image</span>
						<span class="text-xs text-gray-400">JPEG · PNG · GIF · WEBP</span>
					{/if}
					<input
						type="file"
						accept="image/jpeg,image/png,image/gif,image/webp"
						onchange={(e) => {
							const input = e.currentTarget as HTMLInputElement;
							uploadFile = input.files?.[0] ?? null;
						}}
						class="hidden"
					/>
				</label>
				<button
					onclick={handleUpload}
					disabled={!uploadFile || !uploadName.trim() || uploading}
					class="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
				>
					{uploading ? 'Uploading…' : 'Upload'}
				</button>
			</div>
		</div>
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
					class="group relative overflow-hidden rounded-lg border-2 border-transparent bg-gray-100 transition hover:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
				>
					<img
						src={template.image_url}
						alt={template.name}
						class="aspect-square w-full object-cover"
					/>
					<div
						class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-2 opacity-0 transition group-hover:opacity-100"
					>
						<p class="truncate text-xs font-medium text-white">{template.name}</p>
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>
