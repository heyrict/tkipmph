import argparse
import json

from lib import bitdecode_answer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('exhaust_file', help="Input json file")
    parser.add_argument('-o',
                        '--output',
                        default=None,
                        help="Output javascript file")
    parser.add_argument('-I',
                        '--id',
                        required=True,
                        help="Id in url query parameter")
    parser.add_argument('-T',
                        '--true_answer',
                        default=False,
                        action='store_true',
                        help="Use true answer")
    args = parser.parse_args()

    with open(args.exhaust_file) as f:
        data = json.load(f)

        if args.true_answer:
            matrix = [[
                f"{args.id}{q['id']}",
                ','.join(list(q['answer'])),
            ] for q in data['questions'] if q['answer'] != None]
        else:
            matrix = [[
                f"{args.id}{q['id']}",
                ','.join(list(bitdecode_answer(q['user_selection']))),
            ] for q in data['questions'] if q['user_selection'] != 0]

        script = f"""
        data = JSON.parse(`{json.dumps(matrix, ensure_ascii=False)}`);
        data.forEach(([key, value]) => storage.setItem(key, value));
        window.location.reload();
        """

    if args.output:
        with open(args.output, 'w') as f:
            print(script, file=f)
    else:
        print(script)
