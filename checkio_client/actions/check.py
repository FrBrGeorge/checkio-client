import sys
import os
import time

from checkio_client.settings import conf
from checkio_client.api import get_mission_info, check_solution,\
    restore, run_solution
from checkio_client.utils.code import code_for_check

def get_filename(args):
    if args.filename:
        return args.filename
    default_data = conf.default_domain_data
    if 'solutions' not in default_data:
        raise ValueError('Filename is not defined')

    filename = args.mission[0].replace('-', '_') + '.' + default_data['extension']
    return os.path.join(default_data['solutions'], filename)


def main(args):
    filename = get_filename(args)
    mission = args.mission[0]

    domain_data = conf.default_domain_data

    if main_run(args):
        return
    print()
    print('Start checking...')
    print()
    mission_info = get_mission_info(mission)
    mission_id = mission_info['id']
    with open(filename) as fh:
        data = check_solution(code_for_check(fh.read()), mission_id)
    while data:
        block = data.pop(0)
        com = block[0]
        if com == 'start_in':
            print('*** ' + block[1] + ' ***' )
        elif com == 'in':
            print('->' + str(block[1]))
        elif com == 'out':
            print('<-' + str(block[1]))
        elif com == 'ext':
            res = block[1]
            if not res['result']:
                print('!!' + str(res['answer']))
        elif com == 'check':
            if block[1]:
                print('!!! Congratulation !!!')
            else:
                print('!! Failed !!')
        elif com == 'wait':
            print('Waiting for the next piece of data...')
            time.sleep(block[2])
            print('Restore checking...')
            data = restore(block[1])
        else:
            print(block)
    

def main_run(args):
    filename = get_filename(args)
    mission = args.mission[0]

    domain_data = conf.default_domain_data

    print()
    print('Start running...')
    print()

    if 'executable' in domain_data:
        return os.system(' '.join((domain_data['executable'], filename)))

    with open(filename) as fh:
        data = run_solution(code_for_check(fh.read()))
    ret = False
    while data:
        block = data.pop(0)
        com = block[0]
        if com == 'err':
            print(block[1], end='')
            ret = True
        elif com == 'out':
            print(str(block[1]), end='')
        elif com == 'wait':
            data = restore(block[1])
        else:
            print(block)

    print()
    return ret