Database Management
===================

Drunken Boat is focused on performances. Most of current applications
lack performances due to ORM. Yes ORM are great when you need Object
Oriented programation but they lack a lot of features you can find in
modern database like PostgreSQL.

Drunken Boat want to help you write powerful applications where you
can use the most of your database and still use Object Oriented programmation.

This is the reason why Drunken Boat does not force you to create your
database nor managing table schema in his ORM. Sure it gives you some
helpful methods and functions to create database, schema, make ALTER
TABLE on your databases but it's absolutely up to you to manage them
the way you like.

Configuration & Table creation
------------------------------

In the project created by drunken_run.py the file config.py contains
the base detail of a database connection. Change the DATABASE with
connection informations of your database.

Even if drunken_boat don't force you to create table from python, for
this tutorial you can use this simple script to generate the table you
will use in the next step::

  #projection.py
  from drunken_boat.db.postgresql import DB
  from example_blog.config import DATABASE

  def create_tables():
      db = DB(**DATABASE)
      cur = db.cursor()
      cur.execute(
          """select exists(
              select * from information_schema.tables where table_name=%s)
          """,
          ('test',))
      if not cur.fetchone()[0]:
          cur.execute("""CREATE TABLE test (
          id serial PRIMARY KEY,
          num integer,
          data varchar,
          birthday timestamp)""");
          db.conn.commit()
          print("table created")
          return
      print("table already exists")


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

  from drunken_boat.db.postgresql import DB
  from config import DATABASE
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


Where
-----

One thing you will surely do very often is to use `Projection` with
WHERE clause. Where clause are defined with 2 sides. First side is the
clause and the comparison operator, the other side is the parameter.

For example, in the statement:

WHERE id > 4;

id is the clause, > is the comparison operator, and 4 is the parameter.

The first an easier way to make a query with a WHERE clause is simply
adding where and parameter to the select statement::

  >>> projection.select(where='id=%s', params=(1,))

If it's perfectly ok to do so, but sometimes you will need to store a
WHERE clause to use it in many places in your code. For this the Where
object is here to help you.

A where object take a clause, an operator and a value::

  from drunken_boat.db.postgresql.query import Where
  where = Where("id", "=", "%s")

As you can see a Where object is very similar to the select
version. The difference is that you do not define a parameter yet. The
parameter will be define when calling the select method of your
`Projection`::

  >>> projection.select(where=where, params=(1,))


Multiple Where
______________

It's also possible to use multiple where in a single select using
biwise operations. AND, OR and NOT are supported:

AND::

  >>> where = Where("id", "=", "%s") & Where("title", "=", "%s")

OR::

  >>> where = Where("id", "=", "%s") | Where("title", "=", "%s")

NOT::

  >>> where = Where("id", "=", "%s") & ~Where("title", "=", "%s")

NOT can be used as is to make exclude clause::

  >>> where = ~Where("title", "=", "%s")

You can also define priorities with parenthesis::

  >>> where = Where("id", "=", "%s") | (Where("title", "=", "%s") & Where("intro", "=", "%s"))

this will be rendered as::

  id = %s OR (title = %s AND intro = %s)

Insert
------

Even if you do not describe the table schema of your tables,
drunken_boat introspect your table schema to give you automatic
validation of data before even hitting the database.

To demonstrate this behavior let's create another table::

  Table : test

    id serial PRIMARY KEY,
    num integer NOT NULL,
    data varchar NOT NULL,
    birthday timestamp

And another projection::

    class ExampleProjection(Projection):
        """
        Here you can write your real projections
        """
        age = Timestamp(db_name="age(birthday)", virtual=True)
        birthday = Timestamp()

        class Meta:
            table = "test"
            database_object = ExampleDataBaseObject

    example_projection = ExampleProjection(DB(**DATABASE))

Now, with a shell try to insert some data in the table::

  >>> from projections import example_projection
  >>> example_projection.insert({"birthday": datetime.datetime.now()})
  ValueError: num of type integer is required
  data of type character varying is required

Now that you know wich data you must use to insert data you can type::

  >>> example_projection.insert({"num": 10,
  ...                            "data": "some data"})

You can check that your record is saved in the database::

  >>> example_projection.select()
  ... [<projections.DataBaseObject at 0x7f2ac0447c10>]

.. _returning:

Returning
---------

You can feel a bit disturbing to do not have a hint on what's the
result of your insert. If you want to get results, you can use
`returning` parameter to get a result from the database::

  >>> example_projection.insert({"num": 10,
  ...                            "data": "some data"},
  ...                           returning="id, num, data")
  (6, 10, 'some data')

Last but not least, you can even ask drunken_boat to return the object
corresponding to the projection you actually use::

  >>> import datetime
  >>> obj = example_projection.insert(
  ...                       {"data": "hello",
  ...                        "num": "6",
  ...                        "birthday": datetime.datetime.now()},
  ...                       returning="self")
  >>> obj.age
  datetime.timedelta(-1, 33857, 32595)
  >>> obj.birthday
  datetime.datetime(2015, 5, 1, 14, 35, 42, 967405)


Update
------

Updating is similar o insert but the main difference is that when you
commonly insert a single row, when you update a table, you can update
a lot of rows in a single query on the database.

To reflect this, the syntax of update is where clause, updated column
and parameters for the where. For example, if you want to change all
the example_projection object where data is "hello" to goodbye, you
will write::

  >>> example_projection.update("data=%s", {"data": "goodbye"}, ("hello",))

obviously you can use a Where object to make things more readable:

  >>> example_projection.update(Where("data", "=" "%s"),
  ...    {"data": "goodbye"}, ("hello",))

Last bt not least, like with insert you can ask the database for
returning::

  >>> example_projection.update(Where("data", "=" "%s"),
  ...    {"data": "goodbye"}, ("hello",), returning="id, num, data")

or

  >>> example_projection.update(Where("data", "=" "%s"),
  ...    {"data": "goodbye"}, ("hello",), returning="self")


Delete
------

With delete, you do not need to specify what will be changed. So the
api of delete is like update but without changing columns::

  >>> example_projection.delete(Where("data", "=" "%s"),("hello",))

Like for `update` and `insert` you can use `returning` on delete::

  >>> example_projection.delete(Where("data", "=" "%s"),("hello",),
  ...    returning="self")
