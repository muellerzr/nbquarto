from setuptools import setup, find_packages

extras = {}
extras["quality"] = ["black ~= 23.1", "ruff >= 0.0.241"]
extras["testing"] = ["pytest"] + extras["quality"]

setup(
    name='nbquarto',
    version='0.0.1',
    license='MIT',
    description='A minimal nbdev version, focused on writing quarto extensions',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=["pyyaml", "hf-doc-builder~=0.4.0"],
    extras_require=extras,
    keywords="quarto",
    url='https://github.com/muellerzr/nbquarto',
    author='Zachary Mueller',
    package_dir = {'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "nbquarto-process = nbquarto.cli:main"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
)