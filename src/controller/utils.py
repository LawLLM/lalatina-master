num_to_hex = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'A',
    11: 'B',
    12: 'C',
    13: 'D',
    14: 'E',
    15: 'F',
}

hex_to_numb = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'A': 10,
    'B': 11,
    'C': 12,
    'D': 13,
    'E': 14,
    'F': 15,
}

def RGB_to_HEX(r, g, b):
    hex = '#'

    hex += num_to_hex[int(r/16)] + num_to_hex[r%16]
    hex += num_to_hex[int(g/16)] + num_to_hex[g%16]
    hex += num_to_hex[int(b/16)] + num_to_hex[b%16]

    return hex

def HEX_to_RGB(hex):
    r = hex_to_numb[hex[1]] * 16 + hex_to_numb[hex[2]]
    g = hex_to_numb[hex[3]] * 16 + hex_to_numb[hex[4]]
    b = hex_to_numb[hex[5]] * 16 + hex_to_numb[hex[6]]

    return r, g, b

def correct_minutes(minutes_str):
    parte_entera = minutes_str.split('.')[0]
    parte_decimal = minutes_str.split('.')[1]

    if parte_decimal == '0':
        return parte_entera
    else:
        parte_decimal = parte_decimal[:2]
        return parte_entera + '.' + parte_decimal

def time_tournament_to_str(time_left):
    if time_left > 86400:
        num_days = int(time_left / 86400)
        num_hours = int((time_left % 86400) / 3600)
        time_to_start = f'{num_days}d {num_hours}h'
    elif time_left > 3600:
        num_hours = int(time_left / 3600)
        num_minutes = int((time_left % 3600) / 60)
        time_to_start = f'{num_hours}h {num_minutes}m'
    elif time_left > 60:
        num_minutes = int(time_left / 60)
        num_seconds = int(time_left % 60)
        time_to_start = f'{num_minutes}m {num_seconds}s'
    else:
        num_seconds = time_left + 1
        time_to_start = f'{num_seconds}s'

    return time_to_start

def remove_ends(url):
    if url.startswith('<'):
        url = url[1:]
    if url.endswith('>'):
        url = url[:-1]

    return url


def ptTimeToSeconds(pt_time):
    time_str = pt_time[2:]

    time_dict = {}

    numbers = []
    categories = []

    i = 0

    while i < len(time_str):
        number = ""

        while(time_str[i].isdigit()):
            number += time_str[i]
            i += 1

        numbers.append(number)

        categories.append(time_str[i])

        if number == "":
            number = 0
        time_dict[time_str[i]] = int(number)
        i += 1

    duration = 0

    if 'Y' in time_dict.keys():
        duration += time_dict['Y'] * 31536000

    if 'W' in time_dict.keys():
        duration += time_dict['W'] * 604800

    if 'D' in time_dict.keys():
        duration += time_dict['D'] * 86400

    if 'H' in time_dict.keys():
        duration += time_dict['H'] * 3600

    if 'M' in time_dict.keys():
        duration += time_dict['M'] * 60

    if 'S' in time_dict.keys():
        duration += time_dict['S']

    return duration


def time_to_str(duration: int):
    time_hrs = str(int(duration / 3600))
    if len(time_hrs) == 1:
        time_hrs = '0' + time_hrs

    time_min = str(int((duration % 3600) / 60))
    if len(time_min) == 1:
        time_min = '0' + time_min

    time_seg = str(duration % 60)
    if len(time_seg) == 1:
        time_seg = '0' + time_seg

    time_str = ""

    if int(time_hrs) != 0:
        time_str = time_str + time_hrs + ":"
    time_str = time_str + time_min + ":" + time_seg

    return time_str


def format_solution(solution):
    solution_eng = []

    for item in solution:
        solution_eng.append(item.replace("\n✓", ""))

    solution_esp = []

    for item in solution_eng:
        aux = item.replace("Q", "D")
        aux = aux.replace("R", "T")
        aux = aux.replace("B", "A")
        aux = aux.replace("N", "C")
        aux = aux.replace("K", "R")

        solution_esp.append(aux)

    return (solution_eng, solution_esp)


def run():
    a = ['Nc6+\n✓', 'Ka4', 'Rxa6#\n✓']

    b, c = format_solution(a)

    print(b)
    print(c)


if __name__ == "__main__":
    run()