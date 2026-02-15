//CODE-3 (working in terminal (didn't submit))
//CODE-2 fixed by claude ai success for all test cases

/**
 * Converts Unicode-styled social media text into standard Markdown.
 * Handles Bold, Italic, Monospace, and Bullets.
 */
function convertToMarkdown(text) {
  // ===== Character Maps =====
  const NORMAL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  const BOLD =
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭" +
    "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇" +
    "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵";

  const ITALIC =
    "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡" +
    "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻";//for digits italics is the same

  const MONO =
    "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉" +
    "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣" +
    "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿";

  const BULLETS = ["•", "◦", "▪", "▸", "‣"];

  // ===== Helper: Map styled chars to normal =====
  // This function maps fancy Unicode characters to normal characters
  // We use Array.from() to safely handle 4-byte Unicode characters 
  //it Creates an array from an iterable object.
  function mapChars(str, sourceStr, targetStr) {
     // Convert the fancy source string into an array of characters
    const sourceChars = Array.from(sourceStr);
    // Convert the normal target string into an array of characters
    const targetChars = Array.from(targetStr);

    
    //map Calls a defined callback function on each element of an array (Array.from(str)), and returns an array that contains the results.
    //so it takes each character in array of str to corresponding normal character in targetStr..and that list of chars is joined with empty string'' and returns back a string

        // For each character in the input string 'str'
    return Array.from(str).map(ch => {
      const idx = sourceChars.indexOf(ch);
      // If found, return the corresponding normal character
      if( idx !== -1 ){
        return targetChars[idx]
      }else{
        // If not found, return the character as it is
        return ch
      }
    }).join('');// Join all mapped characters back into a single string//  join---> Adds all the elements of an array into a string, separated by the specified separator string.
  }

  // 1️⃣ Replace bullets with "-"
  let result = text;
  // For each bullet symbol
  BULLETS.forEach(b => {
    // Split text into lines
    result = result.split('\n').map(line => {
       // If line starts with bullet(coz we dont want to add bullet if its in the middle of a sentece , usually that doesnt happen , but still safe to do it) (ignoring spaces), replace it with "-", otherwise dont do anything
        return line.trimStart().startsWith(b) ? line.replace(b, "-") : line;
    }).join('\n'); // Join lines back
  });

  // 2️⃣ Convert BOLD fancy text to Markdown **bold**
  // Create regex that matches any sequence of bold Unicode characters
  // The 'u' flag is crucial for Unicode regex
  const boldRegex = new RegExp(`[${BOLD}]+`, "gu");
  // Replace matched bold fancy text with **normalText**
  result = result.replace(boldRegex, match => `**${mapChars(match, BOLD, NORMAL)}**`);

  // 3️⃣ Convert ITALIC
  const italicRegex = new RegExp(`[${ITALIC}]+`, "gu");
   // Replace matched italic fancy text with *normalText*
  result = result.replace(italicRegex, match => `*${mapChars(match, ITALIC, NORMAL)}*`);

  // 4️⃣ Convert MONOSPACE (Inline)
  const monoRegex = new RegExp(`[${MONO}]+`, "gu");
 // Replace matched monospace fancy text with `normalText`
  result = result.replace(monoRegex, match => `\`${mapChars(match, MONO, NORMAL)}\``);

  // ========================================
  // STEP 5: MULTI-LINE CODE BLOCK DETECTION
  // ========================================
  
  /**
   * Detect and convert multi-line code blocks within the document
   * 
   * Strategy: Find consecutive lines (3+) that are all wrapped in backticks
   * and convert them into a proper markdown code block.
   * 
   * This handles both:
   * 1. Entire document is code (original use case)
   * 2. Code blocks within mixed content documents (new fix)
   * 
   * Algorithm:
   * - Scan through lines looking for sequences of 3+ consecutive code lines
   * - A "code line" is one that starts and ends with backticks
   * - When found, replace the sequence with a triple-backtick code block
   * 
   * Example in mixed document:
   * Input after Step 4:
   *   **Title**
   *   
   *   `function hello`
   *   `const x 123`
   *   `return x`
   *   
   *   - Point 1
   * 
   * Output:
   *   **Title**
   *   
   *   ```
   *   function hello
   *   const x 123
   *   return x
   *   ```
   *   
   *   - Point 1
   */
  const lines = result.split("\n");
  const processedLines = [];
  let i = 0;
  
  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();
    
    // Check if this line is a code line (starts and ends with backticks)
    const isCodeLine = trimmed.startsWith('`') && trimmed.endsWith('`') && trimmed.length > 2;
    
    if (isCodeLine) {
      // Found a potential code line, check if there are consecutive code lines
      let consecutiveCodeLines = [line];
      let j = i + 1;
      
      // Collect consecutive code lines (skip empty lines between them)
      while (j < lines.length) {
        const nextLine = lines[j];
        const nextTrimmed = nextLine.trim();
        
        // If empty line, check if code continues after it
        if (nextTrimmed === "") {
          // Peek ahead to see if more code is coming
          let peekIndex = j + 1;
          let foundMoreCode = false;
          
          while (peekIndex < lines.length) {
            const peekTrimmed = lines[peekIndex].trim();
            if (peekTrimmed === "") {
              peekIndex++;
              continue;
            }
            // Found non-empty line, check if it's code
            foundMoreCode = peekTrimmed.startsWith('`') && peekTrimmed.endsWith('`') && peekTrimmed.length > 2;
            break;
          }
          
          if (foundMoreCode) {
            // Include the empty line as part of the code block
            consecutiveCodeLines.push(nextLine);
            j++;
          } else {
            // No more code after this empty line, stop here
            break;
          }
        } else if (nextTrimmed.startsWith('`') && nextTrimmed.endsWith('`') && nextTrimmed.length > 2) {
          // This is a code line, add it
          consecutiveCodeLines.push(nextLine);
          j++;
        } else {
          // Not a code line and not empty, stop collecting
          break;
        }
      }
      
      // Count actual code lines (non-empty lines with backticks)
      const actualCodeLines = consecutiveCodeLines.filter(l => {
        const t = l.trim();
        return t.startsWith('`') && t.endsWith('`') && t.length > 2;
      });
      
      // If we have 3+ consecutive code lines, convert to code block
      if (actualCodeLines.length >= 3) {
        // Remove backticks from all lines in the block
        const cleanedLines = consecutiveCodeLines.map(l => l.replace(/`/g, ""));
        
        // Add code block with triple backticks
        processedLines.push("```");
        processedLines.push(...cleanedLines);
        processedLines.push("```");
        
        // Skip all the lines we just processed
        i = j;
      } else {
        // Not enough consecutive code lines, keep as inline code
        processedLines.push(line);
        i++;
      }
    } else {
      // Not a code line, keep as is
      processedLines.push(line);
      i++;
    }
  }
  
  // Join all processed lines back together
  return processedLines.join("\n");
}

//========================================
// COMPREHENSIVE TEST CASES
// ========================================

console.log("========================================");
console.log("TEST SUITE FOR convertToMarkdown()");
console.log("========================================\n");

// Test Case 1: Bold Text
console.log("Test 1: Bold Text");
console.log("Input:  '𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱'");
const test1 = convertToMarkdown("𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱");
console.log("Output: '" + test1 + "'");
console.log("Expected: '**Hello** **World**'");
console.log("Pass: " + (test1 === "**Hello** **World**") + "\n");

// Test Case 2: Italic Text
console.log("Test 2: Italic Text");
console.log("Input:  '𝘛𝘩𝘪𝘴 𝘪𝘴 𝘪𝘵𝘢𝘭𝘪𝘤'");
const test2 = convertToMarkdown("𝘛𝘩𝘪𝘴 𝘪𝘴 𝘪𝘵𝘢𝘭𝘪𝘤");
console.log("Output: '" + test2 + "'");
console.log("Expected: '*This* *is* *italic*'");
console.log("Pass: " + (test2 === "*This* *is* *italic*") + "\n");

// Test Case 3: Inline Code
console.log("Test 3: Inline Code");
console.log("Input:  'Use 𝚌𝚘𝚗𝚜𝚝 for constants'");
const test3 = convertToMarkdown("Use 𝚌𝚘𝚗𝚜𝚝 for constants");
console.log("Output: '" + test3 + "'");
console.log("Expected: 'Use `const` for constants'");
console.log("Pass: " + (test3 === "Use `const` for constants") + "\n");

// Test Case 4: Mixed Bold and Italic
console.log("Test 4: Mixed Bold and Italic");
console.log("Input:  '𝗕𝗼𝗹𝗱 and 𝘪𝘵𝘢𝘭𝘪𝘤 text'");
const test4 = convertToMarkdown("𝗕𝗼𝗹𝗱 and 𝘪𝘵𝘢𝘭𝘪𝘤 text");
console.log("Output: '" + test4 + "'");
console.log("Expected: '**Bold** and *italic* text'");
console.log("Pass: " + (test4 === "**Bold** and *italic* text") + "\n");

// Test Case 5: Bullet List
console.log("Test 5: Bullet List");
const bulletInput = "• First item\n▪ Second item\n◦ Third item";
console.log("Input:\n" + bulletInput);
const test5 = convertToMarkdown(bulletInput);
console.log("Output:\n" + test5);
const expected5 = "- First item\n- Second item\n- Third item";
console.log("Expected:\n" + expected5);
console.log("Pass: " + (test5 === expected5) + "\n");

// Test Case 6: Multi-line Code Block
console.log("Test 6: Multi-line Code Block");
const codeInput = "𝚏𝚞𝚗𝚌𝚝𝚒𝚘𝚗 𝚑𝚎𝚕𝚕𝚘\n𝚌𝚘𝚗𝚜𝚝 𝚡 𝟷𝟸𝟹\n𝚛𝚎𝚝𝚞𝚛𝚗 𝚡";
console.log("Input:\n" + codeInput);
const test6 = convertToMarkdown(codeInput);
console.log("Output:\n" + test6);
const expected6 = "```\nfunction hello\nconst x 123\nreturn x\n```";
console.log("Expected:\n" + expected6);
console.log("Pass: " + (test6 === expected6) + "\n");

// Test Case 7: Complex Document
console.log("Test 7: Complex Document with Multiple Formats");
const complexInput = "𝗧𝗶𝘁𝗹𝗲\n\n𝘋𝘦𝘴𝘤𝘳𝘪𝘱𝘵𝘪𝘰𝘯 text\n\n• Point 1\n• Point 2\n\nUse 𝚌𝚘𝚍𝚎 here";
console.log("Input:\n" + complexInput);
const test7 = convertToMarkdown(complexInput);
console.log("Output:\n" + test7);
console.log("(Complex output - manual verification needed)\n");

// Test Case 8: Code with Numbers
console.log("Test 8: Code with Numbers");
console.log("Input:  '𝙲𝙾𝙳𝙴 𝟷𝟸𝟹 𝚝𝚎𝚜𝚝'");
const test8 = convertToMarkdown("𝙲𝙾𝙳𝙴 𝟷𝟸𝟹 𝚝𝚎𝚜𝚝");
console.log("Output: '" + test8 + "'");
console.log("Expected: '`CODE` `123` `test`'");
console.log("Pass: " + (test8 === "`CODE` `123` `test`") + "\n");

// Test Case 9: Complex Document with Embedded Code Block (THE FAILING CASE - NOW FIXED!)
console.log("Test 9: Complex Document with Embedded Multi-line Code Block");
const complexInput2 = "𝗧𝗶𝘁𝗹𝗲\n\n𝘋𝘦𝘴𝘤𝘳𝘪𝘱𝘵𝘪𝘰𝘯 text\n\n𝚏𝚞𝚗𝚌𝚝𝚒𝚘𝚗 𝚑𝚎𝚕𝚕𝚘\n𝚌𝚘𝚗𝚜𝚝 𝚡 𝟷𝟸𝟹\n𝚛𝚎𝚝𝚞𝚛𝚗 𝚡\n\n• Point 1\n• Point 2\n\nUse 𝚌𝚘𝚍𝚎 here";
console.log("Input:\n" + complexInput2);
const test9 = convertToMarkdown(complexInput2);
console.log("Output:\n" + test9);
const expected9 = "**Title**\n\n*Description* text\n\n```\nfunction hello\nconst x 123\nreturn x\n```\n\n- Point 1\n- Point 2\n\nUse `code` here";
console.log("\nExpected:\n" + expected9);
console.log("\n✓ Pass: " + (test9 === expected9));
if (test9 === expected9) {
  console.log("✓ Code block properly wrapped with triple backticks");
  console.log("✓ Inline code remains single backtick");
} else {
  console.log("❌ Output doesn't match expected");
  console.log("Note: If there's a mismatch, check that 'Description' uses pure italic characters");
}
console.log();

// Original Test Case from the file
console.log("Original Test Case:");
const originalInput = `𝗛𝗲𝗹𝗹𝗼
𝘪𝘵𝘢𝘭𝘪𝘤 𝘵𝘦𝘹𝘵
𝙲𝙾𝙳𝙴 𝟷𝟸𝟹
• item one
▪ item two`;
console.log("Input:\n" + originalInput);
const originalOutput = convertToMarkdown(originalInput);
console.log("\nOutput:\n" + originalOutput);

console.log("\n========================================");
console.log("TEST SUITE COMPLETE");
console.log("========================================");

