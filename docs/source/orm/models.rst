Models: database management the easy way
========================================

Basicaly Models are simply a thin layer on top of `Projections` see
:doc:`database` for a full documentation on `Projections`. With
models, on can easily create, update and delete database objects using
a clear syntax.

Of course you also get all the power of `Projections` when you need them.


Initialize
----------

To create a model, you need at least a `Database` and a `Projection`
A basic projection can be something like::

    from drunken_boat.db.postgresql.projections import Projection

    class ExampleProjection(Projection):
        """
        A basic projection
        """
        age = Timestamp(db_name="age(birthday)", virtual=True)
        birthday = Timestamp()

        class Meta:
            table = "test"


The underlying database table can be something like::

  Table : test

    id serial PRIMARY KEY,
    num integer NOT NULL,
    data varchar NOT NULL,
    birthday timestamp

you can now import your database configuration::

  from example_blog.config import DATABASE
  from drunken_boat.db.postgresql import DB

  db = DB(**DATABASE)

You are now ready to use the `Models` API::

  from drunken_boat.db.postgresql.models import Model
  my_model = Model(db, projections={"example": ExampleProjection})

Manipulation of Model objects
-----------------------------


With a `Model` instance, you can request an object for creating data
in your database in a very pythonic way. To requert an object, just
do::

  obj = model.object()

Then you can set data on this object::

  obj.num = 10
  obj.data = "something"

And, of course save this object in the database::

  obj.save()

Once saved, the object can be updated::

  obj.num = 25
  obj.update()

Or deleted::

  obj.delete()

How things works
----------------

`Models` are nothing more than just a very thin layer around
`Projections` and database objets. When you create a Model with some
projections, we will look for a "default" projection. If this
projection does not exist, the first projection will be set as the
"default" one.

In order to implement update and delete on model object, we look for
the primary key on the "default" projection. If the primary key is not
on the projection, it will be automaticaly added when you call the
save() method of object.

After that, because we get the primary key of your object we are able
to update and delete the object using this pimary key.

All the projections you a model contains are available in
Model.projections. For example, to get the default projection you just
have to write::

  my_model.projections.default

If you do not want to use the default projection when requestiong a
Model object, you can ask for a particular projection::

  obj = my_model.object(projection=my_model.projections.other)

Using a projection you do not define in your model is absolutly ok
because there is no magic in how Model work::

  obj = my_model.object(projection=AnOtherProjection)

The only limit is that your projection **must** be on the same
table. (same primary key field)


Returning
---------

Because underlying projections offers returning on insert, update and
delete, Model objects offer this behavior too. Simply add the
returning argument to your save, update or delete method just like
with projections::

  obj.save(returning="title")
