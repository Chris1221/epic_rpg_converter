from distutils.core import setup

setup(name='epic_rpg_convert',
      version='1.0',
      description='Convert between items in epic RPG',
      author='Chris Cole',
      author_email='chris.c.1221@gmail.com',
      packages=['epic_rpg_convert'],
      install_requires = [
        'discord.py==1.5.1',
        'numpy==1.18.1',
        'python-dotenv',
        'psycopg2>2.8',
        'networkx>2.0'],
      entry_points={
          'console_scripts': [
              'convert_bot = epic_rpg_convert:run',
              ],
          }
      )
