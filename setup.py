from setuptools import setup

classifiers = ["Development Status :: 4 - Beta",
               "License :: OSI Approved :: Apache Software License"]

setup(name='dictime',
      version='0.0.2',
      description="Dictionary with the dimension of time",
      long_description="",
      classifiers=classifiers,
      keywords='dict list expire future cache',
      author='@stevepeak',
      author_email='steve@stevepeak.net',
      url='https://github.com/stevepeak/dictime',
      license='Apache v2',
      packages=["dictime"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points=None)
