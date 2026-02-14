#!/usr/bin/env node

// ============================================================================
// CLI STREAMING CLIENT FOR LLM RESPONSES
// ============================================================================
// Purpose: Consume Server-Sent Events (SSE) responses from FastAPI /stream endpoint
// Functionality: Sends a prompt to the server and displays tokens as they stream


// Usage: node stream_client.js "Your prompt here"


// 
// How it works:
// 1. Reads prompt from command line arguments
// 2. Sends POST request to http://localhost:8003/stream with prompt
// 3. Receives SSE-formatted response from server
// 4. Parses SSE messages and extracts text tokens
// 5. Prints tokens to console in real-time (no buffering)
// 6. Stops when server sends [DONE] signal

// npm install node-fetch@2 (needed)
// Import the "node-fetch" library and assign it to the variable `fetch`.
// This lets us use the browser-like fetch() API inside Node.js
// to make HTTP requests (GET, POST, etc.) to servers/APIs.
const fetch = require("node-fetch");

// ============================================================================
// MAIN FUNCTION: HANDLE STREAMING RESPONSE FROM /stream ENDPOINT
// ============================================================================
async function streamResponse(prompt) {
  // This async function:
  // 1. Sends POST request with the user's prompt
  // 2. Receives streaming response (chunks of tokens)
  // 3. Parses SSE format and extracts text
  // 4. Prints text to console in real-time
  
  try {
    // STEP 1: SEND POST REQUEST TO /stream ENDPOINT
    // =============================================
    // Fetch API sends HTTP POST request to the FastAPI server
    // The server is expected to run at http://localhost:8003 (local development)
    const response = await fetch("http://localhost:8003/stream", {
      method: "POST",  // HTTP POST request (sending data to server)
      headers: {
        "Content-Type": "application/json",  // Tell server: sending JSON data
      },
      // BODY: The request payload sent to server
      // This matches StreamRequest model from main2.py:
      // {
      //   "prompt": <user's input text>,
      //   "stream": true  # must be true for streaming endpoint
      // }
      body: JSON.stringify({ prompt: prompt, stream: true }),
    });

    // STEP 2: CHECK IF REQUEST WAS SUCCESSFUL
    // ========================================
    // response.ok = true if HTTP status code is 200-299
    // response.ok = false if error (e.g., 400, 404, 500)
    if (!response.ok) {
      console.error("Error: Failed to connect to streaming endpoint");
      // Server returned error status (e.g., empty prompt, stream=false)
      // Exit function and don't try to read response
      return;
    }


    console.log("\nStreaming response:\n");

    // ========================================================================
    // STEP 3-4: SET UP NODE.JS STREAM EVENT LISTENERS
    // ========================================================================
    // WHY NOT getReader() LIKE BROWSER?
    // ==================================
    // Browser (fetch API): Uses getReader() method
    // Node.js: Uses event emitters ("data", "end", "error" events)
    // 
    // Node.js Readable Streams emit events:
    // - "data" event: fired when chunk of data arrives from server
    // - "end" event: fired when stream completes (server closes connection(see connection:keep alive in main2.py))
    // - "error" event: fired on network error
    // 
    // WHY USE EVENTS INSTEAD OF await?
    // - Better for streaming (chunks arrive unpredictably)
    // - Multiple chunks may fire "data" event multiple times
    // - We handle each chunk as it arrives (event-driven)
    
    // Buffer to hold incomplete lines
    // WHY NEEDED: SSE messages split across chunks!
    // 
    // Example problem:
    // Chunk 1: "data: {\"choices\": [{\"delta\": {\"content\": \"Hel\""
    // Chunk 2: "lo\"}}]}\n\ndata: {\"choices\": [...]\n\n"
    // 
    // Line is split! We can't parse chunk 1 (incomplete)
    // Solution: Keep partial data in buffer until we have complete line
    // 
    // How buffer works:
    // - Chunk arrives → add to buffer
    // - Check if buffer contains complete lines (ends with \n)
    // - Process complete lines
    // - Keep incomplete last line in buffer for next chunk
    let buffer = "";  // String to accumulate incoming data
    
    // ========================================================================
    // STEP 5: LISTEN FOR "data" EVENTS (chunks from server)
    // ========================================================================
    // response.body.on("data", callback) registers event listener
    // Every time server sends a chunk, this callback fires
    // parameter: chunk = raw bytes (Buffer object, not string!)
    response.body.on("data", (chunk) => {
      // STEP 6: CONVERT RAW BUFFER → UTF-8 STRING
      // =========================================
      // chunk = Buffer object (raw bytes from network)
      // Buffer example: <Buffer 64 61 74 61 3a 20...> (hexadecimal bytes)
      // chunk.toString("utf-8") = convert to readable text string
      // "utf-8" = character encoding standard (handles multi-byte characters)
      // 
      // WHY NOT GET STRING DIRECTLY?
      // - Network delivers raw bytes, not strings
      // - We must explicitly decode bytes→characters
      // - UTF-8 is standard for web (supports all languages)
      // 
      // Example:
      // Buffer [100, 97, 116, 97] → "data" (ASCII text)
      // Buffer [195, 169] → "é" (UTF-8 encoded, 2 bytes for 1 character)
      const text = chunk.toString("utf-8");

      // ====================================================================
      // STEP 7: ACCUMULATE IN BUFFER (HANDLE MULTI-CHUNK LINES)
      // ====================================================================
      // Multiple chunks may arrive before a complete SSE message
      // SSE message = "data: {...}\n\n"
      // If chunk ends in middle of message, we need to wait for next chunk
      // 
      // Example streaming:
      // Chunk1 → buffer = "data: {\"choices\": ["
      // Chunk2 → buffer += "]\n" → Now we have complete line!
      // Chunk3 → buffer += "data: [DONE]\n"
      buffer += text;

      // ====================================================================
      // STEP 8: SPLIT BUFFER INTO LINES & PRESERVE INCOMPLETE FINAL LINE
      // ====================================================================
      // buffer.split("\n") splits by line breaks
      // Example: "line1\nline2\nline3" → ["line1", "line2", "line3"]
      // BUT: "line1\nline2\nlin" → ["line1", "line2", "lin"]
      // Last element "lin" is INCOMPLETE (no \n at end)
      // 
      // Why this matters:
      // "data: {incomplete" has no \n, so we can't process it yet
      // Next chunk might be: " json}\n\n"
      // Combined: "data: {incomplete json}\n\n" = complete!
      // 
      // Solution: Split lines, save LAST element back in buffer
      const lines = buffer.split("\n");

      // ====================================================================
      // STEP 9: SAVE INCOMPLETE FINAL LINE FOR NEXT CHUNK
      // ====================================================================
      // lines.pop() removes & returns last element from array
      // This last element is INCOMPLETE (no trailing \n)
      // 
      // Example:
      // lines = ["data: {}", "data: incompl"]
      // buffer = lines.pop()  → buffer = "data: incompl"
      // lines = ["data: {}"]  → only complete lines remain
      // 
      // Next chunk arrives:
      // text = "ete}\n\n"
      // buffer += text  → buffer = "data: incomplete}\n\n" (now complete!)
      // Then we split again and process
      buffer = lines.pop();  // Remove incomplete last line, save to buffer for next chunk

      // ====================================================================
      // STEP 10: PROCESS EACH COMPLETE LINE
      // ====================================================================
      // Now 'lines' array contains only COMPLETE lines (each ends with \n)
      // We process each line one by one
      for (let line of lines) {
        // Remove leading/trailing whitespace
        // "  data: {json}  \n" → "data: {json}"
        line = line.trim();

        // STEP 11: IDENTIFY AND PARSE SSE DATA LINES
        // =========================================
        // SSE format requires "data: " prefix
        // Comments start with ": " (just colon-space) — we ignore those
        // Only process lines that have "data: " prefix
        if (line.startsWith("data: ")) {
          // Remove the "data: " prefix to get just the content
          // "data: {\"choices\":[...]}" → "{\"choices\":[...]}"
          const data = line.replace("data: ", "");

          // STEP 12: CHECK FOR COMPLETION SIGNAL
          // ====================================
          // Server sends "data: [DONE]\n\n" when stream finished
          // This is NOT JSON, just a literal string [DONE]
          // When we see this, stream is complete
          if (data === "[DONE]") {
            console.log("\n\n[Stream finished]");
            return;  // Exit function, stream complete
          }

          // STEP 13: PARSE JSON AND EXTRACT TEXT TOKEN
          // ==========================================
          // SSE payload is JSON string that looks like:
          // {
          //   "choices": [
          //     {
          //       "delta": {
          //         "content": "Hello"    ← This is the text token we want
          //       }
          //     }
          //   ]
          // }
          //
          // FLOW: JSON string → Parse to object → Extract nested content
          try {
            // JSON.parse() converts JSON string → JavaScript object
            // "{\\"content\\":\\"Hello\\"}" → {content: "Hello"}
            const parsed = JSON.parse(data);
            
            // Extract the actual text token using optional chaining
            // parsed.choices?.[0]?.delta?.content
            // "?." = safely access property (returns undefined if intermediate is null/undefined)
            // This prevents errors if structure is slightly different
            // Example: if parsed.choices is undefined, returns "" instead of crashing
            const content = parsed.choices?.[0]?.delta?.content || "";

            // STEP 14: DISPLAY TOKEN IN REAL-TIME
            // ===================================
            // process.stdout.write() outputs text WITHOUT newline
            // Why not console.log()? Because that adds \n, breaks formatting
            // Example: "Hello" + "world" prints on same line when using stdout.write()
            //          "Hello\nworld" prints on separate lines when using console.log()
            // Token arrives: "Hello" → displayed immediately
            // Next token arrives: "world" → appended: "Helloworld"
            // User sees text appearing token-by-token in real-time
            process.stdout.write(content);
          } catch (err) {
            // JSON.parse() throws error if string is not valid JSON
            // This might happen if:
            // - Corrupted data from network
            // - Server sent malformed JSON
            // - Partial message (shouldn't happen with SSE, but handle it)
            // We log error but continue processing (don't crash)
            console.error("\nError parsing chunk:", err.message);
          }
        }
        // Lines that don't start with "data: ":
        // - SSE comments (": comment text") — ignored
        // - Empty lines ("") — ignored
        // - Other formats — ignored
      }
    });

    // ========================================================================
    // STEP 15: LISTEN FOR "end" EVENT (stream complete from server side)
    // ========================================================================
    // "end" event fires when server closes the readable stream
    // This happens when Stream/Request is fully received
    // (NOT necessarily when [DONE] message was received)
    // 
    // Difference:
    // - [DONE] = application level signal (from our code)
    // - "end" = network/stream level signal (from HTTP layer)
    // 
    // Both indicate stream is complete, "end" is the cleanup signal
    response.body.on("end", () => {
      console.log("\n\n[Stream ended by server]");
    });
  } catch (error) {
    // Catch network errors:
    // - Connection refused (server not running)
    // - Network timeout
    // - TLS certificate errors
    // - etc.
    console.error("Streaming error:", error.message);
  }
}

// ============================================================================
// COMMAND LINE ARGUMENT PARSING
// ============================================================================
// process.argv is array of command line arguments:
// [0] = path to node executable
// [1] = path to this script (stream_client.js)
// [2...] = user arguments
// Example: node stream_client.js "Explain AI" "in simple words"
// process.argv = [node, stream_client.js, "Explain AI", "in simple words"]

// process.argv.slice(2) removes first 2 elements
// Result: ["Explain AI", "in simple words"]

// .join(" ") concatenates array into single string with spaces
// Result: "Explain AI in simple words"
const prompt = process.argv.slice(2).join(" ");

// ============================================================================
// VALIDATE COMMAND LINE INPUT
// ============================================================================
// User must provide at least one argument (the prompt)
// If no arguments provided:
// - prompt will be empty string ""
// - !prompt evaluates to true
// - Show usage message and exit
if (!prompt) {
  console.log("Usage: node stream_client.js \"Your prompt here\"");
  // process.exit(1) terminates program with exit code 1 (indicates error)
  // Exit code 0 = success, exit code 1 = error
  process.exit(1);
}

// ============================================================================
// CALL STREAMING FUNCTION
// ============================================================================
// streamResponse() is async function that handles entire streaming process
// It:
// 1. Sends prompt to server
// 2. Reads streaming chunks
// 3. Parses SSE format
// 4. Displays text in real-time
// 5. Stops when [DONE] received or error occurs
streamResponse(prompt);




//A doubt- why did we comment "sse msgs split across line".In main2.py we sent a chunk as the dict with data obj completely no..and Streamresponse will get it no

// You're asking a great question! Let me clarify the distinction:

// You're partially right — in main2.py we DO send complete messages:

// yield f"data: {json.dumps(data)}\n\n"  # Complete JSON object + newlines in one yield

// BUT — the network layer (TCP/IP) can still split it across chunks:

// The Real Issue:
// FastAPI yields: One complete SSE message

//"data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n"

// TCP sends it → Can fragment into multiple packets at ANY byte boundary:

// Packet 1: "data: {"choices": [{"delta": {"content": "Hel"
// Packet 2: "lo"}}]}\n\ndata: {"choices": [...]
// Packet 3: ...}}\n\n"

// // Browser/Client receives: Not aligned with our logical messages

// Chunk 1 arrives incomplete
// Chunk 2 arrives with next message starting
// Chunk 3 arrives continuation
// Why Buffer is Still Necessary:
// The network doesn't care about our message boundaries. TCP just sends bytes. So:

// So the buffer is needed to reassemble fragmented messages, even though we send them complete from the server.