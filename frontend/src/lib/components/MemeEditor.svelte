<script lang="ts">
	import { editor } from '$lib/stores/editor.svelte';
	import type { Effect, ImageLayer, TextLayer } from '$lib/types';
	import TextLayerEl from './TextLayerEl.svelte';
	import ImageLayerEl from './ImageLayerEl.svelte';

	// Canvas dimensions — we scale the template to fit a fixed width
	const CANVAS_WIDTH = 600;
	let canvasHeight = $state(450);

	let templateImg = $state<HTMLImageElement | null>(null);
	let containerEl = $state<HTMLDivElement | null>(null);

	// Recompute canvas height when template changes.
	// crossOrigin must be set BEFORE src so the browser makes a CORS request,
	// which is required for canvas.toDataURL() to work without tainting the canvas.
	$effect(() => {
		if (!editor.template) return;
		const img = new Image();
		img.crossOrigin = 'anonymous';
		img.onload = () => {
			canvasHeight = Math.round((img.naturalHeight / img.naturalWidth) * CANVAS_WIDTH);
			templateImg = img;
		};
		img.src = editor.template.image_url;
	});

	// CSS filter for the background image
	const filterMap: Record<Effect, string> = {
		none: 'none',
		grayscale: 'grayscale(100%)',
		blur: 'blur(3px)',
		sharpen: 'contrast(1.4) brightness(1.1)',
		sepia: 'sepia(100%)',
		invert: 'invert(100%)'
	};

	const effects: { label: string; value: Effect }[] = [
		{ label: 'None', value: 'none' },
		{ label: 'Grayscale', value: 'grayscale' },
		{ label: 'Blur', value: 'blur' },
		{ label: 'Sharpen', value: 'sharpen' },
		{ label: 'Sepia', value: 'sepia' },
		{ label: 'Invert', value: 'invert' }
	];

	function deselect(e: MouseEvent) {
		if ((e.target as HTMLElement).closest('[data-layer]')) return;
		editor.selectLayer(null);
	}

	// --- Image overlay upload ---
	function handleImageOverlay(e: Event) {
		const input = e.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		const url = URL.createObjectURL(file);
		const img = new Image();
		img.onload = () => {
			const maxW = CANVAS_WIDTH / 3;
			const scale = Math.min(1, maxW / img.naturalWidth);
			editor.addImageLayer(
				url,
				Math.round(img.naturalWidth * scale),
				Math.round(img.naturalHeight * scale)
			);
		};
		img.src = url;
		input.value = '';
	}

	// --- Export ---
	async function downloadMeme() {
		if (!templateImg) return;
		const canvas = document.createElement('canvas');
		canvas.width = CANVAS_WIDTH;
		canvas.height = canvasHeight;
		const ctx = canvas.getContext('2d')!;

		// Draw template with effect
		ctx.filter = filterMap[editor.effect];
		ctx.drawImage(templateImg, 0, 0, CANVAS_WIDTH, canvasHeight);
		ctx.filter = 'none';

		// Draw image layers (rotate around their center)
		for (const layer of editor.imageLayers) {
			await new Promise<void>((resolve) => {
				const img = new Image();
				img.onload = () => {
					ctx.save();
					ctx.translate(layer.x + layer.width / 2, layer.y + layer.height / 2);
					ctx.rotate((layer.rotation * Math.PI) / 180);
					ctx.drawImage(img, -layer.width / 2, -layer.height / 2, layer.width, layer.height);
					ctx.restore();
					resolve();
				};
				img.src = layer.src;
			});
		}

		// Draw text layers (rotate around their center)
		for (const layer of editor.textLayers) {
			ctx.save();
			ctx.translate(layer.x + layer.width / 2, layer.y + layer.height / 2);
			ctx.rotate((layer.rotation * Math.PI) / 180);
			ctx.translate(-layer.width / 2, -layer.height / 2);
			const weight = layer.bold ? 'bold ' : '';
			const style = layer.italic ? 'italic ' : '';
			ctx.font = `${style}${weight}${layer.fontSize}px ${layer.fontFamily}`;
			ctx.textAlign = layer.align;
			ctx.fillStyle = layer.color;
			const tx =
				layer.align === 'center' ? layer.width / 2 : layer.align === 'right' ? layer.width : 0;
			if (layer.outlineWidth > 0) {
				ctx.strokeStyle = layer.outlineColor;
				ctx.lineWidth = layer.outlineWidth * 2;
				ctx.lineJoin = 'round';
				ctx.strokeText(layer.text, tx, layer.fontSize);
			}
			ctx.fillText(layer.text, tx, layer.fontSize);
			ctx.restore();
		}

		const link = document.createElement('a');
		link.download = 'meme.jpg';
		link.href = canvas.toDataURL('image/jpeg', 0.92);
		link.click();
	}

	// --- Layer list panel ---
	let expandedId = $state<string | null>(null);

	// When a layer is selected on the canvas, auto-expand it in the list.
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

<div class="flex flex-col gap-4 lg:flex-row">
	<!-- Left toolbar -->
	<div class="flex w-full flex-col gap-3 lg:w-48">
		<button
			onclick={() => editor.addTextLayer()}
			class="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700"
		>
			+ Add Text
		</button>

		<label
			class="cursor-pointer rounded-lg border border-indigo-600 px-3 py-2 text-center text-sm font-medium text-indigo-600 hover:bg-indigo-50"
		>
			+ Add Image
			<input type="file" accept="image/*" class="hidden" onchange={handleImageOverlay} />
		</label>

		<div class="border-t pt-3">
			<p class="mb-2 text-xs font-semibold tracking-wide text-gray-500 uppercase">Effect</p>
			{#each effects as ef}
				<button
					onclick={() => editor.setEffect(ef.value)}
					class="w-full rounded px-2 py-1 text-left text-sm {editor.effect === ef.value
						? 'bg-indigo-100 font-semibold text-indigo-700'
						: 'text-gray-700 hover:bg-gray-100'}"
				>
					{ef.label}
				</button>
			{/each}
		</div>

		<div class="mt-auto border-t pt-3">
			<button
				onclick={downloadMeme}
				class="w-full rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
			>
				⬇ Download JPG
			</button>
		</div>
	</div>

	<!-- Editor canvas -->
	<div class="flex flex-1 flex-col gap-3">
		<!--
			Outer div: positions layers, allows overflow so rotation handles
			can appear outside the image boundary.
			Inner div: clips the background image to the rounded border.
		-->
		<div
			bind:this={containerEl}
			onclick={deselect}
			role="presentation"
			class="relative select-none"
			style="width:{CANVAS_WIDTH}px; height:{canvasHeight}px;"
		>
			<!-- Background image clipped to rounded border -->
			<div
				class="pointer-events-none absolute inset-0 overflow-hidden rounded-lg border border-gray-300 bg-gray-900"
			>
				{#if editor.template}
					<img
						src={editor.template.image_url}
						alt={editor.template.name}
						draggable="false"
						crossorigin="anonymous"
						class="h-full w-full object-cover"
						style="filter:{filterMap[editor.effect]}"
					/>
				{/if}
			</div>

			<!-- Layers (overflow allowed for rotation handles) -->
			{#each editor.imageLayers as layer (layer.id)}
				<ImageLayerEl
					{layer}
					selected={editor.selectedLayerId === layer.id}
					onselect={() => editor.selectLayer(layer.id)}
					onupdate={(patch) => editor.updateImageLayer(layer.id, patch)}
					onremove={() => editor.removeImageLayer(layer.id)}
				/>
			{/each}

			{#each editor.textLayers as layer (layer.id)}
				<TextLayerEl
					{layer}
					selected={editor.selectedLayerId === layer.id}
					onselect={() => editor.selectLayer(layer.id)}
					onupdate={(patch) => editor.updateTextLayer(layer.id, patch)}
					onremove={() => editor.removeTextLayer(layer.id)}
				/>
			{/each}
		</div>
	</div>

	<!-- Right: layer list -->
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
				<!-- Header -->
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

				<!-- Properties -->
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
							{#each ['left', 'center', 'right'] as align}
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
						</div>

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
				<!-- Header -->
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

				<!-- Properties -->
				{#if isExpanded}
					<div class="flex flex-col gap-2 border-t bg-white px-3 py-2">
						<label class="flex flex-col gap-1">
							<span class="text-xs text-gray-500">Width — {layer.width}px</span>
							<input
								type="range"
								min="20"
								max={CANVAS_WIDTH}
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
</div>
