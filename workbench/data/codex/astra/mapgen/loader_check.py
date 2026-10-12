"""Exercise only the packaged map loader; abort before any bot or turn exists."""
from unswbc.engine import EngineModule

class Loaded(BaseException):
    pass

def load_only(data):
    notices = []
    def spawn(*args):
        raise Loaded()
    def reply(*args):
        raise AssertionError('A turn must never execute')
    try:
        EngineModule().run(data, reply, bot_spawn=spawn, on_notice=notices.append, debug=0)
    except Loaded:
        return {'loaded': True, 'notices': notices, 'turns': 0}
    except Exception as error:
        return {'loaded': False, 'error': str(error), 'notices': notices, 'turns': 0}
    raise AssertionError('Loader did not stop at initialization')

if __name__ == '__main__':
    import json
    for n in [1,2,9,10,64,65,128,129]:
        data = f'MAP {n} {n}\nSYMMETRY xy\nTILE_COUNT 0\nEDGE_COUNT 0\nDRAGON_COUNT 2\nDRAGON 0 2 0 0 1 0\nDRAGON 1 2 {n-1} {n-1} {n-2} {n-1}\nEND\n'.encode()
        print(n, json.dumps(load_only(data)))
