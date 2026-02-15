#SOLUTION 1
# import pandas as pd

# df1 = pd.read_csv("data1.csv", encoding="cp1252") #[500 rows x 2 columns]
# df2 = pd.read_csv("data2.csv", encoding="utf-8") #[500 rows x 2 columns]
# df3 = pd.read_csv("data3.txt", encoding="utf-16", sep="\t")#tab separated file [500 rows x 2 columns]
# #print(df3)

# # Combine the dataframes into a single dataframe such that all rows from each dataframe are included ,[1500 rows x 2 columns]
# df = pd.concat([df1, df2, df3])
# # print(df)
# #     symbol  value
# # 0        ‡      0
# # 1        ‹      1
# # 2        ‹      2
# # 3        š      3
# # 4        †      4

# #print(df["symbol"].isin(["‡", "‹"]))  prints a boolean series, eg
# # 0       True
# # 1       True
# # 2       True
# # 3      False
# #
# filtered_df = df[df["symbol"].isin(["‡", "‹"])]  #print only the rows where the symbol is either ‡ or ‹
# # print(filtered_df)
# #     symbol  value
# # 0        ‡      0
# # 1        ‹      1
# # 2        ‹      2
# # 33       ‡     33
# # 45       ‡     45
# filtered_df_values = filtered_df["value"] #print only the values column of the filtered dataframe
# # print(filtered_df_values)
# # 0        0
# # 1        1
# # 2        2
# # 33      33
# # 45      45
# #       ...
# # 448    448
# # 450    450

# sum=filtered_df_values.sum() #sum of all the values in the filtered dataframe
# print("Sum of values for symbols ‡ and ‹:", sum)

# #or in short
# # sum_short = df[df["symbol"].isin(["‡", "‹"])]["value"].sum()
# # print("Sum of values for symbols ‡ and ‹ (short method):", sum_short)


#SOLUTION 2
import csv

total = 0
targets = {"‡", "‹"} #set of target symbols

# data1.csv (CP-1252)
with open("data1.csv", encoding="cp1252", newline="") as f:
    #newline="" tells Python:
    # “Don’t change newline characters automatically. Let the CSV module handle them correctly.”
    # This prevents extra blank lines or incorrect line splitting when reading/writing CSV files.
    #ie this basically prevent blank rows from appearing
    reader = csv.DictReader(f) #reads the CSV file as a dictionary,reader is an iterator that returns each row as a dictionary.
    for row in reader:
        if row["symbol"] in targets:
            total += int(row["value"])

# data2.csv (UTF-8)
with open("data2.csv", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["symbol"] in targets:
            total += int(row["value"])

# data3.txt (UTF-16, tab-separated)
with open("data3.txt", encoding="utf-16", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        if row["symbol"] in targets:
            total += int(row["value"])

print(total)
