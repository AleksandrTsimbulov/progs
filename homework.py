import requests
import bs4
from collections import Counter


class CheckingPhenomenon:
    """
    Checks the famous Wikipedia phenomenon that clicking on the first link in the main text of any Wikipedia article,
    and then repeating the process for subsequent articles, would usually lead to the "Philosophy" article.
    Expected average number of links to get to "Philosophy" is 23, see the link below:
        (https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)
    Input:
        starting_url - the url crawler starts from. If not given - random Wiki page is used
        max_page_number - the max number of links to be visited by the crawler before it stops
    Output:
        prints a statement whether the phenomenon takes place under initial conditions (str)
        prints ten mostly used words
        prints average number of words per article (str)
    Usage:
        check_phenomenon = CheckingPhenomenon([url='your_url, max_page_number=int])
        check_phenomenon.run()
    Known issues:
        After several runs with 1000 articles depths the phenomenon never appeared.
        Possible reasons:
            - Clicking on the first non-parenthesized, non-italicized link must be implemented. Current implementation
            is clicking on any first link
    Notes: Python >= 3.6 is required.
           Author: Aleksandr Tsimbulov, worktsa@yandex.ru, 2018-07-04
    """
    def __init__(self, starting_url='https://en.wikipedia.org/wiki/Special:Random', max_page_number=100):
        self._wiki_words_counter = Counter()
        self._total_number_of_words_on_wiki_pages = 0
        self._url = starting_url
        self._max_page_number = max_page_number
        self._content = None
        self._visited_pages = set()
        self._heading = None

    def _parse_and_count_words(self):
        # parse an article and count words for statistics
        resp = requests.get(self._url)
        current_url = resp.url
        self._visited_pages.add(current_url)

        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        self._heading = soup.find(id='firstHeading')
        self._content = soup.find(id='mw-content-text')

        words = self._get_words_from_page()
        self._wiki_words_counter += Counter(words)
        self._total_number_of_words_on_wiki_pages += len(words)

        self._url = self._find_and_save_next_url(current_url)

    def _find_and_save_next_url(self, current_url):
        # avoiding inf loops and bad links
        for tag in self._content.find_all(self._check_good_link):
            new_url = f"https://en.wikipedia.org{tag['href']}"
            if new_url not in self._visited_pages:
                return new_url

        print(f'Infinite loop among wiki pages have been found')
        print(f'Current url for that page in {self._url}')
        exit(code=0)

    def _get_words_from_page(self):
        # collect all of the words stripped lowercased words from the content of wiki page
        content = self._content
        list_of_words = []
        for list_or_word in [text.split() for text in content.stripped_strings]:
            prepared_word = ''  # in order to deprecate the warning
            if isinstance(list_or_word, list):
                for word in list_or_word:
                    prepared_word = self._strip_and_lowercase_the_word(word)
            elif isinstance(list_or_word, str):
                prepared_word = self._strip_and_lowercase_the_word(list_or_word)
            if prepared_word:
                list_of_words.append(prepared_word)
        return list_of_words

    @staticmethod
    def _check_good_link(tag):
        # filter external and inappropriate links
        return tag.name == 'a' and tag.has_attr('href') and tag['href'].startswith('/wiki') and ':' not in tag['href']

    @staticmethod
    def _strip_and_lowercase_the_word(word):
        # preparing words for statistics
        prepared_word = word.strip('()^%#@&!?-.,[]:;"\'\/\\')
        prepared_word = prepared_word.lower()
        return prepared_word

    def _print_statistics(self, number_of_iterations):
        # printing general statistics
        print(f'The ten of the mostly used words in Wiki during our experiment are:'
              f' {self._wiki_words_counter.most_common(10)}')
        print(f'Average number of words into Wiki articles are: '
              f'{self._total_number_of_words_on_wiki_pages // number_of_iterations}')

    def run(self):
        # main crawler loop
        for i in range(self._max_page_number):
            try:
                self._parse_and_count_words()
                print(self._heading.text)  # to see some output during runtime
                if self._heading.text == "Philosophy":
                    print(f'The Wiki phenomenon exist! Got to "Philosophy" page in {i} iterations')
                    self._print_statistics(i+1)
                    exit(code=0)
            except Exception as e:
                # needs to be more specific
                print(e)
                exit()
        print(f'During {self._max_page_number} iterations no Wiki phenomenon found. You might want to increase the '
              f'number of iterations or start with the other page')
        self._print_statistics(self._max_page_number)


if __name__ == '__main__':
    check_phenomenon = CheckingPhenomenon(max_page_number=1000)
    check_phenomenon.run()
