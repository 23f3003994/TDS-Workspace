
//this file was generated automatically when i created this wrangler hello-world project
//This file is only for testing the worker automatically.
// It checks:

// expect(await response.text()).toMatchInlineSnapshot(`"Hello World!"`);


// Meaning:

// “When I call the worker, does it return Hello World?”

// So it’s just a unit test template.
// i have commented it out 
//can remove this test folderif needed

// import { env, createExecutionContext, waitOnExecutionContext, SELF } from 'cloudflare:test';
// import { describe, it, expect } from 'vitest';
// import worker from '../src';

// describe('Hello World worker', () => {
// 	it('responds with Hello World! (unit style)', async () => {
// 		const request = new Request('http://example.com');
// 		// Create an empty context to pass to `worker.fetch()`.
// 		const ctx = createExecutionContext();
// 		const response = await worker.fetch(request, env, ctx);
// 		// Wait for all `Promise`s passed to `ctx.waitUntil()` to settle before running test assertions
// 		await waitOnExecutionContext(ctx);
// 		expect(await response.text()).toMatchInlineSnapshot(`"Hello World!"`);
// 	});

// 	it('responds with Hello World! (integration style)', async () => {
// 		const response = await SELF.fetch('http://example.com');
// 		expect(await response.text()).toMatchInlineSnapshot(`"Hello World!"`);
// 	});
// });
