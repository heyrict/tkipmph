import argparse
import json

from lib import bitdecode_answer, get_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('exhaust_file', help="Input json file")
    parser.add_argument('-o',
                        '--output',
                        default=None,
                        help="Output javascript file")
    parser.add_argument('-c',
                        '--config',
                        default='./config.yaml',
                        help="Config yaml file")
    args = parser.parse_args()

    with open(args.exhaust_file) as f:
        config = get_config(args.config)
        data = json.load(f)
        matrix = [[
            f"{config['USERID']}{q['id']}",
            bitdecode_answer(q['user_selection'])
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
