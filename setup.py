from setuptools import setup, find_packages

setup(
    name='nbdev-mini',
    version='0.0.1',
    license='MIT',
    description='A minimal nbdev example focused on writing quarto extensions',
    long_description=open('README.md').read(),
    install_requires=[],
    keywords="quarto",
    url='https://github.com/muellerzr/nbdev-mini',
    author='Zachary Mueller',
    package_dir = {'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
)