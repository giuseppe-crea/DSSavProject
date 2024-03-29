import shlex
import os.path
import Scanner
import time
import digital_signature

# Global variables
dir_to_scan = './'
type_ext = '.*'
db = 'default_db.db'
period_to_scan = -1


def proc_param(param_name, param_value):
    if param_name == '-d':
        global dir_to_scan
        if not os.path.isdir(param_value):
            return 11
        dir_to_scan = param_value
    elif param_name == '-t':
        global type_ext
        list_types = param_value.split(',')
        type_ext = '|'.join(['.' + ext_type for ext_type in list_types])
    elif param_name == '-p':
        global period_to_scan
        try:
            period_to_scan = int(param_value)
            if period_to_scan < 1:
                return 31
        except ValueError:
            return 32
    elif param_name == '-b':
        global db
        if os.path.isfile(param_value):
            if os.path.splitext(param_value)[1] == '.db':
                db = param_value
            else:
                return 41
        else:
            return 42
    else:
        return 51
    return 0


def help_manual():
    print('\nUsage:\n'
          '-d   "PATH"      :specify folder to scan\n'
          '-t   REGEX       :specify file extensions to scan for\n'
          '-b   "PATH"      :specify database to use for this scan\n'
          '-p   INT         :specify scan interval length in seconds\n'
          'exit             :quit script\n'
          'In order to interrupt a recurring scan, use SIGINT.')


def main():
    help_manual()
    while True:
        running_continuous_scan_flag = False
        try:
            global dir_to_scan, type_ext, db, period_to_scan
            dir_to_scan = './'
            type_ext = '.*'
            db = 'default_db.db'
            period_to_scan = -1

            scan_cmd = input('\n\nrescan > ')
            split_cmd = shlex.split(scan_cmd)
            if scan_cmd == 'exit':
                exit()
            if len(split_cmd) % 2 != 0:
                print("Incorrect Command!")
                help_manual()
                continue

            result_code = 0
            for token in split_cmd[::2]:
                result_code = proc_param(token, split_cmd[split_cmd.index(token) + 1])
            if result_code != 0:
                if result_code == 11:
                    print('The path indicated is not a directory from which you can scan.')
                elif result_code == 31:
                    print('The scan period must be greater than or equal to 1 minute.')
                elif result_code == 32:
                    print('The period must be an integer.')
                elif result_code == 41:
                    print('The indicated file is not a database.')
                elif result_code == 42:
                    print('The indicated database does not exist.')
                else:
                    print('Incorrect parameter.')
                continue
            else:
                print(f'\nDirectory: {dir_to_scan}')
                print(f'Type(s) of file to scan: {type_ext}')
                print(f'Database: {db}')
                digital_signature.define_path_json(db)
                # check if the database is present within the json collecting database signatures
                if digital_signature.check_db_exist(db):
                    # check if the recorded signature corresponds
                    if not digital_signature.check_db(db):
                        # if it doesn't
                        print('the digital signature of the db does not match')
                        continue
                else:
                    # new database not yet present within the json
                    digital_signature. add_db_to_json(db)
                        
                if period_to_scan == -1:
                    print('\nScanned files:')
                    Scanner.scan_cycle(dir_to_scan, type_ext, db)
                else:
                    print(f'Scan period: {period_to_scan} seconds')
                    n = 1
                    running_continuous_scan_flag = True
                    while True:
                        print(f'\nScan number: {n}')
                        print('Scanned files:')
                        Scanner.scan_cycle(dir_to_scan, type_ext, db)
                        time.sleep(period_to_scan)
                        n += 1
                # update signature
                digital_signature.mod_dt_json(db)
                
        except KeyboardInterrupt:
            # capture keyboard interrupts if and only if we are running a scan
            if running_continuous_scan_flag:
                # update signature in case we quit a continuous scan cycle
                # noinspection PyUnboundLocalVariable
                digital_signature.mod_dt_json(db)
                continue
            else:
                exit()


main()
