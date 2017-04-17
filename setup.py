from setuptools import setup

setup(name='tagxon',
      use_vcs_version=True,
      description='Parser for a hideous yet powerful taxonomic description syntax',
      url='http://github.com/matt-hayden/tagxon',
	  maintainer="Matt Hayden",
	  maintainer_email="github.com/matt-hayden",
      license='Unlicense',
      packages=find_packages(),
	  entry_points = {
	    'console_scripts': ['tagxon=tagxon.cli:main'],
	  },
      install_requires=[
		"tqdm >= 4.10",
      ],
      zip_safe=True,
	  setup_requires = [ "setuptools_git >= 1.2", ]
     )
