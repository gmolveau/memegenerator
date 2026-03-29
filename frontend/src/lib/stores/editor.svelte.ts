import type { EditorState, Effect, ImageLayer, Template, TextLayer } from '$lib/types';

function createId() {
	return Math.random().toString(36).slice(2, 10);
}

function defaultText(): TextLayer {
	return {
		id: createId(),
		text: 'Your text here',
		x: 50,
		y: 50,
		width: 300,
		height: 60,
		rotation: 0,
		fontSize: 36,
		fontFamily: 'Impact',
		color: '#ffffff',
		outlineColor: '#000000',
		outlineWidth: 2,
		align: 'center',
		verticalAlign: 'middle',
		bold: false,
		italic: false,
		allCaps: false
	};
}

function createEditorState() {
	let state = $state<EditorState>({
		template: null,
		textLayers: [],
		imageLayers: [],
		effect: 'none',
		selectedLayerId: null
	});

	return {
		get template() {
			return state.template;
		},
		get textLayers() {
			return state.textLayers;
		},
		get imageLayers() {
			return state.imageLayers;
		},
		get effect() {
			return state.effect;
		},
		get selectedLayerId() {
			return state.selectedLayerId;
		},

		clearTemplate() {
			state.template = null;
			state.textLayers = [];
			state.imageLayers = [];
			state.effect = 'none';
			state.selectedLayerId = null;
		},

		setTemplate(template: Template) {
			state.template = template;
			state.textLayers = (template.text_layers ?? []).map((tl, i) => ({
				id: `tpl-${i}`,
				text: '',
				x: tl.x,
				y: tl.y,
				width: tl.width,
				height: tl.height,
				rotation: tl.rotation,
				fontSize: tl.fontSize,
				fontFamily: tl.fontFamily,
				color: tl.color,
				outlineColor: tl.outlineColor,
				outlineWidth: tl.outlineWidth,
				align: tl.align,
				verticalAlign: tl.verticalAlign ?? 'middle',
				bold: tl.bold,
				italic: tl.italic,
				allCaps: tl.allCaps
			}));
			state.imageLayers = [];
			state.effect = 'none';
			state.selectedLayerId = null;
		},

		addTextLayer() {
			const layer = defaultText();
			state.textLayers = [...state.textLayers, layer];
			state.selectedLayerId = layer.id;
		},

		updateTextLayer(id: string, patch: Partial<TextLayer>) {
			state.textLayers = state.textLayers.map((l) => (l.id === id ? { ...l, ...patch } : l));
		},

		removeTextLayer(id: string) {
			state.textLayers = state.textLayers.filter((l) => l.id !== id);
			if (state.selectedLayerId === id) state.selectedLayerId = null;
		},

		addImageLayer(src: string, width: number, height: number) {
			const layer: ImageLayer = {
				id: createId(),
				src,
				x: 20,
				y: 20,
				width,
				height,
				rotation: 0
			};
			state.imageLayers = [...state.imageLayers, layer];
			state.selectedLayerId = layer.id;
		},

		updateImageLayer(id: string, patch: Partial<ImageLayer>) {
			state.imageLayers = state.imageLayers.map((l) => (l.id === id ? { ...l, ...patch } : l));
		},

		removeImageLayer(id: string) {
			state.imageLayers = state.imageLayers.filter((l) => l.id !== id);
			if (state.selectedLayerId === id) state.selectedLayerId = null;
		},

		setEffect(effect: Effect) {
			state.effect = effect;
		},

		selectLayer(id: string | null) {
			state.selectedLayerId = id;
		},

		get selectedTextLayer(): TextLayer | undefined {
			return state.textLayers.find((l) => l.id === state.selectedLayerId);
		}
	};
}

export const editor = createEditorState();
