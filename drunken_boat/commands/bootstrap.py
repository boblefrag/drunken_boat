import sys
import os
from jinja2 import Template
from drunken_boat.commands import BaseCommand


class Command(BaseCommand):
    help = """Create a bootstrap project in the working directory
must be called with the project name as first argument

    drunken_run.py bootstrap example_project

This will create a new directory named example_project in {} with base
file structure to start working:

example_project/
-- __init__.py
-- application.py
-- router.py
-- views.py
-- projection.py
""".format(os.getcwd())

    def execute(self, argv):
        if len(argv) < 3:
            self.get_help()
        else:
            self.projet_name = argv[2]
            self.project_root = os.path.join(os.getcwd(), argv[2])
            os.mkdir(os.path.join(os.getcwd(), argv[2]))
            for tmpl in ["application", "router",
                         "views", "__init__",
                         "config", "projections"]:
                self.create_template(tmpl)
            sys.stdout.write("""project {} initialized.
To start your application:

cd {}
python application.py
then visit localhost:5000/
""".format(self.projet_name, self.project_root))

    def create_template(self, module):
        with open(
                os.path.join(
                    os.path.dirname(__file__),
                    "templates",
                    "bootstrap",
                    "{}.txt".format(module)
                )) as template:
                tmpl = Template(template.read())
                f = open(
                    os.path.join(self.project_root,
                                 "{}.py".format(module)), "w")
                f.write(tmpl.render(project_name=self.projet_name))
                f.close()
