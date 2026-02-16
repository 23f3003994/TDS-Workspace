#method-1
# use https://elevenlabs.io/audio-to-text and map words  to digits
#map words to digits

#step1: run #awk -F',' '{print NF}' filename.txt  to make sure 300 elements on audio.txt


def word_to_digit(word):
    convert_dict = {"zero": 0,"one": 1,"two": 2,"three": 3,"four": 4,"five": 5,"six": 6,"seven": 7,"eight": 8,"nine": 9}
    return convert_dict.get(word, None)

#paste the word text here, remove the last "." from word text (eleven labs gave last extra "two"(so 301) i checked with another transcriber two was not there and so removed it)
word_text="Five, eight, zero, three, four, five, two, five, zero, three, five, five, six, four, three, two, eight, zero, eight, eight, six, two, three, two, zero, three, five, seven, three, four, six, eight, five, three, eight, nine, five, zero, eight, seven, seven, one, one, eight, zero, six, eight, nine, six, one, eight, zero, seven, two, two, two, three, two, one, four, three, seven, two, five, five, zero, three, five, nine, one, six, four, four, eight, four, one, six, four, eight, two, one, nine, six, five, two, three, zero, six, one, three, nine, eight, one, five, six, zero, seven, one, three, six, nine, eight, eight, eight, two, three, six, three, two, six, four, five, one, six, nine, three, two, six, three, six, six, nine, zero, nine, five, seven, one, five, eight, seven, seven, six, six, zero, two, five, seven, three, eight, nine, three, four, five, four, two, two, one, eight, six, four, two, three, five, four, five, eight, nine, one, seven, six, seven, zero, eight, three, eight, three, seven, nine, zero, three, seven, three, six, six, seven, four, five, eight, two, seven, zero, one, eight, three, four, seven, one, two, nine, seven, two, one, four, five, one, nine, nine, seven, three, one, zero, seven, nine, seven, six, one, nine, four, eight, eight, five, two, nine, three, five, zero, eight, three, seven, eight, five, four, one, seven, four, nine, four, zero, three, four, five, two, four, nine, eight, seven, seven, one, four, one, one, two, four, six, eight, zero, four, four, nine, four, seven, zero, three, two, one, four, zero, nine, eight, three, six, five, two, two, two, zero, five, four, three, two, three, zero, one, eight, two, one, nine, seven, nine, two, six, six, six, nine, seven, three, nine, three, four, zero, seven, nine, seven, seven, five, four, zero, one, eight, four"
#word.strip() removes leading and trailing whitespace characters, and .lower() converts the word to lowercase to ensure it matches the keys in the convert_dict.
# Split by comma
elements = word_text.split(",")
print("Number of elements before stripping:", len(elements))

# Remove extra spaces
digits = [word.strip().lower() for word in elements]

#check if all elements are valid digit words
for digit in digits:
    if word_to_digit(digit) is None:
        print(f"Warning: '{digit}' is not a valid digit word.")

digits = [word_to_digit(digit) for digit in digits ]

print("Number of elements:", len(digits))


#check if length of digits is 300, if not return error

if len(digits) != 300:
    raise ValueError("The number of digits is not 300")

#convert list of digits to a single number
number=""
for digit in digits:
    number+=str(digit)
print(number)
print("Length of number:", len(number))


hash="0b378e079d7242820e28bf0fb2a100abba63899347f7bf70a50d662f24f9651f"

#return in json format
import json
result={"number": number, "hash": hash}
print(json.dumps(result))
