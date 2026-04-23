const {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  SystemProgram,
  sendAndConfirmTransaction,
  LAMPORTS_PER_SOL,
} = require("@solana/web3.js");
const { TransactionInstruction } = require("@solana/web3.js");

// Connect to Devnet
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// Your Playground wallet keypair
// We need to import the keypair file you saved earlier
const keypairFile = require("./wallet-keypair.json");
const sender = Keypair.fromSecretKey(new Uint8Array(keypairFile));

// Transaction details
const DESTINATION = new PublicKey("BCJCAvSV89tnGqhFSG2uD8azeQLQ5Hypn9CQyWEN7VEH");
const AMOUNT = 0.014585 * LAMPORTS_PER_SOL; // Convert SOL to Lamports
const MEMO = "7A55-E6B6";

// Memo program ID
const MEMO_PROGRAM_ID = new PublicKey("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr");

async function sendTransactionWithMemo() {
  console.log("Sender address:", sender.publicKey.toString());
  
  // Check balance first
  const balance = await connection.getBalance(sender.publicKey);
  console.log("Balance:", balance / LAMPORTS_PER_SOL, "SOL");

  // Create transfer instruction
  const transferInstruction = SystemProgram.transfer({
    fromPubkey: sender.publicKey,
    toPubkey: DESTINATION,
    lamports: AMOUNT,
  });

  // Create memo instruction
  const memoInstruction = new TransactionInstruction({
    keys: [],
    programId: MEMO_PROGRAM_ID,
    data: Buffer.from(MEMO, "utf-8"),
  });

  // Bundle both instructions into one transaction
  const transaction = new Transaction().add(
    transferInstruction,
    memoInstruction
  );

  console.log("Sending transaction...");
  
  // Send transaction
  const signature = await sendAndConfirmTransaction(
    connection,
    transaction,
    [sender]
  );

  console.log("✅ Transaction successful!");
  console.log("Transaction Signature (TxID):", signature);
  console.log("View on explorer: https://explorer.solana.com/tx/" + signature + "?cluster=devnet");
}

sendTransactionWithMemo().catch(console.error);