def format_file(file_name):
    # Read the file
    with open(file_name) as f:
        contents = f.read()

    # Write to file with the changes we made
    with open(file_name, 'w') as f:
        f.write(format_text(contents) )


def format_text(text):
    text = text.replace('\\"', '"')
    text = text.replace('"[', '[').replace(']"', ']')
    text = text.replace('""""', '""')
    return text


if __name__ == '__main__':
    format_file("Languages/swahili_verbs_STROVE_basics.txt")
