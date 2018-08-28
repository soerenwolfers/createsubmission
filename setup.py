from setuptools import setup, find_packages

setup(
    name='createsubmission',
    version='1.0',
    url = 'https://bitbucket.org/soerenwolfers/createsubmission',
    python_requires='>=3.6',
    long_description=open('README.rst').read(),
    description='Create publication-ready zip file from LaTeX directory',
    author='Soeren Wolfers',
    author_email='soeren.wolfers@gmail.com',
    packages=find_packages(exclude=['*tests']),
    install_requires=['swutil'],
    scripts=['createsubmission.py'],
)

