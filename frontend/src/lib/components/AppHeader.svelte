<script lang="ts">
	import { resolve } from '$app/paths';
	import { loginUrl } from '$lib/api/auth';
	import { auth } from '$lib/stores/auth.svelte';
</script>

<header class="border-b bg-white shadow-sm">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<div class="flex items-baseline gap-2">
			<a href={resolve('/')} class="text-xl font-bold tracking-tight text-indigo-700"
				>Meme Generator</a
			>
			<span class="text-xs text-gray-400">{__APP_VERSION__}</span>
		</div>
		<div class="flex items-center gap-4">
			{#if auth.user}
				{#if auth.user.role === 'admin' || auth.user.role === 'superadmin'}
					<a href={resolve('/admin')} class="text-sm text-gray-500 hover:text-indigo-600">Admin</a>
				{/if}
				<a
					href={resolve('/upload')}
					class="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
					>Upload</a
				>
				<a
					href={resolve('/templates')}
					class="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-indigo-600"
				>{auth.user.name}<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="size-4"
					><path
						d="M10 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM3.465 14.493a1.23 1.23 0 0 0 .41 1.412A9.957 9.957 0 0 0 10 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 0 0-13.074.003Z"
					/></svg
				></a
				>
			{:else if auth.user === null}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
				<a href={loginUrl('/')} class="text-sm text-indigo-600 hover:text-indigo-800">Login</a>
			{/if}
		</div>
	</div>
</header>
