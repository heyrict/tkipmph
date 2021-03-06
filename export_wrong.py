"""
Export tk.ipmph.com wrong questions data to json for use in exhaust.
"""

import argparse
import json
import os
import re
from urllib.request import urlopen, urlsplit

from bs4 import BeautifulSoup
from tqdm.cli import tqdm

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


def maybe_download(url, output_file):
    # Skips downloading the file if it exists
    if os.path.exists(output_file):
        return

    with urlopen(url) as res, open(output_file, "wb") as f:
        f.write(res.read())


def parse_paper(paper):
    title = paper.select('span.test_paper_head')
    img = paper.select('span.test_paper_head img')
    selection_grp = paper.select('ul')
    selections = selection_grp[0].select('li')
    post_buttons = paper.select('div.table_collection ul li button')
    model = get_model(paper)

    answers = paper.select('span.answer_d')
    true_answer = answers[0]
    qid = get_parameter(post_buttons[-1]['onclick'])
    my_answer = answers[1] if len(answers) > 1 else None

    return {
        'model': model,
        'title': text(title),
        'selections': [s.text[1:] for s in selections],
        'true_answer': true_answer.text,
        'my_answer': my_answer.text if my_answer else '',
        'assets': [f"http://tk.ipmph.com{i['src']}" for i in img],
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
            'model': q['model'],
            'question': f"({q['model']}) {q['title']}",
            'selections': selections,
            'answer': q['true_answer'],
            'assets': q['assets'],
            'user_selection': bitencode_answer(q['my_answer']) if q['my_answer'] else 0,
        }) # yapf: disable

    return json.dumps({
        'questions': questions,
    }, ensure_ascii=False)


def go_soup(soup, order_by: None, reverse=False, assets_folder=None):
    papers_list = soup.select('div.list_papers')
    outputs = []

    for papers in papers_list:
        output = parse_paper(papers)
        outputs.append(output)

    if order_by is not None:
        outputs.sort(key=lambda p: p[order_by], reverse=reverse)
    elif reverse:
        outputs = reversed(outputs)

    if assets_folder is not None:
        assets = []

        def _map_asset(img):
            img_name = os.path.basename(urlsplit(img).path)
            img_path = os.path.join(assets_folder, img_name)
            assets.append((img, img_path))
            return img_path

        def _map_paper(o):
            o['assets'] = list(map(_map_asset, o['assets']))
            return o

        if not os.path.exists(assets_folder):
            os.mkdir(assets_folder)

        outputs = list(map(_map_paper, outputs))

        for (url, path) in tqdm(assets,
                                f"Downloading assets to {assets_folder}"):
            maybe_download(url, path)

    return format_outputs(outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('htmlfile', help="Input html file")
    parser.add_argument('-o',
                        '--output',
                        default=None,
                        help="Output json file")
    parser.add_argument('-d',
                        '--assets-dir',
                        default=None,
                        help="Directory to store assets")
    parser.add_argument('-O',
                        '--order-by',
                        default=None,
                        choices=['id', 'model', 'question'],
                        help="Order by field")
    parser.add_argument('-r',
                        '--reverse',
                        default=False,
                        action='store_true',
                        help="Reverse the order")
    args = parser.parse_args()

    with open(args.htmlfile) as f:
        soup = BeautifulSoup(f.read(), 'lxml')
        results = go_soup(soup,
                          order_by=args.order_by,
                          reverse=args.reverse,
                          assets_folder=args.assets_dir)

    if args.output:
        with open(args.output, 'w') as f:
            print(results, file=f)
    else:
        print(results)
