import os
from shutil import rmtree
from drunken_boat import commands
from drunken_boat.commands.bootstrap import Command
from drunken_boat.bin import drunken_run


def test_bootstrap():
    argvs = [os.path.abspath(drunken_run.__file__)]
    command = commands.UtilCommand(argvs)
    assert Command().execute(argvs) is None
    assert commands.run_command(argvs) is None
    assert command.execute() is None
    argvs.append("bootstrap")
    assert command.execute() is None
    argvs.append("dummy_project")
    assert command.execute() is None
    root_path = os.path.join(os.getcwd(), "dummy_project")
    assert os.path.exists(root_path)
    for path in ["application", "router", "views", "__init__",
                 "config", "projections"]:
        assert os.path.exists(os.path.join(root_path))

    from dummy_project import application
    assert application
    rmtree(root_path)
