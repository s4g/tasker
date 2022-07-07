Tasker
======

Tasker is a way to organize your scripts. If you have dozens of small scripts and you keep forgetting what they do and what parameters they take, **tasker** is for you. Instead of scripts you write functions, put them in a file or a couple of them, and then run the main tasker script giving them the task name and the parameters of the task like this:

::

    run_task <task-name> [<task-parameter> ...]

The built-in **help** task will scan your tasks package and give you the call signatures and docstrings of your tasks (see example below).

To be considered a task, the function name should end with ``_task``. The task name is the function name less the suffix. Suppose we have the following file stucture:

::

    run_task
    tasks/
        __init__.py
        module1.py

``__init__.py``

.. code-block:: python

    def taskone_task(p1):
        print('in taskone_task, parameters:', p1)

    def tasktwo_task(p1, p2):
        print('in tasktwo_task, parameters:', p1, p2)

and ``module1.py``

.. code-block:: python

    def t1_task(p1):
        """This is the task's documentation string.

        Continuation of the docstring
        """
        print('in t1_task, parameters:', p1)

    def t2_task(p1, p2=None):
        print('in t2_task, parameters:', p1, p2)


To generate the ``run_task`` script in the current directory run:

::

    python -m tasker <fully-qualified-name-of-tasks-package>  # default = "tasks"


A run of the script with the built-in **help** task produces the following::

    ./run_task help
    Usage: run_task <task-name> [parameter, ...]

    All available tasks:
        help      # print help screen

        In module tasks
            taskone :  (p1)
            tasktwo :  (p1, p2)

        In module tasks.module1
            module1.t1 :  (p1)
                This is the task's documentation string.
            module1.t2 :  (p1, p2=None)

We see the call signatures of the tasks.
If a task function contains a docstring the first line of the docstring will also be included.
To print the complete docstring of a task run::

    ./run_task help <task-name>

IMPORTANT: All task parameters are strings.

With the above setup we can run the following examples in the current directory
(which just print the parameters):

::

    ./run_task taskone foo          # prints foo
    ./run_task tasktwo foo baz      # prints foo, baz
    ./run_task tasktwo foo          # fails, not enough parameters
    ./run_task module1.t1 spam      # prints spam
    ./run_task module1.t2 spam ham  # prints spam, ham
    ./run_task module1.t2 spam      # works too because of default value of the second parameter

You will want to put something meaningful in your tasks.

You can include tasks with distribution of your project and run them all with a single installed script. Suppose your project looks like this:

::

    myproject/
        __init__.py
        somestuff.py
        tasks/

Then you can include the following snippet in ``__init__.py``:

.. code-block:: python

    def run_task():
        import tasker
        tasker.main('tasks')

then include the following in your setuptools-based ``setup.py``:

::

    entry_points={
        'console_scripts': [
            'myproject_run_task = myproject:run_task',
            ],
        }

This setup will create script ``myproject_run_task``, which will run your tasks.

Installation
------------

::

    pip install tasker

The current version is Python 3 only. Use version 0.1.2 for Python 2.7.

