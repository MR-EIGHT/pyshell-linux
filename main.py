import os
import sys
import platform


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def shell():
    last_command = None
    while True:
        command = input(
            BColors.OKBLUE + '(' + os.getlogin() + '@' + platform.system() + ')' + BColors.ENDC + BColors.OKGREEN + os.getcwd() + BColors.ENDC + " > $").strip().split()
        if '|' in command:
            run_pipes(" ".join(command))
        elif command[0] == "!!":
            if last_command is None:
                print(BColors.FAIL + "There is no previous command to execute!" + BColors.ENDC)
            else:
                run_command(last_command)

        else:
            last_command = command.copy()
            run_command(command)


def run_command(command):
    conc_flag = True if command[-1] == '&' else False

    if command[-1] == '&':
        del command[-1]
    if command[0] == 'cd':
        try:
            os.chdir(command[1])
        except FileNotFoundError:
            print(BColors.FAIL + "There is no such directory!" + BColors.ENDC)

    else:
        child = os.fork()
        if child < 0:
            raise Exception("Couldn't fork a child process!")
        if child == 0:
            if ">" in command:
                with open(command[command.index(">") + 1], 'w') as rd_output:
                    os.dup2(rd_output.fileno(), sys.stdout.fileno())
                    del command[command.index(">") + 1]
                    del command[command.index(">")]

            if "<" in command:
                with open(command[command.index("<") + 1], 'r') as rd_input:
                    os.dup2(rd_input.fileno(), sys.stdin.fileno())
                    del command[command.index("<") + 1]
                    del command[command.index("<")]
            try:
                os.execvp(command[0], args=command)
            except FileNotFoundError:
                print(BColors.FAIL + "There is no such File or Directory!" + BColors.ENDC)

            sys.exit(0)
        if not conc_flag:
            os.waitpid(child, 0)


def run_pipes(command):
    command = command.split('|')
    command = [com.strip().split() for com in command]

    child1 = os.fork()
    if child1 < 0:
        raise Exception("Couldn't fork a child process!")
    elif child1 == 0:
        with open('temp', 'w') as rd_output:
            os.dup2(rd_output.fileno(), sys.stdout.fileno())
        os.execvp(command[0][0], args=command[0])
        sys.exit(0)
    os.wait()
    child2 = os.fork()
    if child2 < 0:
        raise Exception("Couldn't fork a child process!")
    elif child2 == 0:
        with open('temp', 'r') as rd_input:
            os.dup2(rd_input.fileno(), sys.stdin.fileno())
        os.execvp(command[1][0], command[1])
        sys.exit()
    os.wait()
    os.remove('temp')


if __name__ == '__main__':
    shell()
