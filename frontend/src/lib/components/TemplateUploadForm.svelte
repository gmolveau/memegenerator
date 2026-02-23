<script lang="ts">
	import { uploadTemplate } from '$lib/api/templates';
	import type { Template } from '$lib/types';

	interface Props {
		onuploaded: (template: Template) => void;
	}

	let { onuploaded }: Props = $props();

	let uploadName = $state('');
	let uploadKeywords = $state<string[]>([]);
	let keywordInput = $state('');
	let uploadFile = $state<File | null>(null);
	let uploading = $state(false);
	let error = $state('');

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

	async function handleUpload() {
		if (!uploadFile || !uploadName.trim()) return;
		uploading = true;
		error = '';
		try {
			const t = await uploadTemplate(uploadName.trim(), uploadKeywords, uploadFile);
			uploadName = '';
			uploadKeywords = [];
			keywordInput = '';
			uploadFile = null;
			onuploaded(t);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Upload failed';
		} finally {
			uploading = false;
		}
	}
</script>

<div class="rounded-lg border border-dashed border-indigo-300 bg-indigo-50 p-4">
	<h3 class="mb-3 text-sm font-semibold text-indigo-800">Upload a template</h3>
	<div class="flex flex-col gap-2">
		<input
			type="text"
			placeholder="Template name *"
			bind:value={uploadName}
			class="rounded border border-gray-300 px-3 py-2 text-sm"
		/>

		<!-- Keyword tag input -->
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

		<!-- File picker -->
		<label
			class="flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed px-4 py-5 transition
				{uploadFile
				? 'border-indigo-400 bg-indigo-50'
				: 'border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-50'}"
		>
			{#if uploadFile}
				<span class="text-2xl">🖼️</span>
				<span class="max-w-full truncate text-xs font-medium text-indigo-700">{uploadFile.name}</span>
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

		{#if error}
			<p class="text-sm text-red-600">{error}</p>
		{/if}

		<button
			onclick={handleUpload}
			disabled={!uploadFile || !uploadName.trim() || uploading}
			class="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
		>
			{uploading ? 'Uploading…' : 'Upload'}
		</button>
	</div>
</div>
