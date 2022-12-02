#!/usr/bin/env python

"""
PracType main
"""

import csv
from enum import Enum
import random
from typing import Tuple, List, Dict

import getch

TAG_RED = '\033[91m'
TAG_NORM = '\033[0m'

LINE_BLANK = " ".join(" " for _ in range(50 - 1))

# Parameters
LINE_NB = 3
WORD_PER_LINE_NB = 10
WORD_LEN_MIN = 1
WORD_LEN_MAX = 9
# CHAR_LIST = "eiransolutymdchgpbkfvwxqzj"
CHAR_LIST = "eirn"

class Ret(Enum):
    """
    Return code
    """
    OK = 0
    STOP = 1

class CharStat():
    """
    Character statistics
    """

    def __init__(self, char: str):

        self.char = char
        self.src_nb = 0
        self.err_nb = 0

class StatDict():
    """
    Dict of character statistics
    """

    def __init__(self, file_name: str = None):

        self.file_name = file_name
        self._dict = {}

    def load(self) -> None:
        """
        Load from file
        """

        if self.file_name is None:
            return

        self._dict.clear()

        with open(self.file_name, "r", newline='', encoding="utf8") as file:

            reader = csv.DictReader(file, delimiter=',', quotechar='"')

            for row in reader:

                char_stat = CharStat(row["char"])
                char_stat.src_nb = int(row["src_nb"])
                char_stat.err_nb = int(row["err_nb"])

                self._dict[ord(char_stat.char)] = char_stat

    def save(self) -> None:
        """
        Save to file
        """

        if self.file_name is None:
            return

        with open(self.file_name, "w", newline='', encoding="utf8") as file:

            field_name_list = ["char", "src_nb", "err_nb"]

            writer = csv.DictWriter(file, fieldnames=field_name_list)

            writer.writeheader()

            for (_, val) in self._dict.items():

                writer.writerow({"char": val.char, "src_nb": val.src_nb, "err_nb": val.err_nb})

    def print(self) -> None:
        """
        Print char stat dict
        """

        print("char | src nb | err nb | accuracy")
        for (_, value) in self._dict.items():
            print("%c    | %06d | %06d | %02.02f" % (
                value.char, value.src_nb, value.err_nb,
                (value.src_nb - value.err_nb) / value.src_nb))

    def get_items(self) -> List:
        """
        Return list of dict entries (key, value)

        Returns:
            List: Dict items
        """
        return self._dict.items()

    def merge_child(self, dict_child) -> None:
        """
        Merge child to self char stat dict

        Args:
            dict_child (Dict[CharStat]): Child char stat dict
        """

        # For each child char stat entry
        for (key, val) in dict_child.get_items():

            # Get self char stat entry
            char_stat = self._dict.get(key)

            if char_stat is not None:
                # Char stat already in self dict
                # Update entry
                char_stat.src_nb += val.src_nb
                char_stat.err_nb += val.err_nb

            else:
                # Char stat not in self dict
                # Create new entry
                self._dict[key] = val

    def add_src(self, char: str) -> None:
        """
        Add source

        Args:
            char (str): Character
        """

        if char == " ":
            return

        char_stat = self._dict.get(ord(char))

        if char_stat is None:
            self._dict[ord(char)] = CharStat(char)

        self._dict[ord(char)].src_nb += 1

    def add_err(self, char: str) -> None:
        """
        Add input error

        Args:
            char (str): Character misstyped
        """

        if char == " ":
            return

        char_stat = self._dict.get(ord(char))
        if char_stat is not None:
            char_stat.err_nb += 1

def print_line_in(line_in: str, line_src: str) -> None:
    """
    Print input line

    Args:
        line_in (str): Input line being typed
        line_src (str): Source line to type
    """

    print("\r", end="")

    for (char_idx, char_in) in enumerate(line_in):

        if char_idx >= len(line_src):
            break

        if char_in == line_src[char_idx]:
            print(char_in, end="")
        else:
            print(TAG_RED + char_in + TAG_NORM, end="")

    print("", end="", flush=True)

def process_line(line_src: str) -> (Ret, Dict):
    """
    Process line typing

    Args:
        line_src (str): Line of text to type

    Returns:
        Ret: Return code
        Dict: Character statistics dict
    """

    ret = Ret.OK
    char_idx = 0
    line_in = ""
    stat_dict = StatDict()

    print(line_src)

    while True:

        char_in = getch.getch()
        # print(ord(char_in))
        # return

        # Escape
        if ord(char_in) == 27:
            ret = Ret.STOP
            break

        # Return
        elif ord(char_in) == 10:
            break

        # Backspace
        elif ord(char_in) == 8:
            line_in = line_in[:-1]
            char_idx -= 1
            print(f"\r{LINE_BLANK}", end="")

        else:

            # Stop at end of line
            if len(line_in) < len(line_src):

                stat_dict.add_src(line_src[char_idx])

                if char_in != line_src[char_idx]:
                    # Character input error
                    stat_dict.add_err(line_src[char_idx])

                line_in += char_in
                char_idx += 1

        print_line_in(line_in, line_src)

    print()

    stat_dict.print()

    return (ret, stat_dict)

def process_text(text: str) -> Dict:
    """
    Process text typing

    Args:
        text (str): Text to type

    Returns:
        Dict: Character statistics dict
    """

    stat_dict = StatDict()
    stat_dict_line = StatDict()

    for line in text.split('\n'):

        (ret, stat_dict_line) = process_line(line)

        stat_dict.merge_child(stat_dict_line)

        stat_dict.print()

        if ret == Ret.STOP:
            break

    return stat_dict

def gen_word(char_list: List[str], len_min: int, len_max: int) -> str:
    """
    Generate word from lsit of characters

    Args:
        char_list (List[str]): List of characters to use
        len_min (int): Min word length
        len_max (int): Max word length

    Returns:
        string: Generated word
    """

    length = random.randrange(len_min, len_max)

    word = char_list[random.randrange(len(char_list))]
    for _ in range(length - 1):

        char = char_list[random.randrange(len(char_list))]

        # Reduce double rep char occurence
        if len(word) >= 1 and char == word[len(word) - 1]:
            char = char_list[random.randrange(len(char_list))]

        # Avoid triple repeated char
        if len(word) >= 2 and word[len(word) - 1] == word[len(word) - 2]:
            while char == word[len(word) - 1]:
                char = char_list[random.randrange(len(char_list))]

        word += char

    return word

def gen_line_from_char_list(char_list: List[str], word_nb: int) -> str:
    """
    Generate line from list of characters

    Args:
        char_list (List[str]): List of characters to use
        word_nb (int): Number of words

    Returns:
        str: Generated line
    """

    line = gen_word(char_list, WORD_LEN_MIN, WORD_LEN_MAX)
    for _ in range(word_nb - 1):
        line += " " + gen_word(char_list, WORD_LEN_MIN, WORD_LEN_MAX)

    return line

def gen_text_from_char_list(char_list: List[str], line_nb: int, word_per_line_nb: int) -> str:
    """
    Generate text from list of characters

    Args:
        char_list (List[str]): List of characters to use
        line_nb (int): Number of lines
        word_per_line_nb (int): Number of words per line

    Returns:
        str: Generated text
    """

    text = gen_line_from_char_list(char_list, word_per_line_nb)
    for _ in range(line_nb - 1):
        text += "\n" + gen_line_from_char_list(char_list, word_per_line_nb)

    return text

def gen_line_from_word_list(word_list: List[str], word_nb) -> str:
    """
    Generate line from list of words

    Args:
        word_list (List[str]): List of words to use
        word_nb (_type_): Number of words

    Returns:
        str: Generated line
    """

    line = word_list[random.randrange(len(word_list))]
    for _ in range(word_nb - 1):
        line += " " + word_list[random.randrange(len(word_list))]

    return line

def gen_text_from_word_list(word_list: List[str], line_nb: int, word_per_line_nb: int) -> str:
    """
    Generated text from list of words

    Args:
        word_list (List[str]): List of words to use
        line_nb (int): Number of lines
        word_per_line_nb (int): Number of words per line

    Returns:
        str: Generated text
    """

    text = gen_line_from_word_list(word_list, word_per_line_nb)
    for _ in range(line_nb - 1):
        text += "\n" + gen_line_from_word_list(word_list, word_per_line_nb)

    return text

def load_word_list() -> List[str]:
    """
    Load list of words from file

    Returns:
        List[str]: Loaded list of words
    """

    with open("dict.txt", "r", encoding="utf8") as file:

        data = file.read()

        word_list = []
        for word in data.split('\n'):
            word_list += [word]

    return word_list

def main():
    """
    Main
    """

    word_list = []

    print("1 : word_list")
    print("2 : characters")
    mode = int(input())

    if mode == 1:
        word_list = load_word_list()
        text = gen_text_from_word_list(word_list, LINE_NB, WORD_PER_LINE_NB)
    elif mode == 2:
        text = gen_text_from_char_list(CHAR_LIST, LINE_NB, WORD_PER_LINE_NB)
    else:
        print(f"ERROR Unhandled mode={mode}")
        return

    stat_dict = StatDict("stats.csv")
    stat_dict.load()
    stat_dict.print()

    stat_dict_text = process_text(text)

    stat_dict.merge_child(stat_dict_text)
    stat_dict.print()
    stat_dict.save()

if __name__ == "__main__":
    main()
