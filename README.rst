Tasker
======

Tasker is a way to organize your scripts. If you have dozens of small scripts and you keep forgetting what they do and what parameters they take, **tasker** is for you. Instead of scripts you write functions, put them in a file or a couple of them, and then run the main tasker script giving them the task name and the parameters of the task like this:

::

    run_task <task-name> [<task-parameter>]...

The **help** task will scan your tasks package and give you the signatures and docstrings of your tasks.

To be considered as a task, the function name should end with ``_task``. The task name is the function name less the suffix. Suppose we have the following file stucture:

::

    run_task
    tasks/
        __init__.py
        moretasks.py

``__init__.py``

.. code-block:: python

    def one_task(p1):
        print 'in one_task, parameters:', p1

    def two_task(p1, p2):
        print 'in two_task, parameters:', p1, p2

and ``moretasks.py``

.. code-block:: python

    def t1_task(p1):
        print 'in t1_task, parameters:', p1

    def t2_task(p1, p2=None):
        print 'in t2_task, parameters:', p1, p2

Then we can run the following examples:

::

    run_task one foo
    run_task two foo baz
    run_task two foo               # fails, not enough parameters
    run_task moretasks.t1 spam
    run_task moretasks.t2 spam ham
    run_task moretasks.t2 spam     # works too because of default value of the second parameter

To generate the ``run_task`` script in the current directory run:

::

    python -m tasker <fully-qualified-name-of-tasks-package>  # default = "tasks"

IMPORTANT: All task parameters are strings.

You can include tasks with distribution of your project and run them all with a single installed script. Suppose your project looks like this:

::

    someproject/
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
            'someproject_task = someproject:run_task',
            ],
        }

This setup will create script ``someproject_task``, which will know about your tasks.

Installation
------------

::

    pip install tasker

Origin
------

This was inspired by the Ruby's ``rake`` utility. I used for some time the ``shovel``
python clone of ``rake`` until I got dissatisfied with it. The important difference of ``tasker``
(apart from simplicity) is that it does not depend on current working directory.
