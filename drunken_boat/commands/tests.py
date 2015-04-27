import os
import sys
from StringIO import StringIO
from shutil import rmtree
from drunken_boat.commands import UtilCommand
from drunken_boat.commands.bootstrap import Command
from drunken_boat.bin import drunken_run


def test_bootstrap():
    argvs = [os.path.abspath(drunken_run.__file__)]
    command = UtilCommand(argvs)
    assert command.execute() == None
    argvs.append("bootstrap")
    command_result = StringIO()
    expected_result = StringIO()
    sys.stdout = command_result
    command.execute()
    sys.stdout = expected_result
    Command().get_help()
    assert command_result.getvalue() == expected_result.getvalue()
    argvs.append("dummy_project")
    assert command.execute() == None
    root_path = os.path.join(os.getcwd(), "dummy_project")
    assert os.path.exists(root_path)
    for path in ["application", "router", "views", "__init__"]:
        assert os.path.exists(os.path.join(root_path))

    from dummy_project import application
    assert application
    rmtree(root_path)
