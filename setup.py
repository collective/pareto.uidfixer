from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='pareto.uidfixer',
      version=version,
      description="Find relative hrefs and img src attributes in HTML fields, and replace then with resolveuid ones.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          ],
      keywords='pareto.uidfixer html tool admin',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='http://github.com/zestsoftware/pareto.uidfixer/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pareto'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
