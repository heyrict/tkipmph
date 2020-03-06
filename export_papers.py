"""
Export tk.ipmph.com test data to json for use in exhaust.

Needs authorization, which should be dumped from `Network` tab and `window.cookie`.

# Shape of config.yaml
```yaml
Cookie: (Paste window.cookie here)
JSESSIONID: (Dump from Request in Network tab)
JEESITE_SESSION_ID: (Dump from Request in Network tab)
Authorization: (Dump from XHR Request in Network tab)
USERID: (See url parameter id=...)
```
"""

import argparse
import json
import re
import time
from random import random

import requests
from bs4 import BeautifulSoup
from tqdm.cli import tqdm

from lib import get_config

ANSWERTHIS_EP = "http://tk.ipmph.com/exam/a/exam/examTask/answerThis"

DEFAULT_UA = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0'


def find_value(key, text):
    match = re.search(f"{key}=([a-z0-9]+)", text)
    if match:
        return match.groups()[0]


def get_headers(referer, config):
    return {
        'Authorization': config['Authorization'],
        'Host': 'tk.ipmph.com',
        'Origin': 'tk.ipmph.com',
        'Referer': referer,
        'User-Agent': DEFAULT_UA,
        'X-Requested-With': 'XMLHttpRequest'
    }


def get_cookies(config):
    cookies_str = config.get('Cookie')
    cookies = {
        'JSESSIONID': config.get('JSESSIONID'),
        'jeesite.session.id': config.get('JEESITE_SESSION_ID'),
    }
    for cookie_str in cookies_str.split(';'):
        [key, value] = cookie_str.split('=')
        cookies[key] = value
    return cookies


def get_testpaper(question_id, esid, paper_id, exam_id, config, cookies):
    headers = get_headers('http://tk.ipmph.com/exam/a/exam/examTask/toAnswer',
                          config)
    res = requests.post(ANSWERTHIS_EP,
                        data={
                            'examStudent.id': esid,
                            'question.id': question_id,
                            'paper.id': paper_id,
                            'exam.id': exam_id,
                        },
                        headers=headers,
                        cookies=cookies)
    return res.json()


def parse_testpage(pagesrc):  # {{{
    esid = find_value('examStudentId', pagesrc)
    paper_id = find_value('paper.id', pagesrc)
    exam_id = find_value('examId', pagesrc)

    soup = BeautifulSoup(pagesrc, 'lxml')
    question_list = [node['name'] for node in soup.select('button.cell')]
    return {
        'questions': question_list,
        'esid': esid,
        'paper_id': paper_id,
        'exam_id': exam_id,
    }  # }}}


def get_testpage(page_url, config, cookies):  # {{{
    headers = get_headers(
        'http://tk.ipmph.com/exam/a/exam/examTask/myExamTaskList', config)
    res = requests.get(page_url, headers=headers, cookies=cookies)
    pagesrc = res.text
    return parse_testpage(pagesrc)  # }}}


def format_choices(choices):
    sorted_choices = sorted(choices, key=lambda c: c['answer'])
    return [{
        'text': c['choiceName'],
        'should_select': False
    } for c in sorted_choices]


def parse_testpaper(testpaper):
    questions = []
    model = testpaper['model']
    extra_title = testpaper.get('parentQuestion')
    choice_override = testpaper.get('parentChoiceList')

    get_title = lambda q: f"{extra_title}\n{q['name']}" if extra_title else q[
        'name']
    get_selections = lambda q: format_choices(
        choice_override) if choice_override else format_choices(q['choiceList']
                                                                )

    for q in testpaper['questionList']:
        questions.append({
            'type': 'Question',
            'id': q['id'],
            'question': f"({model}) {get_title(q)}",
            'selections': get_selections(q),
        })

    return questions


def pipe_testpaper(testpaper):
    questions = parse_testpaper(testpaper)
    return questions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help="Exam page url")
    parser.add_argument('-c',
                        '--config',
                        default='./config.yaml',
                        help="Config yaml file")
    parser.add_argument('-o',
                        '--output',
                        default=None,
                        help="Output json file")
    args = parser.parse_args()

    config = get_config(args.config)
    cookies = get_cookies(config)

    tpdata = get_testpage(args.url, config, cookies)

    tp_viewed = []
    all_questions = []
    for tpid in tqdm(tpdata['questions']):
        if tpid in tp_viewed: continue

        testpaper = get_testpaper(tpid, tpdata['esid'], tpdata['paper_id'],
                                  tpdata['exam_id'], config, cookies)

        questions = pipe_testpaper(testpaper)
        all_questions.extend(questions)
        tp_viewed.extend([q['id'] for q in questions])
        time.sleep(random() / 3)

    results = json.dumps({
        'questions': all_questions,
        'id': tpdata['esid'],
    }, ensure_ascii=False) # yapf: disable

    if args.output:
        with open(args.output, 'w') as f:
            print(results, file=f)
    else:
        print(results)


if __name__ == '__main__':
    main()
