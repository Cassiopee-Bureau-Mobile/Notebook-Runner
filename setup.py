from setuptools import setup, find_packages

setup(
    name="notebook_runner",
    version="0.1.1",
    
    url="https://github.com/SamuelGuillemet/Cassiopee",
    author="Samuel Guillemet",
    
    packages=find_packages(),
    entry_points={'console_scripts': ['notebook_runner = notebook_runner.__main__:notebook_runner']},
    
    install_requires=[
        "nbformat",
        "jupyter",
        "nbconvert",
        "alive_progress",
        "rich"]
)
