def save_to_output(text: str):
    with open("local/output.txt", "w") as file:
        file.write(text)
