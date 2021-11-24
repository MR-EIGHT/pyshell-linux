import os
import platform
import sys

"""
A simple shell implemented for Unix-like operating systems, in python.

Requirements:
A Unix-like OS.
python >= 3.10 :)

"""


# Printing colorful texts in terminal using ANSI escape sequences.
# Wrapped in a class for simplification, ease of use and understanding.

class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    # Other colors commented for later developements...
    # OKCYAN = '\033[96m'
    # HEADER = '\033[95m'
    # WARNING = '\033[93m'
    # UNDERLINE = '\033[4m'


fork_exception = Exception("Couldn't fork a child process!")


def shell():
    run_command(["clear"])  # Clear the terminal
    last_command = None  # last_command keeps the last entered command. It's used to implement history functionality.
    while True:  # An infinite loop that keeps repeating until the user enters "exit" or some exception occur.
        command = input(Colors.BOLD +
                        Colors.OKBLUE + '(' + os.getlogin() + '@' + platform.system() + ')' + Colors.ENDC + Colors.OKGREEN + os.getcwd() + Colors.ENDC + " > $" + Colors.ENDC).strip().split()
        # Covering exit functionality.
        if command[0] == 'exit':
            sys.exit(1)
        # Tokenize piped commands
        elif '|' in command:
            run_pipes(" ".join(command))
        # Command history that keeps the last executed command.
        elif command[0] == "!!":
            if last_command is None:
                print(Colors.FAIL + "There is no previous command to execute!" + Colors.ENDC)
            else:
                run_command(last_command)
        # If none of the above conditions is met, then we have a regular Unix-Command to process.
        else:
            last_command = command.copy()
            run_command(command)


"""
Function that processes regular commands and redirection.
"""


def run_command(command):
    # If the entered command contains "&" the concurrency flag set to be true and the "&" gets deleted from the command.
    conc_flag = command[-1] == '&'
    if command[-1] == '&':
        del command[-1]
    # Covers ChangeDirectory or cd command.
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
            # If there is a ">" or "<" in command, thre is a redirection to process.
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
        # if concurrency flag is false then the parent has to wait for the child to finish and call wait() syscall
        # otherwise, it's neglected and parent continues to work while the child is working separately.
        if not conc_flag:
            os.waitpid(child, 0)

    """
    Function for processing piped commands in two different ways:
    1- using pipe() system call.
    2- using a temp file.
    """


def run_pipes(command, flag="pipe"):
    command = command.split('|')
    command = [com.strip().split() for com in command]

    match flag:
        # In case we want to use pipe syscall.
        case "pipe":
            child1 = os.fork()
            if child1 < 0:
                # Ecception occured.
                raise fork_exception
            elif child1 == 0:
                # In child process
                oread, owrite = os.pipe()
                child2 = os.fork()
                if child2 > 0:
                    # In parent process
                    os.close(owrite)
                    os.dup2(oread, sys.stdin.fileno())
                    os.dup2(oread, sys.stderr.fileno())
                    os.execvp(command[1][0], args=command[1])
                if child2 < 0:
                    # Ecception occured.
                    raise fork_exception
                elif child2 == 0:
                    # In the second child process. (child of "child1")
                    os.close(oread)
                    os.dup2(owrite, sys.stdout.fileno())
                    os.execvp(command[0][0], command[0])
                    sys.exit()
            os.wait()

        # In case we want to use a temp file for piping.
        case "file":
            child1 = os.fork()
            if child1 < 0:
                # Ecception occured.
                raise fork_exception
            elif child1 == 0:
                # In first-child process
                with open('temp', 'w') as rd_output:
                    os.dup2(rd_output.fileno(), sys.stdout.fileno())
                os.execvp(command[0][0], args=command[0])
                sys.exit(0)
            os.wait()
            child2 = os.fork()
            if child2 < 0:
                # Ecception occured.
                raise fork_exception
            elif child2 == 0:
                # In second-child process
                with open('temp', 'r') as rd_input:
                    os.dup2(rd_input.fileno(), sys.stdin.fileno())
                os.execvp(command[1][0], command[1])
                sys.exit()
            os.wait()
            os.remove('temp')


# Deriver code
if __name__ == '__main__':
    shell()
