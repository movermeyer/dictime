from setuptools import setup

version = '0.0.1'

setup(name='suite',
      version=version,
      description="A better dictionary.",
      long_description="""\
A set of things that belong together and methods to control those items.
""",
      classifiers=[],
      keywords='',
      author='@iopeak',
      author_email='steve@stevepeak.net',
      url='https://github.com/stevepeak/suite',
      license='Apache v2',
      packages=["suite"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
