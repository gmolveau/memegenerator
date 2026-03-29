<script lang="ts">
	import { editor } from '$lib/stores/editor.svelte';
	import { incrementPopularity } from '$lib/api/templates';
	import type { Effect } from '$lib/types';

	interface Props {
		canvasHeight: number;
		templateImg: HTMLImageElement | null;
		templateMode?: boolean;
		onsave?: () => void;
	}

	let { canvasHeight, templateImg, templateMode = false, onsave }: Props = $props();

	const CANVAS_WIDTH = 600;

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

	async function downloadMeme() {
		if (!templateImg) return;
		const canvas = document.createElement('canvas');
		canvas.width = CANVAS_WIDTH;
		canvas.height = canvasHeight;
		const ctx = canvas.getContext('2d')!;

		ctx.filter = filterMap[editor.effect];
		ctx.drawImage(templateImg, 0, 0, CANVAS_WIDTH, canvasHeight);
		ctx.filter = 'none';

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

		for (const layer of editor.textLayers) {
			ctx.save();
			ctx.translate(layer.x + layer.width / 2, layer.y + layer.height / 2);
			ctx.rotate((layer.rotation * Math.PI) / 180);
			ctx.translate(-layer.width / 2, -layer.height / 2);
			const weight = layer.bold ? 'bold ' : '';
			const style = layer.italic ? 'italic ' : '';
			ctx.font = `${style}${weight}${layer.fontSize}px ${layer.fontFamily}`;
			ctx.textAlign = layer.align;
			ctx.textBaseline = 'top';
			ctx.fillStyle = layer.color;
			const tx =
				layer.align === 'center' ? layer.width / 2 : layer.align === 'right' ? layer.width : 0;
			const ty =
				layer.verticalAlign === 'bottom'
					? layer.height - layer.fontSize
					: layer.verticalAlign === 'middle'
						? (layer.height - layer.fontSize) / 2
						: 0;
			const text = layer.allCaps ? layer.text.toUpperCase() : layer.text;
			if (layer.outlineWidth > 0) {
				ctx.strokeStyle = layer.outlineColor;
				ctx.lineWidth = layer.outlineWidth * 2;
				ctx.lineJoin = 'round';
				ctx.strokeText(text, tx, ty);
			}
			ctx.fillText(text, tx, ty);
			ctx.restore();
		}

		const link = document.createElement('a');
		link.download = 'meme.jpg';
		link.href = canvas.toDataURL('image/jpeg', 0.92);
		link.click();

		if (editor.template) {
			incrementPopularity(editor.template.id).catch(() => {});
		}
	}
</script>

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
		{#each effects as ef (ef.value)}
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
		{#if templateMode}
			<button
				onclick={onsave}
				class="w-full rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
			>
				Save Template
			</button>
		{:else}
			<button
				onclick={downloadMeme}
				class="w-full rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
			>
				⬇ Download JPG
			</button>
		{/if}
	</div>
</div>
