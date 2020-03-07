import argparse
import json

from lib import bitdecode_answer


def gen_script(matrix):
    return f"""
function get_urlparam(key) {{
  re = new RegExp(`${{key}}=([^&]+)`);
  match = re.exec(window.location.search);
  return match && match[1];
}}

esid = get_urlparam("id");
data = JSON.parse('{json.dumps(matrix, ensure_ascii=False)}');
data.forEach(([key, value]) => storage.setItem(esid + key, value));
window.location.reload();
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('exhaust_file', help="Input json file")
    parser.add_argument('-o',
                        '--output',
                        default=None,
                        help="Output javascript file")
    parser.add_argument(
        '-f',
        '--fall-back',
        default=False,
        action='store_true',
        help="Use user's selection but fall back to true answer")
    parser.add_argument('-T',
                        '--true-answer',
                        default=False,
                        action='store_true',
                        help="Use true answer")
    args = parser.parse_args()

    with open(args.exhaust_file) as f:
        data = json.load(f)

        if args.true_answer:
            matrix = [[
                f"{q['id']}",
                ','.join(list(q['answer'])),
            ] for q in data['questions'] if q['answer'] != None]
        elif args.fall_back:
            matrix = [[
                f"{q['id']}",
                ','.join(list(bitdecode_answer(q['user_selection']))),
            ] if q['user_selection'] != 0 else [
                f"{q['id']}",
                ','.join(list(q['answer'])),
            ] for q in data['questions']]
        else:
            matrix = [[
                f"{q['id']}",
                ','.join(list(bitdecode_answer(q['user_selection']))),
            ] for q in data['questions'] if q['user_selection'] != 0]

        script = gen_script(matrix)

    if args.output:
        with open(args.output, 'w') as f:
            print(script, file=f)
    else:
        print(script)
