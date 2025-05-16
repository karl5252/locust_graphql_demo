def load_query(filename: str) -> str:
    """
    Load a GraphQL query from a file.
    :param filename:
    :return:
    """
    with open(f"queries/{filename}", "r", encoding="utf-8") as file:
        return file.read()
