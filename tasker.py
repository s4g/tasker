import sys, os, io
import inspect
import pkgutil
import importlib
import operator

ARGPARSE_SIG = '(*ap_args)'


def format_docsting(docstring, additional_indent=0):
    """Adapted from pep 257"""
    lines = docstring.expandtabs().splitlines()

    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())

    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    indent_str = ' ' * additional_indent
    return '\n'.join((indent_str + line) for line in trimmed)


def list_package(package_name: str):
    package = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__):
        qualified_name = package_name + "." + module_name
        yield qualified_name
        if is_pkg:
            yield from list_package(qualified_name)


def print_usage(tasks_package_name, verbose=False):
    common_trim_len = len(tasks_package_name) + 1

    print('Usage: %s <task-name> [parameter, ...]\n' % os.path.basename(sys.argv[0]))
    print('All available tasks:')
    print('    help      # print help screen')

    module_names = [tasks_package_name] + list(list_package(tasks_package_name))

    for task_module_name in module_names:
        try:
            task_module = importlib.import_module(task_module_name)
        except ImportError:
            print('Failed to import', task_module_name)
        else:
            docstring = '# ' + task_module.__doc__ if task_module.__doc__ else ''

            all_tasks = [(fn, fun) for fn, fun in vars(task_module).items()
                if (fn.endswith('_task') and inspect.isfunction(fun))]

            if all_tasks:
                print('\n    In module {}  {}'.format(task_module_name, docstring))

            for fn, fun in sorted(all_tasks, key=operator.itemgetter(0)):
                prefix = task_module_name[common_trim_len:]
                task_name = fn[:-5]  # remove the suffix "_task"
                qualified_name = (prefix + '.' + task_name) if prefix else task_name
                signature = str(inspect.signature(fun))
                if signature == ARGPARSE_SIG:
                    signature = 'Argparse based. Run with --help for full parameter list'
                print('        {} :  {}'.format(qualified_name, signature))
                if fun.__doc__ is not None:
                    if verbose:
                        print(format_docsting(fun.__doc__, 12))
                        print()
                    else:
                        print(format_docsting(fun.__doc__, 12).split('\n', 1)[0])


def get_task_function(tasks_package_name, fq_task_function):
    if '.' in fq_task_function:
        task_module_name, task_name = fq_task_function.rsplit('.', maxsplit=1)
        fq_task_module_name = f'{tasks_package_name}.{task_module_name}'
    else:
        task_name = fq_task_function
        fq_task_module_name = tasks_package_name

    task_module = importlib.import_module(fq_task_module_name)
    return getattr(task_module, task_name + '_task')


def main(tasks_package_name='tasks'):
    if len(sys.argv) < 2:
        print('ERROR: Missing parameters. Assuming "help" task\n')
        task = 'help'
        args = []
    else:
        task, *args = sys.argv[1:]

    if task == 'help':
        if args:
            fn, *_ = args
            task_function = get_task_function(tasks_package_name, fn)
            signature = str(inspect.signature(task_function))
            if signature == ARGPARSE_SIG:
                sys.argv[0] = fn
                task_function('--help')
            else:
                print('        {} :  {}'.format(fn, signature))
                print(format_docsting(task_function.__doc__, 12))
            print()
        else:
            print_usage(tasks_package_name)
    else:
        try:
            task_function = get_task_function(tasks_package_name, task)
        except (ImportError, AttributeError):
            print('Task', task, 'not found')
        else:
            return task_function(*args)


if __name__ == '__main__':
    fq_module = f'{__package__}.tasker' if __package__ else 'tasker'

    main_params = '"{}"'.format(sys.argv[1]) if len(sys.argv) > 1 else ''
    if sys.platform.startswith('win'):
        with io.open('run_task.bat', 'wt') as f:
            f.write(f'@{sys.executable} run_task.py %1 %2 %3 %4 %5 %6 %7 %8 %9\n')

        with io.open('run_task.py', 'wt') as f:
            f.write(f'from {fq_module} import main\nmain({main_params})\n')
    else:
        code = '\n'.join([
            '#!' + sys.executable,
            f'from {fq_module} import main',
            f'main({main_params})\n'
        ])

        with io.open('run_task', 'wt') as f:
            f.write(code)
            os.chmod(f.name, 0o777)
