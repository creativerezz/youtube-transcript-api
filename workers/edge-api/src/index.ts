/**
 * YouTube Summaries API - Edge Layer
 *
 * Cloudflare Workers edge layer with 3-tier caching:
 * KV (sub-ms) → Upstash Redis (10ms) → Railway Origin (50-200ms)
 */

export interface Env {
	// D1 Database binding for persistent storage
	DB: D1Database;

	// KV Namespace binding for edge caching (5min TTL)
	CACHE_KV: KVNamespace;

	// Upstash Redis credentials (set via wrangler secret)
	UPSTASH_REDIS_REST_URL: string;
	UPSTASH_REDIS_REST_TOKEN: string;

	// Environment configuration
	ENVIRONMENT: string;
	CACHE_KV_TTL: number;
	UPSTASH_TTL: number;
	RAILWAY_ORIGIN_URL: string;
}

export default {
	async fetch(
		request: Request,
		env: Env,
		ctx: ExecutionContext
	): Promise<Response> {
		// CORS headers
		const corsHeaders = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
			'Access-Control-Allow-Headers': 'Content-Type',
		};

		// Handle CORS preflight
		if (request.method === 'OPTIONS') {
			return new Response(null, {
				headers: corsHeaders,
			});
		}

		const url = new URL(request.url);
		const path = url.pathname;

		try {
			// Health check endpoint
			if (path === '/health' || path === '/') {
				return new Response(
					JSON.stringify({
						status: 'healthy',
						environment: env.ENVIRONMENT,
						timestamp: new Date().toISOString(),
						edge_location: request.cf?.colo || 'unknown',
						services: {
							kv: 'enabled',
							upstash: 'enabled',
							d1: 'enabled',
							origin: env.RAILWAY_ORIGIN_URL,
						},
					}),
					{
						headers: {
							'Content-Type': 'application/json',
							...corsHeaders,
						},
					}
				);
			}

			// TODO: Implement video endpoints with 3-tier caching
			// - POST /video-data
			// - POST /video-captions
			// - POST /video-timestamps
			// - POST /video-transcript-languages
			// - POST /transcripts/get
			// - GET /transcripts/list

			// For now, proxy all other requests to Railway origin
			return new Response(
				JSON.stringify({
					message: 'Edge worker is running. Endpoints coming soon.',
					path,
					timestamp: new Date().toISOString(),
				}),
				{
					status: 200,
					headers: {
						'Content-Type': 'application/json',
						...corsHeaders,
					},
				}
			);
		} catch (error) {
			return new Response(
				JSON.stringify({
					error: 'Internal Server Error',
					message: error instanceof Error ? error.message : 'Unknown error',
					timestamp: new Date().toISOString(),
				}),
				{
					status: 500,
					headers: {
						'Content-Type': 'application/json',
						...corsHeaders,
					},
				}
			);
		}
	},
};
