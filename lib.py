import yaml


class SelectionFlags:
    A = 0b00000001
    B = 0b00000010
    C = 0b00000100
    D = 0b00001000
    E = 0b00010000
    F = 0b00100000
    G = 0b01000000
    H = 0b10000000


def bitencode_answer(answer):
    ans = 0
    for c in answer:
        if c == 'A':
            ans |= SelectionFlags.A
        elif c == 'B':
            ans |= SelectionFlags.B
        elif c == 'C':
            ans |= SelectionFlags.C
        elif c == 'D':
            ans |= SelectionFlags.D
        elif c == 'E':
            ans |= SelectionFlags.E
        elif c == 'F':
            ans |= SelectionFlags.F
        elif c == 'G':
            ans |= SelectionFlags.G
        elif c == 'H':
            ans |= SelectionFlags.H
    return ans


def bitdecode_answer(answer):
    ans = []
    if answer & SelectionFlags.A: ans.append('A')
    if answer & SelectionFlags.B: ans.append('B')
    if answer & SelectionFlags.C: ans.append('C')
    if answer & SelectionFlags.D: ans.append('D')
    if answer & SelectionFlags.E: ans.append('E')
    if answer & SelectionFlags.F: ans.append('F')
    if answer & SelectionFlags.G: ans.append('G')
    if answer & SelectionFlags.H: ans.append('H')

    return ''.join(ans)


def get_config(filename="./config.yaml"):
    with open(filename) as f:
        data = yaml.load(f)
    return data
