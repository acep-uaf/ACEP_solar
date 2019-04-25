from setuptools import setup

setup(name='SolarAlaska',
      version='0.1.beta',
      description='A python package for analyzing and displaying solar panel data.',
      url='https://github.com/acep-solar/ACEP_solar',
      author='ACEP Solar Development Team, University of Washington (2019)',
      license='MIT',
      packages=['SolarAlaska'],
      install_requires=['numpy', 'Folium', 'matplotlib', 'pandas'])
