export interface RunErrorInfo {
	type: 'syntax' | 'runtime' | 'export';
	message: string;
	traceback?: string | null;
}

export interface RunResponse {
	run_id: string;
	status: 'ok' | 'error';
	glb_url: string | null;
	error?: RunErrorInfo | null;
}

export async function runCadQuery(input: {
	code: string;
	params?: Record<string, unknown>;
}): Promise<RunResponse> {
	const res = await fetch('/api/run', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(input)
	});

	if (!res.ok) {
		throw new Error(`Run failed with status ${res.status}`);
	}

	const data = (await res.json()) as RunResponse;
	return data;
}

