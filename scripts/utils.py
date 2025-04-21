import re

def remove_structure_tags(text):
    """
    Removes all structured tags like [heading], [/heading], [paragraph], etc. from the input text.

    Args:
        text (str): Input string with structure tags.

    Returns:
        str: Cleaned string without tags.
    """
    return re.sub(r'\[/?\w+\]', '', text).strip()