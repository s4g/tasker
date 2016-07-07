from __future__ import print_function, unicode_literals
import sys, os, io
import inspect
import pkgutil
import importlib
import operator


def real_abs_path(path):
    return os.path.realpath(os.path.abspath(path))


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


def print_usage(tasks_package_name, verbose=False):
    tasks_package_path = importlib.import_module(tasks_package_name).__path__[0]
    task_module_names = [tasks_package_name] + [(tasks_package_name + '.' + mn)
        for mn in sorted(i[1] for i in pkgutil.walk_packages([tasks_package_path]))]
    common_trim_len = len(tasks_package_name) + 1

    print('Usage: %s <task-name> [parameter, ...]\n' % os.path.basename(sys.argv[0]))
    print('All available tasks:')
    print('    help      # print help screen')
    print('    morehelp  # print verbose help screen')

    for task_module_name in task_module_names:
        try:
            task_module = importlib.import_module(task_module_name)
        except ImportError:
            print('Failed to import', task_module_name)
        else:
            docstring = '# ' + task_module.__doc__ if task_module.__doc__ else ''
            print('\n    In module {}  {}'.format(task_module_name, docstring))

            all_tasks = [(fn, fun) for fn, fun in vars(task_module).items()
                if (fn.endswith('_task') and inspect.isfunction(fun))]

            for fn, fun in sorted(all_tasks, key=operator.itemgetter(0)):
                prefix = task_module_name[common_trim_len:]
                task_name = fn[:-5]  # remove the suffix "_task"
                qualified_name = (prefix + '.' + task_name) if prefix else task_name
                print('        {} :  {}'.format(
                    qualified_name, inspect.formatargspec(*inspect.getargspec(fun))))
                if fun.__doc__ is not None:
                    if verbose:
                        print(format_docsting(fun.__doc__, 12))
                        print()
                    else:
                        print(format_docsting(fun.__doc__, 12).split('\n', 1)[0])


def main(tasks_package_name='tasks'):
    base_path = os.path.dirname(real_abs_path(inspect.stack()[1][0].f_globals['__file__']))
    sys.path.insert(0, base_path)
    tasks_path_split = tasks_package_name.split('.')

    if len(sys.argv) < 2:
        print('ERROR: Missing parameters. Assuming "help" task\n')
        task = 'help'
        args = []
    else:
        task = sys.argv[1]
        args = sys.argv[2:]

    if task == 'help':
        print_usage(tasks_package_name)
    elif task == 'morehelp':
        print_usage(tasks_package_name, verbose=True)
    else:
        task_split = task.split('.')
        task_module_name = '.'.join(tasks_path_split + task_split[:-1])
        task_function_name = task_split[-1] + '_task'
        try:
            task_module = importlib.import_module(task_module_name)
            task_function = getattr(task_module, task_function_name)
        except (ImportError, AttributeError):
            print('Task', task, 'not found')
        else:
            return task_function(*args)


if __name__ == '__main__':
    parsed_path = os.path.splitext(os.path.splitdrive(__file__)[1])[0].split(os.sep)
    for j in range(1, len(parsed_path)):
        fq_module = '.'.join(parsed_path[-j:])
        try:
            __import__(fq_module)
            break
        except ImportError:
            continue
    else:
        raise ImportError('Unable to detect fully qualified tasker module name')

    main_params = '"{}"'.format(sys.argv[1]) if len(sys.argv) > 1 else ''
    if sys.platform.startswith('win'):
        with io.open('run_task.bat', 'wt') as f:
            f.write(u'@{} run_task.py %1 %2 %3 %4 %5 %6 %7 %8 %9\n'.format(sys.executable))

        with io.open('run_task.py', 'wt') as f:
            f.write('from {} import main\nmain({})\n'.format(fq_module, main_params))
    else:
        code = u'\n'.join([
            '#!' + sys.executable,
            'from %s import main' % fq_module,
            'main(%s)\n' % main_params
        ])

        with io.open('run_task', 'wt') as f:
            f.write(code)
            os.chmod(f.name, 0o777)
