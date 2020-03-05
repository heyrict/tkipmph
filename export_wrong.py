"""
Export tk.ipmph.com wrong questions data to json for use in exhaust.
"""

import argparse
import json

import requests
from bs4 import BeautifulSoup

from lib import bitencode_answer


def text(result_set):
    text_set = [r.text for r in result_set]
    return ''.join(text_set)


def get_type(test_papers):
    desc = test_papers.select('div.list_papers_head span.ju_pl5')
    if not desc:
        return None

    return desc[0].text[3:]


def parse_paper(paper):
    title = paper.select('span.test_paper_head')
    selection_grp = paper.select('ul')
    selections = selection_grp[0].select('li')

    answers = paper.select('span.answer_d')
    true_answer = answers[0]
    my_answer = answers[1]

    return {
        'title': text(title),
        'selections': [s.text[1:] for s in selections],
        'true_answer': true_answer.text,
        'my_answer': my_answer.text,
    }


def format_outputs(outputs):
    questions = []
    for q in outputs:
        selections = []
        for (i, s) in enumerate(q['selections']):
            selections.append({
                "text":
                s,
                "should_select":
                q['true_answer'].find(chr(i + ord('A'))) != -1,
            })
        questions.append({
            'type': 'Question',
            'question': q['title'],
            'selections': selections,
            'answer': q['true_answer'],
            'user_selection': bitencode_answer(q['my_answer']),
        })

    return json.dumps({
        'questions': questions,
    }, ensure_ascii=False)


def go_soup(soup):
    papers_list = soup.select('div.list_papers')

    outputs = []

    for papers in papers_list:
        _t = get_type(papers)
        output = parse_paper(papers)
        outputs.append(output)

    return format_outputs(outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('htmlfile', help="Input html file")
    parser.add_argument('-o',
                        '--output',
                        default=None,
                        help="Output json file")
    args = parser.parse_args()

    with open(args.htmlfile) as f:
        soup = BeautifulSoup(f.read(), 'lxml')
        results = go_soup(soup)

    if args.output:
        with open(args.output, 'w') as f:
            print(results, file=f)
    else:
        print(results)
