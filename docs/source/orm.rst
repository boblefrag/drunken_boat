A word about Projections
------------------------

It's common in the ORM world to write your tables schema in your
python code. This cause majors issues.

First of the is duplication. Your schema is in your database AND in
your python code. Every time one chage, the other has to change.

Second is static schema. Database are not bound to a schema, they are
bound to projections. Here is an example, let say you have this
database schema:

Table « public.bookstore_store »

 id          | integer                | not NULL default, nextval('bookstore_store_id_seq'::regclass)
 name        | character varying(250) | not NULL
 close_time  | integer                | not NULL
 open_time   | integer                | not NULL
 open_date   | date                   | not NULL
 location_id | integer                | not NULL


 id      | integer                | not NULL default, nextval('bookstore_location_id_seq'::regclass)
 name    | character varying(250) | non NULL


a store object will always have the representation ::

  Store:
      id
      name
      close_time
      open_time
      open_date
      location_id

Let say you only need the `name` and the `location name` you will
write something like::

  for store in stores:
      store.name
      store.location.name  # Your ORM without telling you anything
                           # will make a query on location for each
                           # store

In Django for example, you will need to specify a select_related
argument to your query to retreive location.name when querying the
store table. You can't get only the store.name and the location.name
without loosing the objects paradigm (or using the "only" parameter
wich will not raise anything but make a query for each field you forget)

Because database can manage this in an admirable manner, and much
more, we decide to create a schemaless ORM without breaking the Object
Oriented paradigm. Seems interesting? Let's take the ride!


