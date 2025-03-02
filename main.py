import sys
import shutil
import os
import subprocess
import shlex
import platform
import tkinter as tk
from tkinter import scrolledtext

# Import readline based on the platform
if platform.system() == 'Windows':
    import pyreadline3
    readline = pyreadline3.Readline()
else:
    import readline

built_in_commands = {}

def command(func):
    built_in_commands[func.__name__.split("_")[1]] = func
    return func

# Register built-in commands (decorator)
@command
def shell_exit(args):
    exit(int(args[0]) if args else 0)

@command
def shell_echo(args):
    sys.stdout.write(" ".join(args) + "\n")

@command
def shell_type(args):
    if args[0] in built_in_commands:
        sys.stdout.write(f"{args[0]} is a shell builtin\n")
    elif path := shutil.which(args[0]):
        sys.stdout.write(f"{args[0]} is {path}\n")
    else:
        sys.stdout.write(f"{args[0]}: not found\n")

@command
def shell_pwd(args):
    print(os.getcwd())

@command
def shell_cd(args):
    if len(args) != 1:
        print("cd: wrong number of arguments")
    else:
        try:
            # Expand ~ to the user's home directory
            path = os.path.expanduser(args[0])
            os.chdir(path)
        except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
            print(f"cd: {args[0]}: {e.strerror}")

@command
def shell_ls(args):
    path = args[0] if args else '.'
    try:
        for entry in os.listdir(path):
            print(entry)
    except FileNotFoundError:
        print(f"ls: cannot access '{path}': No such file or directory")

@command
def shell_help(args):
    for cmd in built_in_commands:
        print(cmd)

@command
def shell_mkdir(args):
    for path in args:
        try:
            os.makedirs(path)
        except FileExistsError:
            print(f"mkdir: cannot create directory '{path}': File exists")
        except PermissionError:
            print(f"mkdir: cannot create directory '{path}': Permission denied")

@command
def shell_rm(args):
    for path in args:
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
        except FileNotFoundError:
            print(f"rm: cannot remove '{path}': No such file or directory")
        except PermissionError:
            print(f"rm: cannot remove '{path}': Permission denied")
        except OSError as e:
            print(f"rm: cannot remove '{path}': {e.strerror}")

@command
def shell_cp(args):
    if len(args) != 2:
        print("cp: wrong number of arguments")
    else:
        src, dest = args
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
        except FileNotFoundError:
            print(f"cp: cannot copy '{src}': No such file or directory")
        except PermissionError:
            print(f"cp: cannot copy '{src}': Permission denied")
        except OSError as e:
            print(f"cp: cannot copy '{src}': {e.strerror}")

@command
def shell_mv(args):
    if len(args) != 2:
        print("mv: wrong number of arguments")
    else:
        src, dest = args
        try:
            shutil.move(src, dest)
        except FileNotFoundError:
            print(f"mv: cannot move '{src}': No such file or directory")
        except PermissionError:
            print(f"mv: cannot move '{src}': Permission denied")
        except OSError as e:
            print(f"mv: cannot move '{src}': {e.strerror}")

@command
def shell_cat(args):
    for path in args:
        try:
            with open(path, 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print(f"cat: cannot open '{path}': No such file or directory")
        except PermissionError:
            print(f"cat: cannot open '{path}': Permission denied")

@command
def shell_touch(args):
    for path in args:
        try:
            with open(path, 'a'):
                os.utime(path, None)
        except PermissionError:
            print(f"touch: cannot touch '{path}': Permission denied")

@command
def shell_head(args):
    if len(args) < 1:
        print("head: missing file operand")
    else:
        path = args[0]
        lines = int(args[1]) if len(args) > 1 else 10
        try:
            with open(path, 'r') as file:
                for _ in range(lines):
                    print(file.readline(), end='')
        except FileNotFoundError:
            print(f"head: cannot open '{path}': No such file or directory")
        except PermissionError:
            print(f"head: cannot open '{path}': Permission denied")

@command
def shell_tail(args):
    if len(args) < 1:
        print("tail: missing file operand")
    else:
        path = args[0]
        lines = int(args[1]) if len(args) > 1 else 10
        try:
            with open(path, 'r') as file:
                all_lines = file.readlines()
                for line in all_lines[-lines:]:
                    print(line, end='')
        except FileNotFoundError:
            print(f"tail: cannot open '{path}': No such file or directory")
        except PermissionError:
            print(f"tail: cannot open '{path}': Permission denied")

@command
def shell_chmod(args):
    if len(args) != 2:
        print("chmod: wrong number of arguments")
    else:
        mode, path = args
        try:
            os.chmod(path, int(mode, 8))
        except FileNotFoundError:
            print(f"chmod: cannot access '{path}': No such file or directory")
        except PermissionError:
            print(f"chmod: changing permissions of '{path}': Permission denied")

@command
def shell_find(args):
    path = args[0] if args else '.'
    try:
        for root, dirs, files in os.walk(path):
            for name in dirs + files:
                print(os.path.join(root, name))
    except FileNotFoundError:
        print(f"find: `{path}`: No such file or directory")
    except PermissionError:
        print(f"find: `{path}`: Permission denied")

@command
def shell_source(args):
    if len(args) != 1:
        print("source: wrong number of arguments")
    else:
        script_path = args[0]
        try:
            with open(script_path, 'r') as script_file:
                for line in script_file:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Ignore empty lines and comments
                        execute_command(line)
        except FileNotFoundError:
            print(f"source: cannot open '{script_path}': No such file or directory")
        except PermissionError:
            print(f"source: cannot open '{script_path}': Permission denied")

# Add the new command to the built-in commands
built_in_commands['source'] = shell_source

# for auto partial completion
def longest_common_prefix(strs):
    if not strs:
        return ""
    shortest = min(strs, key=len)
    for i, char in enumerate(shortest):
        for other in strs:
            if other[i] != char:
                return shortest[:i]
    return shortest

def completer(text, state):
    options = [cmd + ' ' for cmd in built_in_commands if cmd.startswith(text)]
    # add external executables to the options
    for path in os.environ["PATH"].split(os.pathsep):
        try:
            for entry in os.listdir(path):
                if entry.startswith(text) and os.access(os.path.join(path, entry), os.X_OK):
                    options.append(entry + ' ')
        except FileNotFoundError:
            continue

    if state == 0:
        completer.matches = options
        if len(completer.matches) > 1:
            common_prefix = longest_common_prefix([match.strip() for match in completer.matches])
            if common_prefix and common_prefix != text:
                completer.matches = [common_prefix + ' ']
            else:
                print('\a', end='', flush=True)
        elif len(completer.matches) == 1:
            completer.matches = [completer.matches[0]]

    return completer.matches[state] if state < len(completer.matches) else None

def execute_pipeline(commands):
    processes = []
    for i, command in enumerate(commands):
        if i == 0:
            # First command
            p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        elif i == len(commands) - 1:
            # Last command
            p = subprocess.Popen(shlex.split(command), stdin=processes[-1].stdout)
        else:
            # Intermediate commands
            p = subprocess.Popen(shlex.split(command), stdin=processes[-1].stdout, stdout=subprocess.PIPE)
        processes.append(p)
    
    for p in processes:
        p.wait()

def execute_command(user_input):

    if '|' in user_input:
        commands = user_input.split('|')
        execute_pipeline(commands)

    elif user_input.endswith('&'): #for background run
        subprocess.Popen(shlex.split(user_input[:-1].strip())) #popen allows to spawn new process
    
    else:
        commands, *args = shlex.split(user_input) #shlex handles both "" and ''
        if commands in built_in_commands:
            built_in_commands[commands](args)
        else:
            try:
                subprocess.run([commands] + args, check=True)
            except FileNotFoundError:
                print(f"{commands}: command not found")
            except subprocess.CalledProcessError as e:
                print(f"{commands}: command failed with exit code {e.returncode}")

def handle_redirection(user_input):
    
    if '2>' in user_input: #write and append standard error to a file
        
        append_std = '2>>' in user_input
        
        parts = user_input.split('2>>' if append_std else '2>')
        command_part, error_file = parts[0].strip(), parts[1].strip()
        commands, *args = shlex.split(command_part)
        
        with open(error_file, 'a' if append_std else 'w') as file:
            sys.stderr = file
            if commands in built_in_commands:
                built_in_commands[commands](args)
            else:
                try:
                    subprocess.run([commands] + args, stderr=file)
                except FileNotFoundError:
                    print(f"{commands}: command not found")
    else:
        #write and append output to a file
        append_mode = '>>' in user_input
       
        parts = user_input.split('>>' if append_mode else '>')
        command_part, output_file = parts[0].strip(), parts[1].strip()
        
        if command_part.endswith('1'): #handles both 1> and >
            command_part = command_part[:-1].strip()
        
        commands, *args = shlex.split(command_part)
        
        with open(output_file, 'a' if append_mode else 'w') as file:
            sys.stdout = file
            if commands in built_in_commands:
                built_in_commands[commands](args)
            else:
                try:
                    subprocess.run([commands] + args, stdout=file)
                except FileNotFoundError:
                    print(f"{commands}: command not found")
                except subprocess.CalledProcessError as e:
                    print(f"{commands}: command failed with exit code {e.returncode}")
            sys.stdout = sys.__stdout__

class RedirectText:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)

    def flush(self):
        pass

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Shell")

    # Create a text area for displaying output
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    text_area.pack(padx=10, pady=10)

    # Redirect stdout and stderr to the text area
    sys.stdout = RedirectText(text_area)
    sys.stderr = RedirectText(text_area)

    # Create an entry widget for user input
    entry = tk.Entry(root, width=100)
    entry.pack(padx=10, pady=10)

    def on_enter(event):
        user_input = entry.get()
        entry.delete(0, tk.END)
        readline.add_history(user_input)

        # Check for output redirection
        if '>' in user_input:
            handle_redirection(user_input)
        else:
            execute_command(user_input)

    entry.bind("<Return>", on_enter)

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    root.mainloop()

if __name__ == "__main__":
    main()
