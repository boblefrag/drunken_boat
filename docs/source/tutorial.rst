Tutorial
========

The inevitable blog example
___________________________

First, install `drunken-boat` see :doc:`install`. Once drunken_boat
installed you can boostrap your first application with::

     drunken_run.py bootstrap example_blog

This will create for you all you need to start::

    cd /home/yohann/Dev/drunken_boat/example_blog
    python application.py

then visit http://localhost:5000/

If everything is fine you should see a bare "Hello World!" This it a
first victory but there is much more to do.


Database management
-------------------

Drunken Boat is focused on performances. Most of current applications
lack performances due to ORM. Yes ORM are great when you need Object
Oriented programation but they lack a lot of features you can find in
modern database like PostgreSQL.

Drunken Boat want to help you write powerful applications where you
can use the most of your database.

This is the reason why Drunken Boat does not force you to create your
database nor managing table schema in his ORM. Sure it gives you some
helpful methods and functions to create database, schema, make ALTER
TABLE on your databases but it's absolutely up to you to manage them
the way you like.


Projections
-----------

Projections are the object based representation of the `result` of a
database query. See them as what you expect from the database.

Let say you make this query::

  select name, age(birthdate) from user;

the corresponding projection will just fit::

  class UserNameAge(Projection):
      name = CharField()
      age = Timestamp(name="age(birthdate)")

      class Meta:
          table = "user"

  projection = UserNameAge(DB(**connection_params))


And you can get your results as easily as::

  >> users = projection.select()
  >> users[0].age
  datetime.timedelta(13850, 50160)

results are list of `DataBaseObject`. because DataBaseObject are
objects, you can attach any method you want on it. For example::

  from drunken_boat.db.postgresql.fields import Timestamp
  from drunken_boat.db.postgresql.projections import (Projection,
                                                      DataBaseObject)
  class ExampleDataBaseObject(DataBaseObject):

      def display_birthyear_and_days(self):
          days = self.age.days
          year = self.birthdate.year
          return "{} days since {}".format(days, year)

  class ExampleProjection(Projection):
      """
      Here you can write your real projections
      """

      age = Timestamp(db_name="age(birthday)", virtual=True)
      birthdate = Timestamp()

      class Meta:
          table = "test"
          database_object = ExampleDataBaseObject

  example_projection = ExampleProjection(DB(**DATABASE))


  >>> from projections import example_projection
  >>> t = example_projection.select()
  >>> t[0].display_birthyear_and_days()
  '13850 days since 1977'
