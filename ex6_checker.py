"""
Just run this file to test your code.
Don't forget to create main() function in moogle_old.py file.
Enjoy!
AS
"""

import sys
import moogle
import os
import io
import pickle
import traceback

URL = "https://www.cs.huji.ac.il/w~intro2cs1/ex6/wiki/"
LINKS_FILE = "test_files/links.txt"
CRAWL_FILE = "test_files/crawl.pickle"
RANKS_FILE = "test_files/ranks.pickle"
WORDS_FILE = "test_files/words.pickle"

PAGES = ["Luna_Lovegood.html",
         "Tom_Riddle.html", "Harry_Potter.html"]
EMPTY_DICTIONARY = "test_files/empty.pickle"
STANDARD_ARGUMENTS = {
    "crawl": ["crawl", URL, LINKS_FILE, CRAWL_FILE],
    "page_rank": ["page_rank", "100", CRAWL_FILE, RANKS_FILE],
    "words_dict": ["words_dict", URL, LINKS_FILE, WORDS_FILE],
    "search": lambda query, max_results="4": ["search", query, RANKS_FILE, WORDS_FILE, max_results]
}

printed_text = None

# region utils
can_use_color = False

try:
    import colorama
    colorama.init()
    can_use_color = True
except ImportError:
    class MockColorama:
        class Fore:
            RED = ""
            GREEN = ""
            BLUE = ""
            YELLOW = ""
            MAGENTA = ""
            CYAN = ""
            WHITE = ""

    colorama = MockColorama()
    pass


def c_print(text, color, end=None):
    if can_use_color:
        print(color + text + colorama.Style.RESET_ALL, end=end)
    else:
        print(text)


def read_dictionary_file(path_to_file: str) -> dict:
    with open(path_to_file, "rb") as file:
        dictionary = pickle.load(file)

    return dictionary
# endregion

# region setup


def setup():
    if not os.path.exists("test_files"):
        os.makedirs("test_files")
    if not os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "w") as file:
            to_write = PAGES
            text = "\n".join(to_write)
            file.write(text)
    if not os.path.exists(EMPTY_DICTIONARY):
        with open(EMPTY_DICTIONARY, "wb") as file:
            pickle.dump({}, file)


if not hasattr(moogle, "main"):
    c_print("Error: main function not found", colorama.Fore.RED)
    c_print("Your moogle_old.py file should contain a function called main, Like this:",
            colorama.Fore.YELLOW)

    c_print("def main():", colorama.Fore.WHITE)
    c_print("    # Your code here", colorama.Fore.CYAN)
    c_print("if __name__ == '__main__':", colorama.Fore.WHITE)
    c_print("    main()", colorama.Fore.CYAN)
    sys.exit(1)

# endregion


def run_task(command: list[str]):
    global printed_text
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    sys.argv = ["moogle"] + command
    moogle.main()
    sys.stdout = sys.__stdout__
    printed_text = capturedOutput.getvalue()


setup()


def test_crawl():
    rank_file = read_dictionary_file(CRAWL_FILE)

    assert len(rank_file) == len(PAGES)
    for page in PAGES:
        assert page in rank_file
        assert len(rank_file[page]) > 0, f"Page {page} is empty"

    assert rank_file["Luna_Lovegood.html"]["Tom_Riddle.html"] == 6, f"""Luna_Lovegood.html should have 6 links to Tom_Riddle.html, got {
        rank_file['Luna_Lovegood.html']['Tom_Riddle.html']}"""
    assert "Luna_Lovegood.html" not in rank_file["Luna_Lovegood.html"], f"""Luna_Lovegood.html should not have a link to itself, got {
        rank_file['Luna_Lovegood.html']['Luna_Lovegood.html']}"""
    assert rank_file["Luna_Lovegood.html"]["Harry_Potter.html"] == 10, f"""Luna_Lovegood.html should have 10 links to Harry_Potter.html, got {
        rank_file['Luna_Lovegood.html']['Harry_Potter.html']}"""

    assert rank_file["Tom_Riddle.html"]["Luna_Lovegood.html"] == 1, f"""Tom_Riddle.html should have 1 link to Luna_Lovegood.html, got {
        rank_file['Tom_Riddle.html']['Luna_Lovegood.html']}"""
    assert "Tom_Riddle" not in rank_file["Tom_Riddle.html"], f"""Tom_Riddle.html should not have a link to itself, got {
        rank_file['Tom_Riddle.html']['Tom_Riddle.html']}"""
    assert rank_file["Tom_Riddle.html"]["Harry_Potter.html"] == 29, f"""Tom_Riddle.html should have 29 links to Harry_Potter.html, got {
        rank_file['Tom_Riddle.html']['Harry_Potter.html']}"""


def test_page_rank_0_iterations():
    rank_dictionary = read_dictionary_file(RANKS_FILE)
    crawl_dictionary = read_dictionary_file(CRAWL_FILE)

    assert len(rank_dictionary) == len(
        crawl_dictionary), "The rank dictionary should have the same number of pages as the crawl dictionary"

    for key, value in rank_dictionary.items():
        assert value == 1, f"""Page {
            key} should have a rank of 1, when 0 iterations are run, got {value}"""


def test_page_rank_empty_dictionary():
    rank_dictionary = read_dictionary_file(RANKS_FILE)

    assert len(rank_dictionary) == 0, "The rank dictionary should be empty"


def test_page_rank():
    rank_dictionary = read_dictionary_file(RANKS_FILE)
    crawl_dictionary = read_dictionary_file(CRAWL_FILE)

    assert len(rank_dictionary) == len(
        crawl_dictionary), "The rank dictionary should have the same number of pages as the crawl dictionary"

    sum_of_ranks = sum(rank_dictionary.values())
    assert abs(sum_of_ranks - len(rank_dictionary)
               ) <= 0.00001, "The sum of all ranks should be more or less equal to the number"

    for page in PAGES:
        assert page in rank_dictionary, f"""Page {
            page} is missing from the rank dictionary"""
        assert rank_dictionary[page] > 0, f"""Page {
            page} has a rank of 0 or negative"""


def test_words_dictionary():
    words_dictionary = read_dictionary_file(WORDS_FILE)

    for word, pages in words_dictionary.items():        
        assert len(pages) > 0, f"""The word '{word}' is empty"""
        for page, count in pages.items():
            assert count > 0, f"""{word} in Page {
                page} has a count of 0 or negative"""


    assert " " not in words_dictionary, "The words dictionary should not contain an empty word: ''"

    assert words_dictionary["Hermione"]["Tom_Riddle.html"] == 12, f"""Tom_Riddle.html should have the word 'Hermione' 12 times, got {
        words_dictionary['Hermione']['Tom_Riddle.html']}"""
    assert words_dictionary["Luna"]["Luna_Lovegood.html"] == 173, f"""Luna_Lovegood.html should have the word 'Luna' 173 times, got {
        words_dictionary['Luna']['Luna_Lovegood.html']}"""
    assert words_dictionary["spell"]["Harry_Potter.html"] == 7, f"""Harry_Potter.html should have the word 'spell' 7 times, got {
        words_dictionary['spell']['Harry_Potter.html']}"""


def test_search_empty_dictionaries():
    assert printed_text == "", f"Expected no print, got {printed_text}"


def test_search(keyword):
    def search():
        expected_results = {
            "love.2": [
                ("Tom_Riddle.html", 20.618585283947613),
                ("Harry_Potter.html", 15.341589923915683)
            ],
            "love.1": [
                ("Harry_Potter.html", 15.341589923915683)
            ],
            "Hermione": [
                ("Harry_Potter.html", 248.25481876881742),
                ("Luna_Lovegood.html", 15.174490541015643),
                ("Tom_Riddle.html", 13.745723522631742),

            ]
        }

        tuples_strings = [
            f"{tup[0]} {tup[1]}\n" for tup in expected_results[keyword]
        ]
        expected_str = "".join(tuples_strings)

        assert printed_text == expected_str, f"""Expected {
            expected_str}, got: {printed_text}"""
    return search


tests = [
    (test_crawl, STANDARD_ARGUMENTS["crawl"]),
    (test_page_rank_0_iterations,
     [STANDARD_ARGUMENTS["page_rank"][0], "0", *STANDARD_ARGUMENTS["page_rank"][2:]]),
    (test_page_rank_empty_dictionary,
     [*STANDARD_ARGUMENTS["page_rank"][:2], EMPTY_DICTIONARY, STANDARD_ARGUMENTS["page_rank"][3]]),
    (test_page_rank, STANDARD_ARGUMENTS["page_rank"]),
    (test_words_dictionary, STANDARD_ARGUMENTS["words_dict"]),
    (test_search_empty_dictionaries, [
     "search", "Harry", EMPTY_DICTIONARY, EMPTY_DICTIONARY, "4"]),
    (test_search("love.2"), STANDARD_ARGUMENTS["search"]("love")),
    (test_search("Hermione"), STANDARD_ARGUMENTS["search"]("Hermione")),
    (test_search("love.1"), STANDARD_ARGUMENTS["search"]("love", "1"))
]

for (test, arguments) in tests:
    try:
        c_print(f"Running test: {test.__name__}", colorama.Fore.BLUE)
        run_task(arguments)
        test()
    except Exception as e:
        sys.stdout = sys.__stdout__
        if(type(e) == AssertionError):
            c_print(f"{test.__name__} Test Failed: {e}", colorama.Fore.RED)
        else:      
            c_print(f"""Got error in: {test.__name__} : {traceback.format_exc()}""", colorama.Fore.RED)
        c_print(f"Used arguments: {arguments}", colorama.Fore.CYAN)
        exit(1)
    c_print(f"{test.__name__} Test Passed", colorama.Fore.GREEN)


try:
    import webbrowser
    webbrowser.open('https://ibb.co/1vR3z4P')
except ImportError:
    pass

c_print("All tests passed! 🦥", colorama.Fore.GREEN)
