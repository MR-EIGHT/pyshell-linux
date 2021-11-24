import os
import sys
import platform


class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    # Other colors commented for later developements...

    # OKCYAN = '\033[96m'
    # HEADER = '\033[95m'
    # FAIL = '\033[91m'
    # BOLD = '\033[1m'
    # UNDERLINE = '\033[4m'


fork_exception = Exception("Couldn't fork a child process!")


def shell():
    run_command(["clear"])  # Clear the terminal
    last_command = None
    while True:
        command = input(
            Colors.OKBLUE + '(' + os.getlogin() + '@' + platform.system() + ')' + Colors.ENDC + Colors.OKGREEN + os.getcwd() + Colors.ENDC + " > $").strip().split()
        if command[0] == 'exit':
            sys.exit(1)
        elif '|' in command:
            run_pipes(" ".join(command))
        elif command[0] == "!!":
            if last_command is None:
                print(Colors.FAIL + "There is no previous command to execute!" + Colors.ENDC)
            else:
                run_command(last_command)

        else:
            last_command = command.copy()
            run_command(command)


def run_command(command):
    conc_flag = command[-1] == '&'

    if command[-1] == '&':
        del command[-1]
    if command[0] == 'cd':
        try:
            os.chdir(command[1])
        except FileNotFoundError:
            print(Colors.FAIL + "There is no such directory!" + Colors.ENDC)

    else:
        child = os.fork()
        if child < 0:
            raise fork_exception
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
                print(Colors.FAIL + "There is no such File or Directory!" + Colors.ENDC)

            sys.exit(0)
        if not conc_flag:
            os.waitpid(child, 0)


def run_pipes(command):
    command = command.split('|')
    command = [com.strip().split() for com in command]

    child1 = os.fork()
    if child1 < 0:
        raise fork_exception
    elif child1 == 0:
        with open('temp', 'w') as rd_output:
            os.dup2(rd_output.fileno(), sys.stdout.fileno())
        os.execvp(command[0][0], args=command[0])
        sys.exit(0)
    os.wait()
    child2 = os.fork()
    if child2 < 0:
        raise fork_exception
    elif child2 == 0:
        with open('temp', 'r') as rd_input:
            os.dup2(rd_input.fileno(), sys.stdin.fileno())
        os.execvp(command[1][0], command[1])
        sys.exit()
    os.wait()
    os.remove('temp')


if __name__ == '__main__':
    shell()
