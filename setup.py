import khbr
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
	name = 'khbr',
	packages = find_packages(),
	package_data={'': ['KH2/data/**', 'KH2/data/ai_mods/**']},
	version = '2.0',
	long_description = long_description,
	long_description_content_type='text/markdown',
	license = 'MIT',
	author = 'Thundrio',
	author_email= 'thundrio@yahoo.com',
	maintainer_email = 'thundrio@yahoo.com',
	url = 'https://github.com/thundrio-kh/khbr',
	classifiers = [
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3"
	],
	install_requires=[
        'PyYAML',
    ],
	platforms = 'any'
)