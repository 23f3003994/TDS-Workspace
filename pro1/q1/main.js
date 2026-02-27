
// npm install seedrandom crypto-js
// run `node main.js`

//Key insight: Uses ARC4 seedrandom (the default export of the seedrandom npm package),
//  NOT the alea PRNG. This distinction is critical — using the wrong PRNG yields completely incorrect agent IDs.
//by default it uses arc4


const seedrandom = require("seedrandom");
const CryptoJS = require("crypto-js");

const TARGET_AGENT = 89;
const SALT = "tds-share-secret-default-salt";

function getAgentId(email) {
  const seed = "q-share-secret-server#agent-id#" + email;
  const rng = seedrandom(seed);
  return Math.floor(rng() * 100);
}

function getPassword(email) {
  const text = `q-share-secret-server#${SALT}#${email}`;
  const hash = CryptoJS.SHA256(text).toString(CryptoJS.enc.Hex);
  return hash.slice(0, 16);
}

const years = ["21", "22", "23", "24"];
const batches = ["f1", "f2", "f3"];



for (const year of years) {
  for (const batch of batches) {
    const prefix = year + batch;

    for (let roll = 1; roll < 1000000; roll++) {
      const rollStr = String(roll).padStart(6, "0");
      const email = `${prefix}${rollStr}@ds.study.iitm.ac.in`;

      const agentId = getAgentId(email);

      if (agentId === TARGET_AGENT) {
        const password = getPassword(email);

        console.log("\n FOUND AGENT 089!");
        console.log("Email:", email);
        console.log("Password:", password);
        process.exit(0);
      }
    }
  }
}


// console.log(getAgentId("23f3003994@ds.study.iitm.ac.in"))
// console.log(getPassword("23f3003994@ds.study.iitm.ac.in"))