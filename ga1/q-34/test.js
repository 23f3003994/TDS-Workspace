//chatgpt code-submitted and passed but not right answer

// // ===== Character Maps =====
// const NORMAL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

// const BOLD =
//   "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭" +
//   "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇" +
//   "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟕𝟴𝟵";

// const ITALIC =
//   "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡" +
//   "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻";

// const MONO =
//   "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉" +
//   "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣" +
//   "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿";

// // Bullet characters to replace
// const BULLETS = ["•", "◦", "▪", "▸", "‣"];

// // ===== Helper: map styled chars to normal =====
// function mapChars(text, source, target) {
//   let result = "";
//   console.log(text)
//   for (let ch of text) {
//     const idx = source.indexOf(ch);
//      console.log(`Character: ${ch}, Index: ${idx}`); // Debugging line
//     if (idx !== -1){
//     result += target[idx] 
//     } else{
//         result+= ch
//   }
//   return result;
// }
// };
// // ===== Main Function =====
// function convertToMarkdown(text) {
//   // 1️⃣ Replace bullets with "-"
//   BULLETS.forEach(b => {
//     text = text.replaceAll(b, "-");
//   });

//   // 2️⃣ Convert BOLD
//   // replace() with /g runs for "EVERY match" automatically, for each match callback runs, ie each match replaced by the returnedvalue, internally its like
//   //call function("𝗛𝗲𝗹𝗹𝗼")
//   //call function("𝗪𝗼𝗿𝗹𝗱")
// // 'match' = the substring that matched the regex
// // We convert that substring to normal characters
// // The returned string replaces that matched substring in text
// //`string${var}string`-->template literal so here we create a new regex with bold chars like [ABCD....012..9]+g 
// //  coz just [A-9] or [A-za-z0-9] using bold chars is not working
//   const boldRegex = new RegExp(`[${BOLD}]+`, "gu");
//   text = text.replace(boldRegex, match => {
//     const converted = mapChars(match, BOLD, NORMAL);
//     return `**${converted}**`;
//   });

//   // 3️⃣ Convert ITALIC
//   const italicRegex = new RegExp(`[${ITALIC}]+`, "gu");
//   text = text.replace(italicRegex, match => {
//     const converted = mapChars(match, ITALIC, NORMAL);
//     return `*${converted}*`;
//   });

//   // 4️⃣ Convert MONOSPACE (inline first)
//   const monoRegex = new RegExp(`[${MONO}]+`, "gu");
//   text = text.replace(monoRegex, match => {
//     const converted = mapChars(match, MONO, NORMAL);
//     return `\`${converted}\``;
//   });

//   // 5️⃣ Detect multi-line monospace → code block
//   const lines = text.split("\n");
//   let monoCount = 0;

//   for (let line of lines) {
//     if (/^`.*`$/.test(line.trim())) monoCount++;
//   }

//   if (monoCount >= 3) {
//     const cleaned = lines.map(l => l.replace(/`/g, "")).join("\n");
//     return "```\n" + cleaned + "\n```";
//   }

//   return text;
// }


/// gemini
// /**
//  * Converts Unicode-styled social media text into standard Markdown.
//  * Handles Bold, Italic, Monospace, and Bullets.
//  */
// function convertToMarkdown(text) {
//   // ===== Character Maps =====
//   const NORMAL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

//   const BOLD =
//     "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭" +
//     "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇" +
//     "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵";

//   const ITALIC =
//     "𝘈𝘉𝘊𝘋<i>𝘌</i>𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘<i>𝘙</i>𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡" +
//     "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻";

//   const MONO =
//     "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉" +
//     "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣" +
//     "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿";

//   const BULLETS = ["•", "◦", "▪", "▸", "‣"];

//   // ===== Helper: Map styled chars to normal =====
//   // We use Array.from() to safely handle 4-byte Unicode characters
//   function mapChars(str, sourceStr, targetStr) {
//     const sourceChars = Array.from(sourceStr);
//     const targetChars = Array.from(targetStr);
    
//     return Array.from(str).map(ch => {
//       const idx = sourceChars.indexOf(ch);
//       return idx !== -1 ? targetChars[idx] : ch;
//     }).join('');
//   }

//   // 1️⃣ Replace bullets
//   let result = text;
//   BULLETS.forEach(b => {
//     result = result.split('\n').map(line => {
//         return line.trimStart().startsWith(b) ? line.replace(b, "-") : line;
//     }).join('\n');
//   });

//   // 2️⃣ Convert BOLD
//   // The 'u' flag is crucial for Unicode regex
//   const boldRegex = new RegExp(`[${BOLD}]+`, "gu");
//   result = result.replace(boldRegex, match => `**${mapChars(match, BOLD, NORMAL)}**`);

//   // 3️⃣ Convert ITALIC
//   const italicRegex = new RegExp(`[${ITALIC}]+`, "gu");
//   result = result.replace(italicRegex, match => `*${mapChars(match, ITALIC, NORMAL)}*`);

//   // 4️⃣ Convert MONOSPACE (Inline)
//   const monoRegex = new RegExp(`[${MONO}]+`, "gu");
//   result = result.replace(monoRegex, match => `\`${mapChars(match, MONO, NORMAL)}\``);

//   // 5️⃣ Detect Multi-line Code Block
//   const lines = result.split("\n");
//   let isMultiLineCode = lines.every(line => {
//     const trimmed = line.trim();
//     return trimmed === "" || (trimmed.startsWith('`') && trimmed.endsWith('`'));
//   }) && lines.filter(l => l.trim() !== "").length >= 3;

//   if (isMultiLineCode) {
//     const cleaned = lines.map(l => l.replace(/`/g, "")).join("\n");
//     return "```\n" + cleaned + "\n```";
//   }

//   return result;
// }



//gemini2---working
function convertToMarkdown(text) {
  // Define the Unicode starting points (offsets) for different styles
  const maps = [
    { 
      // Bold (Sans-serif Bold)
      regex: /[\u{1D5EE}-\u{1D607}\u{1D5D4}-\u{1D5ED}\u{1D7EC}-\u{1D7F5}]+/gu, 
      prefix: '**', suffix: '**', 
      offsetMap: (char) => {
        const code = char.codePointAt(0);
        if (code >= 0x1D5D4 && code <= 0x1D5ED) return String.fromCodePoint(code - 0x1D5D4 + 65); // A-Z
        if (code >= 0x1D5EE && code <= 0x1D607) return String.fromCodePoint(code - 0x1D5EE + 97); // a-z
        if (code >= 0x1D7EC && code <= 0x1D7F5) return String.fromCodePoint(code - 0x1D7EC + 48); // 0-9
        return char;
      }
    },
    { 
      // Italic (Sans-serif Italic)
      regex: /[\u{1D622}-\u{1D63B}\u{1D608}-\u{1D621}]+/gu, 
      prefix: '*', suffix: '*', 
      offsetMap: (char) => {
        const code = char.codePointAt(0);
        if (code >= 0x1D608 && code <= 0x1D621) return String.fromCodePoint(code - 0x1D608 + 65); // A-Z
        if (code >= 0x1D622 && code <= 0x1D63B) return String.fromCodePoint(code - 0x1D622 + 97); // a-z
        return char;//digits are usually not italized..they are normal
      }
    },
    { 
      // Monospace (Code)
      regex: /[\u{1D670}-\u{1D6A3}\u{1D7F6}-\u{1D7FF}]+/gu, 
      prefix: '`', suffix: '`', 
      offsetMap: (char) => {
        const code = char.codePointAt(0);
        if (code >= 0x1D670 && code <= 0x1D689) return String.fromCodePoint(code - 0x1D670 + 65); // A-Z
        if (code >= 0x1D68A && code <= 0x1D6A3) return String.fromCodePoint(code - 0x1D68A + 97); // a-z
        if (code >= 0x1D7F6 && code <= 0x1D7FF) return String.fromCodePoint(code - 0x1D7F6 + 48); // 0-9
        return char;
      }
    }
  ];

  let processedText = text;

  // 1. Handle Bullets first
  const BULLETS = ["•", "◦", "▪", "▸", "‣"];
  processedText = processedText.split('\n').map(line => {
    let trimmed = line.trimStart();
    if (BULLETS.some(b => trimmed.startsWith(b))) {
      return line.replace(new RegExp(`[${BULLETS.join('')}]`), '-');
    }
    return line;
  }).join('\n');

  // 2. Map Unicode styles to standard characters + Markdown tags
  maps.forEach(({ regex, prefix, suffix, offsetMap }) => {
    processedText = processedText.replace(regex, (match) => {
      const normalChars = Array.from(match).map(offsetMap).join('');
      return `${prefix}${normalChars}${suffix}`;
    });
  });

  // 3. Handle Multi-line Code Blocks
  // If 3+ consecutive lines are wrapped in backticks, merge them into a code fence
  const lines = processedText.split('\n');
  const resultLines = [];
  let i = 0;

  while (i < lines.length) {
    let codeBlock = [];
    while (i < lines.length && lines[i].startsWith('`') && lines[i].endsWith('`')) {
      codeBlock.push(lines[i].slice(1, -1)); // Strip the inline backticks
      i++;
    }

    if (codeBlock.length >= 3) {
      resultLines.push('```');
      resultLines.push(...codeBlock);
      resultLines.push('```');
    } else if (codeBlock.length > 0) {
      // If less than 3 lines, keep them as inline code
      codeBlock.forEach(line => resultLines.push('`' + line + '`'));
    } else {
      resultLines.push(lines[i]);
      i++;
    }
  }

  return resultLines.join('\n');
}

// ===== Test =====
const input = `𝗛𝗲𝗹𝗹𝗼
𝘪𝘵𝘢𝘭𝘪𝘤 𝘵𝘦𝘹𝘵
𝙲𝙾𝙳𝙴 𝟷𝟸𝟹
• item one
▪ item two`;


//𝗛𝗲𝗹𝗹𝗼\n𝘪𝘵𝘢𝘭𝘪𝘤 𝘵𝘦𝘹𝘵\n𝙲𝙾𝙳𝙴 𝟷𝟸𝟹\n• item one\n▪ item two
//first we convert change bullets to - -->then bold to **normal**--> then italic to *normal*-->monospace to `normal`
//**Hello**\n*italic* *text*\n`code` `123`\n- item one\n- item two
 

console.log(convertToMarkdown(input));


// Your function will be tested with 8 test cases:
// Bold text
// Italic text
// Inline code
// Mixed bold and italic
// Bullet list
// Multi-line code block
// Complex document
// Code with numbers


 
// text.replace(regex, replacement)
// If regex has /g → replaces every match

// If no /g → replaces only first match

//its like s/regex/replacement/g or s/regex/replacement



  //text.replace(pattern, function(match) {
  // decide replacement dynamically
  // });

  //or using arrow fn
// text.replace(pattern,(match) => {
//   
// });

 // 1️⃣ The regex /[regx]+/g finds chunks of bold Unicode text
  // Example match could be: "𝗕𝗼𝗹𝗱"

  // 2️⃣ For every match found, replace() calls this arrow function
  // and passes the matched substring as the parameter "match"

    // replace() with /g runs for "EVERY match" automatically, for each match callback runs, ie each match replaced by the returnedvalue, internally its like
  //call function("𝗛𝗲𝗹𝗹𝗼")
  //call function("𝗪𝗼𝗿𝗹𝗱")
// 'match' = the substring that matched the regex
// We convert that substring to normal characters
// The returned string replaces that matched substring in text

  // 3️⃣ We convert each fancy Unicode character to normal letters
 // e.g. "𝗕𝗼𝗹𝗱" -> "Bold"

  // 4️⃣ The function RETURNS the replacement string
  // This returned value replaces the original matched substring in the text
  
  // e.g. returns "**Bold**"


//   Meaning of ${}:- template literals in JavaScript.

// It inserts the variable value inside a string.
//return "**" + converted + "**"; or return `**${converted}**`;

//order matters
// Correct order:
// 1.	bullets
// 2.	bold
// 3.	italic
// 4.	monospace inline
// 5.	multi-line code block (final pass)
// Why?
// Because code blocks shouldn’t get wrapped inside * or **.

