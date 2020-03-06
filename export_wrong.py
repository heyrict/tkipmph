"""
Export tk.ipmph.com wrong questions data to json for use in exhaust.
"""

import argparse
import json
import re

import requests
from bs4 import BeautifulSoup

from lib import bitencode_answer

SINGLE_QUOTED_RE = re.compile(r"'([^']+)'")


def text(result_set):
    text_set = [r.text for r in result_set]
    return '\n'.join(text_set)


def get_parameter(text):
    match = SINGLE_QUOTED_RE.search(text)
    if match:
        return match.groups()[0]


def get_model(test_papers):
    desc = test_papers.select('div.list_papers_head span.ju_pl5')
    if not desc:
        return None

    return desc[0].text[3:]


def parse_paper(paper):
    title = paper.select('span.test_paper_head')
    selection_grp = paper.select('ul')
    selections = selection_grp[0].select('li')
    post_buttons = paper.select('div.table_collection ul li button')
    model = get_model(paper)

    answers = paper.select('span.answer_d')
    true_answer = answers[0]
    qid = get_parameter(post_buttons[-1]['onclick'])
    my_answer = answers[1] if len(answers) > 1 else None

    return {
        'title': f"({model}) {text(title)}",
        'selections': [s.text[1:] for s in selections],
        'true_answer': true_answer.text,
        'my_answer': my_answer.text if my_answer else '',
        'qid': qid,
    }


def format_outputs(outputs):
    questions = []
    for q in outputs:
        selections = []
        for (i, s) in enumerate(q['selections']):
            selections.append({
                "text": s,
                "should_select":
                    q['true_answer'].find(chr(i + ord('A'))) != -1,
            }) # yapf: disable
        questions.append({
            'type': 'Question',
            'id': q['qid'],
            'question': q['title'],
            'selections': selections,
            'answer': q['true_answer'],
            'user_selection': bitencode_answer(q['my_answer']) if q['my_answer'] else 0,
        }) # yapf: disable

    return json.dumps({
        'questions': questions,
    }, ensure_ascii=False)


def go_soup(soup, reverse=False):
    papers_list = soup.select('div.list_papers')

    if reverse:
        papers_list = reversed(papers_list)

    outputs = []

    for papers in papers_list:
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
    parser.add_argument('-r',
                        '--reverse',
                        default=False,
                        action='store_true',
                        help="Reverse the order")
    args = parser.parse_args()

    with open(args.htmlfile) as f:
        soup = BeautifulSoup(f.read(), 'lxml')
        results = go_soup(soup, reverse=args.reverse)

    if args.output:
        with open(args.output, 'w') as f:
            print(results, file=f)
    else:
        print(results)
