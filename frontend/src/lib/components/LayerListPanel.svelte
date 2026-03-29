<script lang="ts">
	import { editor } from '$lib/stores/editor.svelte';
	import type { TextLayer } from '$lib/types';

	interface Props {
		canvasWidth: number;
	}

	let { canvasWidth }: Props = $props();

	// eslint-disable-next-line svelte/prefer-writable-derived
	let expandedId = $state<string | null>(null);

	$effect(() => {
		expandedId = editor.selectedLayerId;
	});

	function toggleLayer(id: string) {
		editor.selectLayer(id);
		expandedId = expandedId === id ? null : id;
	}

	// Delete selected layer with the Delete key.
	// Skips when an input/textarea/select has focus (e.g. inline text editing, panel fields).
	$effect(() => {
		function onKeyDown(e: KeyboardEvent) {
			if (e.key !== 'Delete' && e.key !== 'Backspace') return;
			const tag = (document.activeElement as HTMLElement)?.tagName;
			if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
			const id = editor.selectedLayerId;
			if (!id) return;
			e.preventDefault();
			if (editor.textLayers.some((l) => l.id === id)) {
				editor.removeTextLayer(id);
			} else {
				editor.removeImageLayer(id);
			}
		}
		window.addEventListener('keydown', onKeyDown);
		return () => window.removeEventListener('keydown', onKeyDown);
	});
</script>

<div class="flex w-full flex-col gap-2 lg:w-64">
	<p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">Layers</p>

	{#if editor.textLayers.length === 0 && editor.imageLayers.length === 0}
		<div class="rounded-lg border border-dashed p-4 text-center text-xs text-gray-400">
			No layers yet.<br />Add text or an image overlay.
		</div>
	{/if}

	{#each editor.textLayers as layer (layer.id)}
		{@const isSelected = editor.selectedLayerId === layer.id}
		{@const isExpanded = expandedId === layer.id}
		<div
			class="overflow-hidden rounded-lg border {isSelected
				? 'border-indigo-400'
				: 'border-gray-200'}"
		>
			<button
				onclick={() => toggleLayer(layer.id)}
				class="flex w-full items-center gap-2 px-3 py-2 text-left {isSelected
					? 'bg-indigo-50'
					: 'hover:bg-gray-50'}"
			>
				<span
					class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-indigo-200 text-xs font-bold text-indigo-700"
					>T</span
				>
				<span class="flex-1 truncate text-xs text-gray-700">{layer.text || 'Text'}</span>
				<span class="text-xs text-gray-400">{isExpanded ? '▲' : '▼'}</span>
			</button>

			{#if isExpanded}
				<div class="flex flex-col gap-2 border-t bg-white px-3 py-2">
					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Content</span>
						<textarea
							rows="2"
							value={layer.text}
							oninput={(e) =>
								editor.updateTextLayer(layer.id, {
									text: (e.currentTarget as HTMLTextAreaElement).value
								})}
							class="rounded border border-gray-300 px-2 py-1 text-xs"
						></textarea>
					</label>

					<div class="flex gap-3">
						<label class="flex items-center gap-1 text-xs">
							<input
								type="checkbox"
								checked={layer.bold}
								onchange={(e) =>
									editor.updateTextLayer(layer.id, {
										bold: (e.currentTarget as HTMLInputElement).checked
									})}
							/>
							Bold
						</label>
						<label class="flex items-center gap-1 text-xs">
							<input
								type="checkbox"
								checked={layer.italic}
								onchange={(e) =>
									editor.updateTextLayer(layer.id, {
										italic: (e.currentTarget as HTMLInputElement).checked
									})}
							/>
							Italic
						</label>
						<label class="flex items-center gap-1 text-xs">
							<input
								type="checkbox"
								checked={layer.allCaps}
								onchange={(e) =>
									editor.updateTextLayer(layer.id, {
										allCaps: (e.currentTarget as HTMLInputElement).checked
									})}
							/>
							ALL CAPS
						</label>
					</div>

					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Font size — {layer.fontSize}px</span>
						<input
							type="range"
							min="12"
							max="120"
							value={layer.fontSize}
							oninput={(e) =>
								editor.updateTextLayer(layer.id, {
									fontSize: Number((e.currentTarget as HTMLInputElement).value)
								})}
						/>
					</label>

					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Font</span>
						<select
							value={layer.fontFamily}
							onchange={(e) =>
								editor.updateTextLayer(layer.id, {
									fontFamily: (e.currentTarget as HTMLSelectElement).value
								})}
							class="rounded border border-gray-300 px-2 py-1 text-xs"
						>
							<option value="Impact">Impact</option>
							<option value="Arial">Arial</option>
							<option value="Comic Sans MS">Comic Sans</option>
							<option value="Georgia">Georgia</option>
							<option value="Helvetica">Helvetica</option>
							<option value="Times New Roman">Times New Roman</option>
						</select>
					</label>

					<div class="flex gap-2">
						<label class="flex flex-1 flex-col gap-1">
							<span class="text-xs text-gray-500">Color</span>
							<input
								type="color"
								value={layer.color}
								oninput={(e) =>
									editor.updateTextLayer(layer.id, {
										color: (e.currentTarget as HTMLInputElement).value
									})}
								class="h-7 w-full cursor-pointer rounded border border-gray-300"
							/>
						</label>
						<label class="flex flex-1 flex-col gap-1">
							<span class="text-xs text-gray-500">Outline</span>
							<input
								type="color"
								value={layer.outlineColor}
								oninput={(e) =>
									editor.updateTextLayer(layer.id, {
										outlineColor: (e.currentTarget as HTMLInputElement).value
									})}
								class="h-7 w-full cursor-pointer rounded border border-gray-300"
							/>
						</label>
					</div>

					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Outline width — {layer.outlineWidth}</span>
						<input
							type="range"
							min="0"
							max="10"
							value={layer.outlineWidth}
							oninput={(e) =>
								editor.updateTextLayer(layer.id, {
									outlineWidth: Number((e.currentTarget as HTMLInputElement).value)
								})}
						/>
					</label>

					<div class="flex items-center gap-2">
						<span class="text-xs text-gray-500">Align</span>
						{#each ['left', 'center', 'right'] as align (align)}
							<button
								onclick={() =>
									editor.updateTextLayer(layer.id, {
										align: align as TextLayer['align']
									})}
								class="rounded px-2 py-0.5 text-xs {layer.align === align
									? 'bg-indigo-600 text-white'
									: 'bg-gray-100 text-gray-700'}"
							>
								{align[0].toUpperCase()}
							</button>
						{/each}
					</div>

					<div class="flex items-center gap-2">
						<span class="text-xs text-gray-500">Vertical</span>
						{#each [['top', 'Top'], ['middle', 'Mid'], ['bottom', 'Bot']] as [val, label] (val)}
							<button
								onclick={() =>
									editor.updateTextLayer(layer.id, {
										verticalAlign: val as TextLayer['verticalAlign']
									})}
								class="rounded px-2 py-0.5 text-xs {layer.verticalAlign === val
									? 'bg-indigo-600 text-white'
									: 'bg-gray-100 text-gray-700'}"
							>
								{label}
							</button>
						{/each}
					</div>

					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Rotation — {Math.round(layer.rotation)}°</span>
						<input
							type="range"
							min="-180"
							max="180"
							value={Math.round(layer.rotation)}
							oninput={(e) =>
								editor.updateTextLayer(layer.id, {
									rotation: Number((e.currentTarget as HTMLInputElement).value)
								})}
						/>
					</label>

					<button
						onclick={() => editor.removeTextLayer(layer.id)}
						class="rounded bg-red-100 px-2 py-1 text-xs text-red-700 hover:bg-red-200"
					>
						Remove layer
					</button>
				</div>
			{/if}
		</div>
	{/each}

	{#each editor.imageLayers as layer (layer.id)}
		{@const isSelected = editor.selectedLayerId === layer.id}
		{@const isExpanded = expandedId === layer.id}
		<div
			class="overflow-hidden rounded-lg border {isSelected
				? 'border-indigo-400'
				: 'border-gray-200'}"
		>
			<button
				onclick={() => toggleLayer(layer.id)}
				class="flex w-full items-center gap-2 px-3 py-2 text-left {isSelected
					? 'bg-indigo-50'
					: 'hover:bg-gray-50'}"
			>
				<img src={layer.src} alt="" class="h-5 w-5 flex-shrink-0 rounded object-cover" />
				<span class="flex-1 truncate text-xs text-gray-700">Image overlay</span>
				<span class="text-xs text-gray-400">{isExpanded ? '▲' : '▼'}</span>
			</button>

			{#if isExpanded}
				<div class="flex flex-col gap-2 border-t bg-white px-3 py-2">
					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Width — {layer.width}px</span>
						<input
							type="range"
							min="20"
							max={canvasWidth}
							value={layer.width}
							oninput={(e) =>
								editor.updateImageLayer(layer.id, {
									width: Number((e.currentTarget as HTMLInputElement).value)
								})}
						/>
					</label>

					<label class="flex flex-col gap-1">
						<span class="text-xs text-gray-500">Rotation — {Math.round(layer.rotation)}°</span>
						<input
							type="range"
							min="-180"
							max="180"
							value={Math.round(layer.rotation)}
							oninput={(e) =>
								editor.updateImageLayer(layer.id, {
									rotation: Number((e.currentTarget as HTMLInputElement).value)
								})}
						/>
					</label>

					<button
						onclick={() => editor.removeImageLayer(layer.id)}
						class="rounded bg-red-100 px-2 py-1 text-xs text-red-700 hover:bg-red-200"
					>
						Remove layer
					</button>
				</div>
			{/if}
		</div>
	{/each}
</div>
