<script lang="ts">
	import type { ImageLayer } from '$lib/types';

	interface Props {
		layer: ImageLayer;
		selected: boolean;
		onselect: () => void;
		onupdate: (patch: Partial<ImageLayer>) => void;
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
		onupdate({
			x: Math.max(0, startLayerX + (e.clientX - startX)),
			y: Math.max(0, startLayerY + (e.clientY - startY))
		});
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
		onupdate({
			width: Math.max(20, startW + (e.clientX - startX)),
			height: Math.max(20, startH + (e.clientY - startY))
		});
	}

	function onResizeUp() {
		resizing = false;
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	data-layer="image"
	role="button"
	tabindex="0"
	class="absolute cursor-move touch-none {selected ? 'ring-2 ring-indigo-500 ring-offset-1' : ''}"
	style="left:{layer.x}px; top:{layer.y}px; width:{layer.width}px; height:{layer.height}px;"
	onpointerdown={onPointerDown}
	onpointermove={onPointerMove}
	onpointerup={onPointerUp}
	onkeydown={(e) => e.key === 'Delete' && onremove()}
>
	<img
		src={layer.src}
		alt="overlay"
		draggable="false"
		class="pointer-events-none h-full w-full object-cover"
	/>

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
