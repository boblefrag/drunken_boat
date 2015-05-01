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


Returning
_________

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


Foreignkey
----------

When you need to manage relation between objects (ForeignKey), you
will need a way to tell the Database wich fields of the related table
you want to retreive. You will also need to tell the database how to
handle the relation. Of course with projections it's really easy to
do.


Of course you need to create the tables in your database. For this
purpose you can use something like this::

  db = DB(**DATABASE)
  cur = db.cursor()
  cur.execute(
  """CREATE TABLE author (id serial PRIMARY KEY,
                          first_name = varchar(250) NOT NULL,
                          last_name = varchar(250) NOT NULL)
  """)
  db.conn.commit()
  cur.execute(
  """CREATE TABLE blog_post (id serial PRIMARY KEY,
                             title varchar(250),
                             introduction text,
                             body text,
                             created_at timestamp default now(),
                             last_edited_at default now(),
                             author_id integer NOT NULL,
                             published boolean default False)
  """)
  db.conn.commit()
  cur.execute(
  "alter table blog_post add foreign key(author_id)
  references author"
  )
  db.conn.commit()

Then you can create two new projections::


  class AuthorProjection(Projection):
      first_name = CharField()
      last_name = CharField()
      birthdate = Timestamp()

      class Meta:
          table = "author"

  author_projection = AuthorProjection(DB(**DATABASE))

  class PostProjection(Projection):
      title = CharField()
      introduction = Text()
      body = Text()
      created_at = Timestamp()
      last_edited_at = Timestamp()
      author = ForeignKey(join=["author_id", "id"],
                          projection=AuthorProjection)
      published = Boolean()

      class Meta:
          table = "blog_post"

  post_projection = PostProjection(DB(**DATABASE))

`ForeignKey` take two mandatory parameters, join and projection.

- join: This is a list of 2 elements. First element is the field on
        the table you're working on. Second element is the field on
        the related table.

- projection:: The projection to use to render the field.

Usage of projections with foreignkeys are straitforward::

  >>> from projections import post_projection
  >>> post = post_projection.select()[0]
  >>> post.__dict__
  {'author': <drunken_boat.db.postgresql.projections.DataBaseObject at 0x7f7170187490>,
   'body': None,
   'created_at': datetime.datetime(2015, 5, 1, 17, 18, 20, 95226),
   'introduction': 'Pouet Pouet PimPim',
   'last_edited_at': datetime.datetime(2015, 5, 1, 17, 18, 20, 95226),
   'published': False,
   'title': 'hello'}
  >>> post.author.__dict__
  {'birthdate': None, 'first_name': 'Paul', 'last_name': 'Eluard'}
