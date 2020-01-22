#!/usr/bin/env python

import setuptools

setuptools.setup(name='sakstig',
      version='0.1.7',
      description='SakStig is an objectpath implementation that uses '
      'proper querysets and supports querying any python object that '
      'supports the dict or list interfaces.',
      author='Egil Moeller',
      author_email='egil@innovationgarage.no',
      url='https://github.com/innovationgarage/sakstig',
      packages=setuptools.find_packages(),
      install_requires=[
          "pyleri"
      ],
      include_package_data=True,
      entry_points='''
      [console_scripts]
      sakstig = sakstig:main
      sakstig-grammar = sakstig.grammar:main
      sakstig-ast = sakstig.ast:main
      sakform = sakform:main
      '''
  )
