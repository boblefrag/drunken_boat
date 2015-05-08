Relations
=========


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


ReverseForeignkey
-----------------

Another cas you will encounter a lot is when you want to reverse the
relation. In our example, this can be :

How to get the authors with their corresponding posts ?

To solve this case we have to retreive all the posts belonging to one
of the author and then dispatch the posts to the corresponding author
representation.

`ReverseForeign` is a type of `Field` created for this job.

It need to know the related column on the "from" side and the related
column on the "to" side. Exactly the opposite of `ForeignKey`.

In our example we want all the post with an `author_id` equal to the
`author.id`.

We also need to tell `ReverseForeign` wich `Projection` to use for
rendering the posts. Here is an example::

  class PostProjectionRelated(Projection):
      title = CharField()
      introduction = Text()

      class Meta:
          table = "blog_post"

  post_projection_related = PostProjectionRelated(DB(**DATABASE))


  class AuthorProjectionWithPost(AuthorProjection):
      posts = ReverseForeign(join=["id", "author_id"],
                             projection=PostProjectionRelated)

  author_projection_with_post = AuthorProjectionWithPost(DB(**DATABASE))

`author_projection_with_post.select()` will return a list of Author
with the attribute posts containing all the posts of this author::

  >>> for author in author_projection_with_post.select():
  ...     print(author.id, [post.__dict__ for post in author.posts])
  1, [],
  2, [{"title": "a title", "introduction": "an introduction",
  "author_id": 2}, {"title": "another title", "introduction": "another
  introduction", "author_id":2 ] ...


If the first element of ReverseForeign.join is not in the projection,
(`id` in the example) it will be automaticaly added.

The same go for the ReverseForeign.projection wich will gain the
second part of ReverseForeign.join (`author_id` in the example).

This is the reason why we can get `author.id` even if `id` is not on the
`AuthorProjectionWithPost.fields` and `post.author_id` even if
`author_id` is not on `PostProjectionRelated.fields`

Filter reverse foreignkey
-------------------------

Sometimes getting the related objects is not enought and you will need
to filter the related objects.

To do so, `drunken_boat` offer a simple API. You only need to give to
the `select` method a related argument to hold every related fields
where and params::

  >>> projection = author_projection_with_post.select(
  ...     related={'posts':
  ...         'where': 'title=%s',
  ...         'params': ('a title')})
  >>> print post.__dict__ for post in projection[1].posts]
  [{"title": "a title", "introduction": "an introduction",
  "author_id": 2}]

Many To Many
------------

With `ReverseForeign` and `ForeignKey` you can already implement Many
to many relations. To do so, let say you have the following tables in
your database::

  CREATE TABLE product (
    id serial PRIMARY KEY
  , product    text NOT NULL
  , price      numeric NOT NULL DEFAULT 0
  );

  CREATE TABLE bill (
    id  serial PRIMARY KEY
  , bill     text NOT NULL
  , billdate date NOT NULL DEFAULT now()::date
  );

  CREATE TABLE bill_product (
    bill_id    int REFERENCES bill (bill_id) ON UPDATE CASCADE ON DELETE CASCADE
  , product_id int REFERENCES product (product_id) ON UPDATE CASCADE
  , amount     numeric NOT NULL DEFAULT 1
  , CONSTRAINT bill_product_pkey PRIMARY KEY (bill_id, product_id)
  );

You can then create the following projections::

  class Product(Projection):
      product = CharField()
      price = Integer()

      class Meta:
          table = "product"

  product_projection = Product(DB(**DATABASE))


  class BillProduct(Projection):
      product = ForeignKey(join=["product_id", "id"],
                           projection=Product)
      class Meta:
          table = "bill_product"

  productbill_projection = BillProduct(DB(**DATABASE))


  class Bill(Projection):
      bill = CharField()
      billdate = Timestamp()
      products = ReverseForeign(join=["id", "bill_id"],
                                projection=BillProduct)
      class Meta:
          table = "bill"

  bill_projection = Bill(DB(**DATABASE))

With a select on `bill_projection` you will retreive all the
`BillProduct` matching your select. `BillProduct` will then retreive
the corresponding `Product`. This will give you the following results::

  [
    {"bill": "<text>",
     "billdate": <a date>,
     "products": [
       {"product":
         {"product": <text>, "price": <a price>},
       {"product":
         {"product": <text>, "price": <a price>},
       ...
     ]
   ...
  ]

create a bill with product you need to create the corresponding
bill_product record. This can be done using :ref:`returning`::

  import datetime
  bill = bill_projection.insert(
      {"bill": "a bill",
       "billdate": datetime.datetime.now()
      }, returning="id")

  # because we use returning, bill is the bill.id of the object just
  # saved

  product = product_projection.insert(
      {"product": "screwdriver",
       "price": 10},
       returning="id"
      )

  productbill_projection.insert({"bill_id": bill, "product_id": product})
