<script lang="ts">
	import type { TextLayer } from '$lib/types';

	interface Props {
		layer: TextLayer;
		selected: boolean;
		onselect: () => void;
		onupdate: (patch: Partial<TextLayer>) => void;
		onremove: () => void;
	}

	let { layer, selected, onselect, onupdate, onremove }: Props = $props();

	let dragging = $state(false);
	let resizing = $state(false);
	let startX = 0,
		startY = 0,
		startLayerX = 0,
		startLayerY = 0;
	let startW = 0,
		startH = 0;

	function onPointerDown(e: PointerEvent) {
		if ((e.target as HTMLElement).dataset.resize) return;
		e.stopPropagation();
		onselect();
		dragging = true;
		startX = e.clientX;
		startY = e.clientY;
		startLayerX = layer.x;
		startLayerY = layer.y;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onPointerMove(e: PointerEvent) {
		if (!dragging) return;
		const dx = e.clientX - startX;
		const dy = e.clientY - startY;
		onupdate({ x: Math.max(0, startLayerX + dx), y: Math.max(0, startLayerY + dy) });
	}

	function onPointerUp() {
		dragging = false;
	}

	function onResizeDown(e: PointerEvent) {
		e.stopPropagation();
		resizing = true;
		startX = e.clientX;
		startY = e.clientY;
		startW = layer.width;
		startH = layer.height;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onResizeMove(e: PointerEvent) {
		if (!resizing) return;
		const dx = e.clientX - startX;
		const dy = e.clientY - startY;
		onupdate({
			width: Math.max(60, startW + dx),
			height: Math.max(30, startH + dy)
		});
	}

	function onResizeUp() {
		resizing = false;
	}

	const fontStyle = $derived(
		`${layer.italic ? 'italic ' : ''}${layer.bold ? 'bold ' : ''}${layer.fontSize}px ${layer.fontFamily}`
	);
	const textShadow = $derived(
		layer.outlineWidth > 0
			? `${layer.outlineWidth}px ${layer.outlineWidth}px 0 ${layer.outlineColor},
         -${layer.outlineWidth}px -${layer.outlineWidth}px 0 ${layer.outlineColor},
         ${layer.outlineWidth}px -${layer.outlineWidth}px 0 ${layer.outlineColor},
         -${layer.outlineWidth}px ${layer.outlineWidth}px 0 ${layer.outlineColor}`
			: 'none'
	);
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	data-layer="text"
	role="button"
	tabindex="0"
	class="absolute cursor-move touch-none {selected ? 'ring-2 ring-indigo-500 ring-offset-1' : ''}"
	style="left:{layer.x}px; top:{layer.y}px; width:{layer.width}px; height:{layer.height}px;"
	onpointerdown={onPointerDown}
	onpointermove={onPointerMove}
	onpointerup={onPointerUp}
	onkeydown={(e) => e.key === 'Delete' && onremove()}
>
	<div
		class="h-full w-full overflow-hidden break-words whitespace-pre-wrap"
		style="
      font: {fontStyle};
      color: {layer.color};
      text-align: {layer.align};
      text-shadow: {textShadow};
      line-height: 1.2;
      padding: 4px;
    "
	>
		{layer.text}
	</div>

	<!-- Resize handle -->
	{#if selected}
		<div
			data-resize="se"
			class="absolute right-0 bottom-0 h-4 w-4 cursor-se-resize bg-indigo-500 opacity-80"
			onpointerdown={onResizeDown}
			onpointermove={onResizeMove}
			onpointerup={onResizeUp}
		></div>
	{/if}
</div>
