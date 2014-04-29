from setuptools import setup

classifiers = ["Development Status :: 4 - Beta",
               "License :: OSI Approved :: Apache Software License"]

with open('requirements.txt') as f:
    install_requires = f.readlines()

setup(name='suite',
      version='0.2.0',
      description="Time sensitive dictionary and library",
      long_description="""A lightweight extended dict to manage 
future/expiring assets and relationships between dictionarys""",
      classifiers=classifiers,
      keywords='dict list expire future cache',
      author='@stevepeak',
      author_email='steve@stevepeak.net',
      url='https://github.com/stevepeak/suite',
      license='Apache v2',
      packages=["suite"],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points=None)
