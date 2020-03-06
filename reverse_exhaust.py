import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('exhaust_file', help="Input json file")
    args = parser.parse_args()

    with open(args.exhaust_file, 'r') as f:
        data = json.load(f)

        data['questions'] = list(reversed(data['questions']))

    with open(args.exhaust_file, 'w') as f:
        json.dump(data, f)
