#method-1
# use https://elevenlabs.io/audio-to-text and map words  to digits
#map words to digits

#step1: run #awk -F',' '{print NF}' filename.txt  to make sure 300 elements on audio.txt


def word_to_digit(word):
    convert_dict = {"zero": 0,"one": 1,"two": 2,"three": 3,"four": 4,"five": 5,"six": 6,"seven": 7,"eight": 8,"nine": 9}
    return convert_dict.get(word, None)

#paste the word text here, remove the last "." from word text (eleven labs gave last extra "two"(so 301) i checked with another transcriber two was not there and so removed it)
#word_text="Five, eight, zero, three, four, five, two, five, zero, three, five, five, six, four, three, two, eight, zero, eight, eight, six, two, three, two, zero, three, five, seven, three, four, six, eight, five, three, eight, nine, five, zero, eight, seven, seven, one, one, eight, zero, six, eight, nine, six, one, eight, zero, seven, two, two, two, three, two, one, four, three, seven, two, five, five, zero, three, five, nine, one, six, four, four, eight, four, one, six, four, eight, two, one, nine, six, five, two, three, zero, six, one, three, nine, eight, one, five, six, zero, seven, one, three, six, nine, eight, eight, eight, two, three, six, three, two, six, four, five, one, six, nine, three, two, six, three, six, six, nine, zero, nine, five, seven, one, five, eight, seven, seven, six, six, zero, two, five, seven, three, eight, nine, three, four, five, four, two, two, one, eight, six, four, two, three, five, four, five, eight, nine, one, seven, six, seven, zero, eight, three, eight, three, seven, nine, zero, three, seven, three, six, six, seven, four, five, eight, two, seven, zero, one, eight, three, four, seven, one, two, nine, seven, two, one, four, five, one, nine, nine, seven, three, one, zero, seven, nine, seven, six, one, nine, four, eight, eight, five, two, nine, three, five, zero, eight, three, seven, eight, five, four, one, seven, four, nine, four, zero, three, four, five, two, four, nine, eight, seven, seven, one, four, one, one, two, four, six, eight, zero, four, four, nine, four, seven, zero, three, two, one, four, zero, nine, eight, three, six, five, two, two, two, zero, five, four, three, two, three, zero, one, eight, two, one, nine, seven, nine, two, six, six, six, nine, seven, three, nine, three, four, zero, seven, nine, seven, seven, five, four, zero, one, eight, four"
word_text="Seven seven six zero one one five two six zero two six zero four three nine eight nine nine seven six nine zero two two eight nine six eight nine one five zero one three four two six eight one seven two three zero four three nine seven five six four nine three three one zero four three seven one zero nine zero eight three three two three seven one six two seven nine three five six two zero seven two six one five three three three nine four two nine one nine five five four two zero three one two six zero six eight two eight seven zero three seven four three nine three seven four zero two eight three nine seven zero zero eight six eight eight four five one nine five one four one two four five seven six one six one six zero eight six six two four nine one five three five three two five seven nine zero seven two four seven eight eight eight five nine five zero five one eight one seven six six seven seven three four five two two two nine nine one seven six seven eight five eight five four two nine four zero zero seven zero seven zero two five eight eight three zero one two three four two two five six five six six seven two eight four two six two one six seven nine four seven three nine zero nine four six nine eight one two two nine seven three five nine one zero five zero eight three seven two eight five eight one one three nine six seven eight one eight five two six seven zero five one zero eight eight two three zero six two six seven six six four two eight two six two"
#word.strip() removes leading and trailing whitespace characters, and .lower() converts the word to lowercase to ensure it matches the keys in the convert_dict.
# Split by comma
elements = word_text.split(" ") #for audio.txt it was ","
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


# hash="0b378e079d7242820e28bf0fb2a100abba63899347f7bf70a50d662f24f9651f"
hash="9ed3e8e556756ab1860a29e156ac970923d463aee2a4a18041c19f3b98754e88"
#return in json format
import json
result={"number": number, "hash": hash}
print(json.dumps(result))

#old answer
# {"number": "580345250355643280886232035734685389508771180689618072223214372550359164484164821965230613981560713698882363264516932636690957158776602573893454221864235458917670838379037366745827018347129721451997310797619488529350837854174940345249877141124680449470321409836522205432301821979266697393407977540184", "hash": "0b378e079d7242820e28bf0fb2a100abba63899347f7bf70a50d662f24f9651f"}

#new answer
#{"number": "776011526026043989976902289689150134268172304397564933104371090833237162793562072615333942919554203126068287037439374028397008688451951412457616160866249153532579072478885950518176677345222991767858542940070702588301234225656672842621679473909469812297359105083728581139678185267051088230626766428262", "hash": "9ed3e8e556756ab1860a29e156ac970923d463aee2a4a18041c19f3b98754e88"}