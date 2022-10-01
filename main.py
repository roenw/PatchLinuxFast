import getpass
import paramiko
from termcolor import colored
import itertools
import threading
import time
import sys

username = ""
password = ""
done = False
mode = ""


def get_update_flow():
    global mode

    print("Welcome to the system patching script.")
    mode = input("Select automated or interactive mode [a/i]: ")


def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rWorking   [' + c + ']')
        sys.stdout.flush()
        time.sleep(0.1)


def get_credentials():
    global username
    global password

    username = input("SSH Username: ")
    password = getpass.getpass("SSH Password: ")


def run_sudo_command(command, server_address, server_username, server_pass):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=server_address,
                username=server_username,
                password=server_pass)
    # key file is acceptable here too

    session = ssh.get_transport().open_session()
    session.set_combine_stderr(True)

    session.get_pty()
    session.exec_command("sudo bash -c \"" + command + "\"")
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    stdin.write(server_pass + '\n')
    stdin.flush()
    print(stdout.read().decode("utf-8"))


def verify_creds_entered():
    if username and password:
        return
    else:
        print(colored("\nYou did not enter credentials. Exiting.", 'red'))
        exit()


def run_command_with_loading(command, ip, uname, passwd):
    global done
    done = False
    t = threading.Thread(target=animate)
    t.start()
    run_sudo_command(command, ip, uname, passwd)
    done = True


def perform_updates():
    def update_ubuntu(ip):
        print(colored("Updating package lists on " + system_ip + "...", 'cyan'))
        run_command_with_loading("ls -l", ip, username, password)
        print(colored("Upgrading packages on " + system_ip + "...", 'blue'))
        run_command_with_loading("ls -l", ip, username, password)
        print(colored("The update process appears to have exited. Please check output to verify successful upgrading.", "white", "on_green"))

    # Main updating function
    system_ip = input("System IP to patch: ")
    system_type = input("Select system OS [ubuntu/redhat]: ")

    if system_type == "ubuntu" or system_type == "u":
        print(colored("\nAttempting to update Ubuntu system located at " + system_ip, 'cyan'))
        update_ubuntu(system_ip)
    elif system_type == "redhat" or system_type == "r":
        print("redhat")
    else:
        print(colored("\nInvalid system type. Expected \"ubuntu\" or \"redhat\"", 'red'))
        return


if __name__ == '__main__':
    get_update_flow()

    if mode == "i":
        # Obtain and verify credentials are entered
        get_credentials()
        verify_creds_entered()

        # SSH into the systems and perform updates
        perform_updates()
    elif mode == "a":
        print(colored("Automated mode isn't supported yet. Sorry!\n", 'red'))
        exit()