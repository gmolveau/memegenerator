export interface Template {
	id: number;
	name: string;
	keywords: string[];
	image_url: string;
	created_at: string;
}

export interface TextLayer {
	id: string;
	text: string;
	x: number; // px from left of canvas
	y: number; // px from top of canvas
	width: number;
	height: number;
	rotation: number; // degrees, clockwise
	fontSize: number;
	fontFamily: string;
	color: string;
	outlineColor: string;
	outlineWidth: number;
	align: 'left' | 'center' | 'right';
	bold: boolean;
	italic: boolean;
	allCaps: boolean;
}

export interface ImageLayer {
	id: string;
	src: string; // object URL or data URL
	x: number;
	y: number;
	width: number;
	height: number;
	rotation: number; // degrees, clockwise
}

export type Effect = 'none' | 'grayscale' | 'blur' | 'sharpen' | 'sepia' | 'invert';

export interface EditorState {
	template: Template | null;
	textLayers: TextLayer[];
	imageLayers: ImageLayer[];
	effect: Effect;
	selectedLayerId: string | null;
}
