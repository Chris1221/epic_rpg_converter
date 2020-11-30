from distutils.core import setup

setup(name='epic_convert',
      version='1.0',
      description='Convert between items in epic RPG',
      author='Chris Cole',
      author_email='chris.c.1221@gmail.com',
      packages=['epic_convert'],
      entry_points={
          'console_scripts': [
              'epic_convert = epic_convert:run',
              ],
          }
      )
