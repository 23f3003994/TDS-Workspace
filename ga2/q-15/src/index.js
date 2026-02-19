/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */
//the below one is the default hello-world code that is generated when i created this wrangler project

// export default {
// 	async fetch(request, env, ctx) {
// 		return new Response('Hello World!');
// 	},
// };

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }

    // Route: POST /data
    if (url.pathname === "/data" && request.method === "POST") {
      try {
        const { type, value } = await request.json();
        let reversed;

        if (type === "string") {
          reversed = value.split("").reverse().join("");
        } else if (type === "array") {
          reversed = value.slice().reverse();
        } else if (type === "words") {
          reversed = value.split(" ").reverse().join(" ");
        } else if (type === "number") {
          reversed = parseInt(value.toString().split("").reverse().join(""));
        } else {
          return jsonResponse({ error: "Invalid type" }, 400);
        }

        return jsonResponse({
          reversed,
          email: "23f3003994@ds.study.iitm.ac.in"
        });

      } catch (e) {
        return jsonResponse({ error: "Invalid JSON" }, 400);
      }
    }

    return new Response("Not Found", { status: 404 });
  },
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(),
    },
  });
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}
