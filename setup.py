from setuptools import setup, find_packages

setup(
    name='idmf',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'numpy',
        'matplotlib',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        idmf=cli.idmf:idmf
    ''',
)