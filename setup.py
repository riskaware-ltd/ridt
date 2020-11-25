from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ridt',
    version='1.1.2',
    author="Riskaware Ltd",
    packages=find_packages(),
    description="Rapid Indoor Diffusion Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riskaware-ltd/ridt",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'click',
        'numpy==1.16.5',
        'scipy',
        'matplotlib',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        ridt=ridt.cli.ridt:ridt
    ''',
)
