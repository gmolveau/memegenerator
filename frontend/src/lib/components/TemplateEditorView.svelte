<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { fetchTemplate, updateTemplate, uploadTemplate } from '$lib/api/templates';
	import { auth } from '$lib/stores/auth.svelte';
	import { editor } from '$lib/stores/editor.svelte';
	import type { TemplateTextLayer } from '$lib/types';
	import { onMount } from 'svelte';
	import AppHeader from './AppHeader.svelte';
	import MemeEditor from './MemeEditor.svelte';

	interface Props {
		templateId?: number; // undefined = new template (upload flow)
	}

	let { templateId }: Props = $props();

	let name = $state('');
	let keywords = $state<string[]>([]);
	let keywordInput = $state('');
	let file = $state<File | null>(null);
	let previewUrl = $state<string | null>(null);
	let saving = $state(false);
	let saved = $state(false);
	let error = $state('');

	const isNew = $derived(templateId === undefined);
	const canSave = $derived(name.trim().length > 0 && keywords.length > 0 && (!isNew || !!file));

	onMount(async () => {
		await auth.init();
		if (!auth.user) {
			goto(resolve('/'));
			return;
		}
		if (templateId !== undefined) {
			try {
				const t = await fetchTemplate(templateId);
				name = t.name;
				keywords = [...t.keywords];
				editor.setTemplate(t);
			} catch {
				error = 'Template not found.';
			}
		} else {
			editor.clearTemplate();
		}
	});

	const MAX_SIZE = 3 * 1024 * 1024; // 3 MB

	function handleImageUpload(f: File) {
		if (f.size > MAX_SIZE) {
			error = 'Image must be 3 MB or smaller.';
			return;
		}
		file = f;
		if (previewUrl) URL.revokeObjectURL(previewUrl);
		previewUrl = URL.createObjectURL(f);
		editor.setTemplate({
			id: 0,
			name: name || f.name,
			keywords: [],
			image_url: previewUrl,
			created_at: '',
			text_layers: []
		});
	}

	function addKeyword() {
		const kw = keywordInput.trim();
		if (kw && !keywords.includes(kw)) keywords = [...keywords, kw];
		keywordInput = '';
	}

	function onKeywordKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ',') {
			e.preventDefault();
			addKeyword();
		} else if (e.key === 'Backspace' && keywordInput === '' && keywords.length > 0) {
			keywords = keywords.slice(0, -1);
		}
	}

	function collectLayers(): TemplateTextLayer[] {
		return editor.textLayers.map((l) => ({
			x: l.x,
			y: l.y,
			width: l.width,
			height: l.height,
			rotation: l.rotation,
			fontSize: l.fontSize,
			fontFamily: l.fontFamily,
			color: l.color,
			outlineColor: l.outlineColor,
			outlineWidth: l.outlineWidth,
			align: l.align,
			verticalAlign: l.verticalAlign,
			bold: l.bold,
			italic: l.italic,
			allCaps: l.allCaps
		}));
	}

	async function handleSave() {
		if (!canSave) return;
		saving = true;
		saved = false;
		error = '';
		try {
			const layers = collectLayers();
			if (isNew) {
				const template = await uploadTemplate(name, keywords, file!);
				if (layers.length > 0) {
					await updateTemplate(template.id, template.name, template.keywords, layers);
				}
				goto(resolve('/'));
			} else {
				await updateTemplate(templateId!, name, keywords, layers);
				saved = true;
			}
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Save failed.';
		} finally {
			saving = false;
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<AppHeader />

	<main class="mx-auto max-w-6xl px-4 py-6">
		{#if !error}
			{#if !isNew || file}
				<div class="mb-4 flex flex-col gap-2">
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-600" for="title-input-field">Name *</label>
						<input
							type="text"
							id="title-input-field"
							bind:value={name}
							placeholder="Template name"
							class="w-full rounded-lg border px-3 py-1.5 text-sm focus:ring-2 focus:outline-none {name.trim()
								.length === 0
								? 'border-red-300 focus:ring-red-400'
								: 'border-gray-300 focus:ring-indigo-500'}"
						/>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-600" for="keywords-input-field"
							>Keywords *</label
						>
						<div
							class="flex min-h-[2.25rem] flex-wrap items-center gap-1 rounded-lg border bg-white px-2 py-1 focus-within:ring-2 focus-within:ring-indigo-500 {keywords.length ===
								0 && keywordInput === ''
								? 'border-red-300'
								: 'border-gray-300'}"
						>
							{#each keywords as kw (kw)}
								<span
									class="flex items-center gap-0.5 rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700"
								>
									{kw}
									<button
										type="button"
										onclick={() => (keywords = keywords.filter((k) => k !== kw))}
										class="leading-none text-indigo-400 hover:text-indigo-700">&times;</button
									>
								</span>
							{/each}
							<input
								type="text"
								id="keywords-input-field"
								bind:value={keywordInput}
								onkeydown={onKeywordKeydown}
								onblur={addKeyword}
								placeholder={keywords.length === 0 ? 'Keywords…' : ''}
								class="min-w-[5rem] flex-1 border-none bg-transparent text-sm outline-none placeholder:text-gray-400"
							/>
						</div>
					</div>
					{#if saved}
						<p class="text-sm font-medium text-emerald-600">Saved!</p>
					{/if}
				</div>
			{/if}

			<div class="overflow-x-auto">
				<MemeEditor
					templateMode={true}
					onsave={canSave && !saving ? handleSave : undefined}
					onimageupload={isNew ? handleImageUpload : undefined}
				/>
			</div>
		{:else}
			<p class="text-red-600">{error}</p>
		{/if}
	</main>
</div>
