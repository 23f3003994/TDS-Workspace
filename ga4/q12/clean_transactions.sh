#!/bin/bash

INPUT="transactions.csv"

echo "Step 1: Normalize separators (convert commas to pipes)..."
sed 's/,/|/g' "$INPUT" > step1_normalized.csv


echo "Step 2: Clean extra whitespace around separators..."
sed 's/ *| */|/g' step1_normalized.csv > step2_whitespace_fixed.csv


echo "Step 3: Remove header and fix broken rows..."
# After normalization, some rows may have extra columns.
# We enforce exactly 6 fields: ID|Date|Amount|Category|Merchant|City
# header row is skipped nr>1
awk -F'|' '
NR > 1 { 
    # If more than 6 fields, merge properly
    if (NF > 6) {
        # Rebuild correct structure
        $1=$1;  # force field rebuild
    }
    print $1 "|" $2 "|" $3 "|" $4 "|" $5 "|" $6
}
' OFS='|' step2_whitespace_fixed.csv > step3_structured.csv


echo "Step 4: Remove rows with missing Category..."
awk -F'|' '$4 != ""' step3_structured.csv > step4_filtered.csv


echo "Step 5: Aggregate totals per category..."
awk -F'|' '
{
    sum[$4] += $3
}
END {
    for (cat in sum)
        printf "%s:%.2f\n", cat, sum[cat]
}
' step4_filtered.csv | sort > step5_totals.txt


echo "Step 6: Format final output..."
awk 'ORS="|"' step5_totals.txt | sed 's/|$//' > final_output.txt


echo "Done!"
echo "Final result:"
cat final_output.txt