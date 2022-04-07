import json
from operator import itemgetter

FILENAME = "highscores.json"
NR_HIGHSCORE_ENTRYS = 5


def is_highscore(user_score):
    try:
        with open(FILENAME, 'r') as file:
            data = json.loads(file.read())
            data = sorted(data, key=itemgetter(1), reverse=True)
    except FileNotFoundError:
        return True

    try:
        for i in range(0, NR_HIGHSCORE_ENTRYS):
            if data[i][1] < user_score:
                return True
    except IndexError:
        return True
    return False


def get_all_highscores():
    highscores = []
    try:
        with open(FILENAME, 'r') as file:
            data = json.loads(file.read())
            data = sorted(data, key=itemgetter(1), reverse=True)
    except FileNotFoundError:
        return highscores

    try:
        for i in range(0, NR_HIGHSCORE_ENTRYS):
            highscores.append(data[i])
    except IndexError:
        return highscores
    return highscores


def save_highscore(user_name, user_score):
    try:
        with open(FILENAME, 'r') as file:
            data = json.loads(file.read())
            data.append((user_name, user_score))
    except FileNotFoundError:
        data = [(user_name, user_score)]

    with open(FILENAME, 'w') as file:
        json_obj = json.dumps(data)
        file.write(json_obj)


def main():
    pass


if __name__ == '__main__':
    main()
