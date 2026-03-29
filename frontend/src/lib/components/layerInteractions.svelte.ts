interface Layer {
	x: number;
	y: number;
	width: number;
	height: number;
	rotation: number;
}

interface Opts {
	getEl: () => HTMLDivElement | null;
	getLayer: () => Layer;
	onupdate: (patch: Partial<Layer>) => void;
	onselect: () => void;
	isEditing?: () => boolean;
	minWidth?: number;
	minHeight?: number;
}

export function createLayerInteractions(opts: Opts) {
	const minWidth = opts.minWidth ?? 20;
	const minHeight = opts.minHeight ?? 20;

	// --- Drag ---
	let dragging = $state(false);
	let startX = 0,
		startY = 0,
		startLayerX = 0,
		startLayerY = 0;

	function onPointerDown(e: PointerEvent) {
		if (opts.isEditing?.()) return;
		const target = e.target as HTMLElement;
		if (target.dataset.resize || target.dataset.rotate) return;
		e.stopPropagation();
		opts.onselect();
		dragging = true;
		startX = e.clientX;
		startY = e.clientY;
		const layer = opts.getLayer();
		startLayerX = layer.x;
		startLayerY = layer.y;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onPointerMove(e: PointerEvent) {
		if (!dragging) return;
		opts.onupdate({
			x: Math.max(0, startLayerX + (e.clientX - startX)),
			y: Math.max(0, startLayerY + (e.clientY - startY))
		});
	}

	function onPointerUp() {
		dragging = false;
	}

	// --- Resize ---
	let resizing = $state(false);
	let startW = 0,
		startH = 0;

	function onResizeDown(e: PointerEvent) {
		e.stopPropagation();
		resizing = true;
		startX = e.clientX;
		startY = e.clientY;
		const layer = opts.getLayer();
		startW = layer.width;
		startH = layer.height;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onResizeMove(e: PointerEvent) {
		if (!resizing) return;
		opts.onupdate({
			width: Math.max(minWidth, startW + (e.clientX - startX)),
			height: Math.max(minHeight, startH + (e.clientY - startY))
		});
	}

	function onResizeUp() {
		resizing = false;
	}

	// --- Rotate ---
	let rotating = $state(false);
	let centerX = 0,
		centerY = 0,
		startAngle = 0,
		startRotation = 0;

	function onRotateDown(e: PointerEvent) {
		e.stopPropagation();
		rotating = true;
		const rect = opts.getEl()!.getBoundingClientRect();
		centerX = rect.left + rect.width / 2;
		centerY = rect.top + rect.height / 2;
		startAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
		startRotation = opts.getLayer().rotation;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onRotateMove(e: PointerEvent) {
		if (!rotating) return;
		const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
		opts.onupdate({ rotation: startRotation + (angle - startAngle) });
	}

	function onRotateUp() {
		rotating = false;
	}

	return {
		get dragging() {
			return dragging;
		},
		onPointerDown,
		onPointerMove,
		onPointerUp,
		onResizeDown,
		onResizeMove,
		onResizeUp,
		onRotateDown,
		onRotateMove,
		onRotateUp
	};
}
