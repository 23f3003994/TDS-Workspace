function convertToMarkdown(text) {
  // 1. Define the Maps (Easy to read and edit)
  const NORMAL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const BOLD   = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵";
  const ITALIC = "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘<i>𝘙</i>𝘚𝘛<i>𝘜</i>𝘝𝘞𝘟𝘠𝘡<i>𝘢</i>𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻";
  const MONO   = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿";
  const BULLETS = ["•", "◦", "▪", "▸", "‣"];

  // Helper to swap styled characters for normal ones
  function unstyle(str, styleMap) {
    const sourceChars = Array.from(styleMap);
    const normalChars = Array.from(NORMAL);
    return Array.from(str)
      .map(char => {
        const index = sourceChars.indexOf(char);
        return index !== -1 ? normalChars[index] : char;
      })
      .join("");
  }

  // 2. Replace Bullets
  BULLETS.forEach(b => {
    text = text.replaceAll(b, "-");
  });

  // 3. Convert Styles using Regex
  // The 'u' flag is vital for these double-width Unicode characters
  text = text.replace(new RegExp(`[${BOLD}]+`, "gu"),   m => `**${unstyle(m, BOLD)}**`);
  text = text.replace(new RegExp(`[${ITALIC}]+`, "gu"), m => `*${unstyle(m, ITALIC)}*`);
  text = text.replace(new RegExp(`[${MONO}]+`, "gu"),   m => `\`${unstyle(m, MONO)}\``);

  // 4. Handle Multi-line Code Blocks
  const lines = text.split("\n");
  const result = [];
  let i = 0;

  while (i < lines.length) {
    let block = [];
    // Check if the line is just an inline code snippet: `text`
    while (i < lines.length && /^`.*`$/.test(lines[i].trim())) {
      block.push(lines[i].trim().slice(1, -1)); // Remove the `
      i++;
    }

    if (block.length >= 3) {
      result.push("```", ...block, "```");
    } else if (block.length > 0) {
      // Put them back as they were if the block is too short
      block.forEach(l => result.push("`" + l + "`"));
    } else {
      result.push(lines[i]);
      i++;
    }
  }

  return result.join("\n");
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