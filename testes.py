from functools import wraps


def wee(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = 'Weeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        return f(data, *args, **kwargs)
    return decorated


@wee
def main(data):
    print(data)


if __name__ == '__main__':
    main()
