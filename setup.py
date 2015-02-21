import io
from distutils.core import setup


def long_description():
    with io.open('README.rst', encoding='utf8') as f:
        return f.read()

setup(
    name='tasker',
    version='0.1.1',
    py_modules=['tasker'],
    url='https://github.com/s4g/tasker',
    license='MIT License',
    author='Vyacheslav Rafalskiy',
    author_email='rafalskiy@gmail.com',
    description='Run functions as scripts',
    long_description=long_description(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],

)
