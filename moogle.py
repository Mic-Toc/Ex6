from typing import Dict
import bs4
import requests as requests
import urllib.parse
import sys
import pickle
import copy


USER_AGENT = "curl"


def find_relative_urls(index_file):

    relative_url_list = []

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            line_without_newline = line.replace("\n", "")
            relative_url_list.append(line_without_newline)

    return relative_url_list


def find_full_URLs(relative_urls_list, base_url):

    full_url_list = []

    for i in range(len(relative_urls_list)):

        full_url = urllib.parse.urljoin(base_url, relative_urls_list[i])

        full_url_list.append(full_url)

    return full_url_list


def find_html_of_url(full_url):

    header = {'User-Agent': USER_AGENT}

    response = requests.get(full_url, headers=header)

    html_code = response.text

    return html_code


def amount_of_links(relative_url, html_code):

    count_links = 0

    soup = bs4.BeautifulSoup(html_code, 'html.parser')
    for p in soup.find_all("p"):
        for link in p.find_all("a"):
            target = link.get("href")

            if target == relative_url:
                count_links += 1

    return count_links


def create_traffic_dict(base_url, index_file):

    traffic_dict: Dict[str, Dict[str, int]] = dict()

    relative_urls = find_relative_urls(index_file)

    full_urls = find_full_URLs(relative_urls, base_url)

    for i in range(len(relative_urls)):

        html_of_url = find_html_of_url(full_urls[i])

        amount_of_links_dict: Dict[str, int] = dict()

        for j in range(len(relative_urls)):

            number_of_links = amount_of_links(relative_urls[j], html_of_url)

            amount_of_links_dict[f"{relative_urls[j]}"] = number_of_links

        traffic_dict[f"{relative_urls[i]}"] = amount_of_links_dict

    for out_page in list(traffic_dict.keys()):
        for inner_page in list(traffic_dict[out_page].keys()):

            if traffic_dict[out_page][inner_page] == 0:
                traffic_dict[out_page].pop(inner_page)

    return traffic_dict


def save_traffic_dict(traffic_dict, out_file):

    with open(out_file, 'wb') as f:
        pickle.dump(traffic_dict, f)


def crawl(base_url, index_file, out_file):

    traffic_dict = create_traffic_dict(base_url, index_file)
    for out_page in traffic_dict.keys():
        print(out_page + ": \n")
        for inner_page in traffic_dict[out_page].keys():
            print(inner_page + ":" + str(traffic_dict[out_page][inner_page]), end=" ")

        print("\n", traffic_dict)

    save_traffic_dict(traffic_dict, out_file)


def total_num_links(links_dict_file: Dict[str, Dict[str, int]],
                    page_name: str):

    total_links = 0

    page_dict = links_dict_file[page_name]

    for num_links in page_dict.values():
        total_links += num_links

    return total_links


def calculate_page_ranking(page_name: str,
                           links_dict: Dict[str, Dict[str, int]],
                           old_rating_dict: Dict[str, float]):

    ranking = 0

    for from_page, dictionary in links_dict.items():

        total_links = total_num_links(links_dict, from_page)

        for to_page, links in dictionary.items():

            if to_page == page_name and from_page != page_name:
                ranking += old_rating_dict[from_page] * (links / total_links)

    return ranking


def create_ranking_dict(iterations: int,
                        links_dict: Dict[str, Dict[str, int]]):

    r: Dict[str, float] = dict()

    for page_name in links_dict.keys():
        r[f"{page_name}"] = 1

    for i in range(iterations):

        new_r = dict()

        for p in r.keys():
            new_r[p] = 0

        for page in r.keys():

            curr_page_rating = calculate_page_ranking(page,
                                                      links_dict,
                                                      r)

            new_r[page] = curr_page_rating

        r = new_r

    return r


def save_ranking_dict(ratings_dict, out_file):

    with open(out_file, 'wb') as f:
        pickle.dump(ratings_dict, f)


def page_rank(iterations, links_dict_file, out_file):

    with open(links_dict_file, "rb") as f:
        links_dict = pickle.load(f)

    r = create_ranking_dict(iterations, links_dict)

    print(r)

    save_ranking_dict(r, out_file)


def split_text_to_words(text: str):

    no_new_line_list = text.split("\n")
    no_new_line_str = ""

    for elem in no_new_line_list:
        no_new_line_str += elem

    no_tabs_list = no_new_line_str.split("\t")
    no_tabs_str = ""

    for part in no_tabs_list:
        no_tabs_str += part

    no_spaces_list = no_tabs_str.split(" ")

    return no_spaces_list


def update_num_of_words_in_page(page_name: str,
                                html_code,
                                word_dict: Dict[str, Dict[str, int]]):

    soup = bs4.BeautifulSoup(html_code, "html.parser")

    for p in soup.find_all('p'):

        content = p.text

        words_list = split_text_to_words(content)

        for word in words_list:

            if word in word_dict.keys():

                if page_name in word_dict[word].keys():

                    word_dict[word][page_name] += 1

                else:

                    word_dict[word][page_name] = 1

            else:

                amount_of_words_dict: Dict[str, int] = dict()
                amount_of_words_dict[page_name] = 1

                word_dict[word] = amount_of_words_dict

    return word_dict


def create_words_dict(base_url, index_file):

    word_dict: Dict[str, Dict[str, int]] = dict()

    relative_urls = find_relative_urls(index_file)

    full_urls = find_full_URLs(relative_urls, base_url)

    for i in range(len(relative_urls)):

        html_of_url = find_html_of_url(full_urls[i])

        updated_word_dict = update_num_of_words_in_page(relative_urls[i],
                                                        html_of_url,
                                                        word_dict)

        word_dict = updated_word_dict

    if "" in word_dict.keys():
        word_dict.pop("")

    return word_dict


def save_words_dict(word_dict, out_file):

    with open(out_file, 'wb') as f:
        pickle.dump(word_dict, f)


def words_dict(base_url, index_file, out_file):

    words_dictionary = create_words_dict(base_url, index_file)

    save_words_dict(words_dictionary, out_file)


def find_query_pages(words_query,
                     find_words_dict: Dict[str, Dict[str, int]],
                     total_pages):

    pages_with_query = []
    # for dictionary in find_words_dict.values():
    #     for page in dictionary.keys():
    #
    #         for word in words_query:
    #             if word not in find_words_dict.keys():
    #                 return None
    #
    #             elif page not in find_words_dict[word].keys():
    #                 is_append = False
    #                 break
    #
    #         if is_append:
    #             pages_with_query.append(page)
    for page in total_pages:
        is_append = True

        for word in words_query:
            if word not in find_words_dict.keys():
                return None

            elif page not in find_words_dict[word].keys():

                is_append = False
                break

        if is_append:
            pages_with_query.append(page)

    return pages_with_query


def list_to_dict(pages_with_query_list,
                 ranking_dict: Dict[str, float]):

    pages_with_query_dict: Dict[str, float] = dict()

    for page_name in pages_with_query_list:

        pages_with_query_dict[page_name] = ranking_dict[page_name]

    return pages_with_query_dict


def rate_pages_with_query(pages_with_query_dict: Dict[str, float],
                          max_results):

    max_results = int(max_results)

    copy_query_dict = copy.deepcopy(pages_with_query_dict)

    ordered_ranking_dict: Dict[str, float] = dict()

    while copy_query_dict != {}:
        for page in list(copy_query_dict.keys()):

            highest_rank = max(copy_query_dict.values())

            if copy_query_dict[page] == highest_rank:

                ordered_ranking_dict[page] = copy_query_dict[page]

                copy_query_dict.pop(page)

    max_res_ordered_dict = dict()

    count = 0

    for page_name in ordered_ranking_dict:
        if count >= max_results:
            break

        max_res_ordered_dict[page_name] = ordered_ranking_dict[page_name]
        count += 1

    return max_res_ordered_dict


def min_occur_query(query: str,
                    find_words_dict: Dict[str, Dict[str, int]],
                    page_name: str):

    words_list = split_text_to_words(query)

    min_occurrence_value = 0
    min_occurrence_word = words_list[0]

    for first in words_list:
        min_occurrence_value = find_words_dict[first][page_name]
        break

    for word in words_list:

        if find_words_dict[word][page_name] < min_occurrence_value:

            min_occurrence_value = find_words_dict[word][page_name]
            min_occurrence_word = word

    return min_occurrence_word


def total_rate(ordered_ranking_dict: Dict[str, float],
               find_words_dict: Dict[str, Dict[str, int]],
               query: str):

    total_rate_dict: Dict[str, float] = dict()

    for page in ordered_ranking_dict.keys():

        min_word = ""
        if query != "":
            min_word = min_occur_query(query, find_words_dict, page)

            total_rate_dict[page] = (ordered_ranking_dict[page] *
                                     find_words_dict[min_word][page])

        else:
            total_rate_dict[page] = ordered_ranking_dict[page]

    return total_rate_dict


def order_total_rate(total_rate_dict: Dict[str, float]):

    copy_rating_dict = copy.deepcopy(total_rate_dict)

    ordered_rate_dict: Dict[str, float] = dict()

    while copy_rating_dict != {}:
        for page_name in list(copy_rating_dict.keys()):

            highest_rank = max(copy_rating_dict.values())

            if copy_rating_dict[page_name] == highest_rank:

                ordered_rate_dict[page_name] = highest_rank

                copy_rating_dict.pop(page_name)

    return ordered_rate_dict


def search(ranking_dict_file, words_dict_file, max_results, query=""):

    with open(ranking_dict_file, "rb") as f:
        ranking_dict = pickle.load(f)

    with open(words_dict_file, "rb") as file:
        find_words_dict = pickle.load(file)

    words_query = split_text_to_words(query)

    total_pages = ranking_dict.keys()

    pages_with_query = find_query_pages(words_query,
                                        find_words_dict,
                                        total_pages)

    if pages_with_query is not None:
        query_dict = list_to_dict(pages_with_query, ranking_dict)

        ordered_ranking_dict = rate_pages_with_query(query_dict, max_results)

        total_rating_dict = total_rate(ordered_ranking_dict,
                                       find_words_dict,
                                       query)

        ordered_total_rate_dict = order_total_rate(total_rating_dict)

        for elem in ordered_total_rate_dict.keys():
            print(elem, ordered_total_rate_dict[elem])


def main():

    args = sys.argv

    if args[1] == "crawl":
        BASE_URL = args[2]
        INDEX_FILE = args[3]
        OUT_FILE = args[4]

        crawl(BASE_URL, INDEX_FILE, OUT_FILE)

    elif args[1] == "page_rank":
        ITERATIONS = args[2]
        ITERATIONS = int(ITERATIONS)
        DICT_FILE = args[3]
        OUT_FILE = args[4]

        page_rank(ITERATIONS, DICT_FILE, OUT_FILE)

    elif args[1] == "words_dict":
        BASE_URL = args[2]
        INDEX_FILE = args[3]
        OUT_FILE = args[4]

        words_dict(BASE_URL, INDEX_FILE, OUT_FILE)

    elif args[1] == "search":

        if len(args) == 5:
            QUERY = ""
            RANKING_DICT_FILE = args[2]
            WORDS_DICT_FILE = args[3]
            MAX_RESULTS = args[4]

        else:
            QUERY = args[2]
            for i in range(3, len(args) - 3):
                QUERY += " " + args[i]
            RANKING_DICT_FILE = args[len(args) - 3]
            WORDS_DICT_FILE = args[len(args) - 2]
            MAX_RESULTS = args[len(args) - 1]

        search(RANKING_DICT_FILE, WORDS_DICT_FILE, MAX_RESULTS, QUERY)


if __name__ == "__main__":
    main()

