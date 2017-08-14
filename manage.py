import unittest

from flask_script import Manager
from flask_migrate import MigrateCommand

from bucketlist.app import app

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """automated test run"""
    tests = unittest.TestLoader().discover('./bucketlist/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == "__main__":
    manager.run()
