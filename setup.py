from setuptools import setup

setup(name='ARCTIC',
      version='0.1.beta',
      description='A python package for analyzing and displaying solar panel data.',
      url='https://github.com/acep-solar/ACEP_solar',
      author='ARCTIC Development Team, University of Washington (2019)',
      license='MIT',
      packages=['ARCTIC'],
      install_requires=['numpy', 'Folium', 'bokeh', 'pandas', 'scikit-learn', 'h5py'])
