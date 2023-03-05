import json
from json import JSONDecodeError


# Helper dfs method, returns true iff the morpheme
def check_morpheme_word_match(morpheme, word):
    # Check that the morpheme is at least as long as the word
    if len(morpheme["form"]) > len(word):
        return False

    # Check that the morpheme fits at the start of the word
    start_of_word = word[0: len(morpheme["form"])]
    return morpheme["form"] == start_of_word


# Helper dfs method, removes the form of the morpheme from the start of the word
def delete_word_initial_morpheme(morpheme, word):
    # Sanity check, assert that we are allowed to remove this from the start of the word
    assert word[0: len(morpheme["form"])] == morpheme["form"]

    return word[len(morpheme["form"]): ]


# Helper dfs method, (re)adds the form of the morpheme from the start of the word
def add_word_initial_morpheme(morpheme, word):
    return morpheme["form"] + word


# Returns true iff the sequence internally has correct agreements
def validate_agreements(sequence):
    # Iterate over all morphemes
    for morpheme in sequence:
        agreements = morpheme["agreements"]
        # If there are no agreements, continue
        if not agreements:
            continue
        # Otherwise, for each agreement, confirm that it's valid
        for agreement in agreements:
            agreement_property = agreement[0]
            agreement_slot = agreement[1]
            agreed_morpheme = find_morpheme_from_slot(sequence, agreement_slot)

            # Ensure that the agreed_morpheme has the properties required
            if agreement_property not in agreed_morpheme["properties"]:
                return False

    # If there are no contradictions, return true
    return True


# Returns the morpheme from the sequence of the given slot (string), or None otherwise
# Pre: there is at most one morpheme in sequence belonging to slot
def find_morpheme_from_slot(sequence, slot):
    for morpheme in sequence:
        if morpheme["slot"] == "slot":
            return morpheme
    else:
        return None


class Parser:

    # Creates a Parser object based on the input file
    def __init__(self, file_name):
        # Open the file
        self.file_name = file_name
        file = open(file_name, "r")

        # Collect the objects from the file and read/initialize the contents
        try:
            contents = json.loads(file.read())
            self.language = contents[0]
            self.slots = contents[1]
            self.morphemes = contents[2]
            print("Successfully loaded file ", self.file_name, " for the language: ", self.language)
            print(len(self.slots), "slots: ", str(self.slots))
            print(self.count_morphemes(), "morphemes: \n", str(self.morphemes))  # Temporary
        except JSONDecodeError:
            print("The file didn't exist or wasn't formatted properly, so a new one was made for you.")
            print("If this was a mistake, exit the program now. Otherwise, your file will be overwritten.\n")
            self.language = ""
            self.slots = []
            self.morphemes = {}

        print()
        file.close()
        self.changes_made = False

    # Count the total number of morphemes in this Parser instance
    def count_morphemes(self):
        count = 0
        for slot in self.morphemes:
            count += len(self.morphemes[slot])
        return count

    # Allow the user to add morphemes
    def add_morphemes(self):
        self.changes_made = True

        # Require a language name and slots if they're not present
        if not self.language:
            print("NAME")
            self.language = input("Please enter the name of the language:\n")
            print()
        if not self.slots:
            # Assumes no duplicates
            print("SLOTS")
            print("Please enter the comma separated slots of the PoS you're glossing (no spaces).")
            slots_input = input("Any required slot should be followed by '!'.\n")
            print()

            # If it doesn't have any slots, then that means that it doesn't have any self.morphemes structure
            for slot in slots_input.split(","):
                self.slots.append({
                    "slot": slot.strip("!"),
                    "is_required": slot[-1] == '!'
                })
                self.morphemes[slot] = []

        # Add morphemes
        print("MORPHEMES")
        print("You'll now add morphemes until you tell the program to stop.")
        print("Each allomorph and morpheme belonging to a different class should be entered separately.")
        print("Don't include spaces in your answer. Only include ',', '/', and '-' as directed.")
        print("Please enter a morpheme as follows (no spaces): form,slot,property1/property2/...,"
              "agreement1-slot1/agreement2-slot2/...,gloss \n")
        while True:
            morpheme_input = input("Enter your morpheme (or enter to quit): ").strip(" ")

            # Quit if necessary
            if not morpheme_input:
                break

            morpheme_characteristics = morpheme_input.split(",")
            is_valid = True

            # Sanity check: 5 properties
            if len(morpheme_characteristics) != 5:
                print("Separate entries for form, slot, properties, agreement, and gloss by commas, even if null.")
                is_valid = False

            morpheme_form = morpheme_characteristics[0]
            morpheme_slot = morpheme_characteristics[1]
            morpheme_properties = morpheme_characteristics[2].split("/")
            preproc_morpheme_agreements = morpheme_characteristics[3].split("/")
            morpheme_gloss = morpheme_characteristics[4]

            # Sanity check: valid slot
            if morpheme_slot not in self.get_slot_list():
                print("The slot ", morpheme_slot, " is invalid. Please choose between ", str(self.get_slot_list()))
                is_valid = False

            # Sanity check: agreements to a slot, doesn't agree with itself, and morpheme_agreements splitting
            morpheme_agreements = []
            if preproc_morpheme_agreements:  # If there is anything to actually parse
                for preproc_morpheme_agreement in preproc_morpheme_agreements:
                    morpheme_agreement = preproc_morpheme_agreement.split("-")
                    # One agreement to one slot
                    if len(morpheme_agreement) != 2:
                        print("Each agreement should agree with exactly one slot, separated by '-'.")
                        is_valid = False
                    # Doesn't agree with itself
                    if morpheme_agreement[1] == morpheme_slot:
                        print("You can't specify a morpheme to agree with itself. You might be thinking of a property.")
                        is_valid = False
                    morpheme_agreements.append(morpheme_agreement)

            # If failed validity checks, continue
            if not is_valid:
                continue

            # Confirm
            morpheme = {
                "form": morpheme_form,
                "slot": morpheme_slot,
                "properties": morpheme_properties,
                "agreements": morpheme_agreements,
                "gloss": morpheme_gloss
            }
            print("You just added ", str(morpheme))

            self.morphemes[morpheme_slot].append(morpheme)

    # Returns a list with all the slot names
    def get_slot_list(self):
        slot_list = []
        for slot in self.slots:
            slot_list.append(slot["slot"])
        return slot_list

    # Give a command to write all the information to the json file
    def update_file(self):
        # Only update the file if changes were made
        if self.changes_made:
            # Open the file
            with open(self.file_name, 'w') as file_descriptor:
                json.dump((self.language, self.slots, self.morphemes), file_descriptor)
            print("Successfully closed file")

    # Given a word, returns a set containing morpheme sequences stored in a list
    # The morpheme sequences may not be grammatically valid, but would match the regex of the morphemes
    def find_sequences(self, input_word):
        current_sequence = []
        valid_sequences = []
        self.helper_find_sequences(input_word, current_sequence, valid_sequences, 0)
        return valid_sequences

    # Helper method to find_sequences for dfs
    def helper_find_sequences(self, input_word, current_sequence, valid_combinations, slot_index):
        # If we finished parsing the word, and we're at the final slot, we can add the word to combinations
        if slot_index == len(self.slots):
            if not input_word:
                valid_combinations.append(list(current_sequence) )
        else:  # Otherwise, we search through all the morphemes at the given slot_index, and dfs them
            current_slot = self.slots[slot_index]["slot"]
            for morpheme in self.morphemes[current_slot]:  # For all morphemes in the current slot
                if morpheme["slot"] == self.slots[slot_index]["slot"]:  # If the slot agrees with the slot
                    if check_morpheme_word_match(morpheme, input_word):  # If the morpheme fits
                        # Process the morpheme and input_word, and adjust slot_index accordingly
                        current_sequence.append(morpheme)
                        input_word = delete_word_initial_morpheme(morpheme, input_word)
                        slot_index += 1

                        # dfs
                        self.helper_find_sequences(input_word, current_sequence, valid_combinations, slot_index)

                        # Deprocess all the changed variables
                        current_sequence.pop()
                        input_word = add_word_initial_morpheme(morpheme, input_word)
                        slot_index -= 1

    # Returns true or false depending on whether a sequence is valid
    def is_valid(self, sequence):
        # Validate that all required slots are filled
        # Validating each slot is filled at most once is not necessary thanks to the dfs slot_index += 1 each iteration
        if not self.validate_slots_filled(sequence):
            return False

        # Validate that all agreements are satisfied
        if not validate_agreements(sequence):
            return False

        return True

    # Returns true iff all the required slots are filled
    def validate_slots_filled(self, sequence):
        # Find all the required slots
        required_slots = set()
        for slot in self.slots:
            if slot["is_required"]:
                required_slots.add(slot["slot"])

        # Confirm they're all filled
        for morpheme in sequence:
            required_slots.discard(morpheme["slot"])

        return len(required_slots) == 0


def main():
    # Open the parser object
    parser = Parser("Languages/italian.txt")

    # Add to it
    # parser.add_morphemes()

    # Find the sequences
    sequences = parser.find_sequences("amano")
    print("Your sequences are ", sequences)

    # Close/update the file
    parser.update_file()


if __name__ == '__main__':
    main()
