import json
from json import JSONDecodeError


class Parser:

    # Creates a Parser object based on the input file
    def __init__(self, file_name):
        # Open the file
        self.file_name = file_name
        file = open(file_name, "r")

        # Collect the objects from the file and read/initialize the contents
        try:
            contents = json.loads(file.read() )
            self.language = contents[0]
            self.slots = contents[1]
            self.morphemes = contents[2]
            print("Successfully loaded file ", self.file_name, " for the language: ", self.language)
            print("Loaded slots: ", self.slots, ", for a total of", self.count_morphemes(), "morphemes.\n")
        except JSONDecodeError:
            print("The file didn't exist or wasn't formatted properly, so a new one was made for you.")
            print("If this was a mistake, exit the program now. Otherwise, your file will be overwritten.\n")
            self.language = ""
            self.slots = []
            self.morphemes = {}

        file.close()

    # Count the total number of morphemes in this Parser instance
    def count_morphemes(self):
        count = 0
        for slot in self.morphemes:
            count += len(self.morphemes[slot])
        return count

    # Allow the user to add morphemes
    def add_morphemes(self):
        # Require a language name and slots if they're not present
        if not self.language:
            self.language = input("Please enter the name of the language: ")
        if not self.slots:
            # Assumes no duplicates
            slots_input = input("Please enter the comma separated slots of the PoS you're glossing (no spaces): \n")
            self.slots = slots_input.split(",")
            # If it doesn't have any slots, then that means that it doesn't have any self.morphemes structure
            for slot in self.slots:
                self.morphemes[slot] = []

        # Add morphemes
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
            if morpheme_slot not in self.slots:
                print("The slot ", morpheme_slot, " is invalid. Please choose between ", str(self.slots))
                is_valid = False

            # Sanity check: agreements to a slot, and morpheme_agreements splitting
            morpheme_agreements = []
            if not preproc_morpheme_agreements:  # If there is anything to actually parse
                for preproc_morpheme_agreement in preproc_morpheme_agreements:
                    morpheme_agreement = preproc_morpheme_agreement.split("-")
                    if len(morpheme_agreement) != 2:
                        print("Each agreement should agree with exactly one slot, separated by '-'.")
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

    # Give a command to write all the information to the json file
    def update_file(self):
        # Open the file
        with open(self.file_name, 'w') as file_descriptor:
            json.dump((self.language, self.slots, self.morphemes), file_descriptor)
        print("Successfully closed file")


def main():
    # Open the parser object
    parser = Parser("Languages/italian.txt")

    # Add to it
    parser.add_morphemes()

    # Close/update the file
    parser.update_file()


if __name__ == '__main__':
    main()
