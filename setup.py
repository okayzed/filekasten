from setuptools import setup

setup(
    name='filekasten',
    version='0.0.2',
    author='okay',
    author_email='okay.zed+jt@gmail.com',
    include_package_data=True,
    packages=['filekasten', 'filekasten.md_ext' ],
    scripts=['bin/filekasten'],
    url='http://github.com/okayzed/filekasten',
    license='MIT',
    description='a personal file note manager',
    long_description=open('README').read(),
    install_requires=[
        "flask",
        "peewee",
        "markdown-checklist",
        "Markdown",
        "Jinja2",
        "python-frontmatter",
        "babel",
        "flask_peewee",
        "addict",
        "pudgy",
    ],
    )

