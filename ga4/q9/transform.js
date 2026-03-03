// Function to split an array into chunks of a specified size
// Description: Takes an array and divides it into smaller sub-arrays (chunks) of the given size

function splitArray(array, chunkSize = 3) {
  // Initialize an empty array that will store all the chunks
  const chunks = [];
  
  // Loop through the array starting at index 0, incrementing by chunkSize each iteration
  for (let i = 0; i < array.length; i += chunkSize) {
    // Extract elements from position i up to position i + chunkSize using slice method
    // slice() returns a shallow copy without modifying the original array
    const chunk = array.slice(i, i + chunkSize);
    
    // Add the extracted chunk to the chunks array
    chunks.push(chunk);
  }
  
  // Return the complete array containing all chunks
  return chunks;
}

// ============================================
// HOW TO RUN THIS CODE WITH NODE:
// 1. Save this file as transform.js
// 2. Open your terminal/command prompt
// 3. Navigate to the directory containing this file
// 4. Run: node transform.js
// ============================================

// Test data: array of numbers 1 through 8
const testData = [1, 2, 3, 4, 5, 6, 7, 8];

// Call the function with testData and chunk size of 3
// Expected output: [ [ 1, 2, 3 ], [ 4, 5, 6 ], [ 7, 8 ] ]
console.log('Result:', splitArray(testData, 3));
