# -*- coding: utf-8 -*-
"""
    Configuration

    A sphinx config generator for Tryton

    :copyright: (c) 2011 by Douglas Morato
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL
from trytond.config import CONFIG
from jinja2 import Environment

from utils import guess_type


class XMLSource(object):
    """Sphinx needs to invoke xmlpipe stream producer in order index data
    incoming from strem

    :param name: Name of the source and index in sphinx.conf
    :param command: Shell command to invoke xmlpipe stream producer.
    :param fields: List of field names for full text indexing.
    :param attributes: A :class:`dict` of fiueld names as keys and type as
                       values eg. {'name': 'xmlpipe_attr_uint'}
    """
    fields = []
    attributes = dict()

    def __init__(self, name, command, fields=None, attributes=None):
        self.name = name
        self.command = command
        if fields is not None:
            self.fields = fields
        if attributes is not None:
            self.attributes = attributes

    @classmethod
    def from_model(cls, database_name, model_object):
        """Creates and returns an XMLPIPE2 data source

        :param database_name: The name of tryton database to index data from
        :param model_obj: The instance of a model as obtained from
                          `trytond.pool.Pool`
        """
        # TODO: Morphology
        # TODO: An indexer for each language ???
        command = 'xmlpipe2_trytond %s %s %s' % (
            CONFIG.configfile, database_name, model_object._name)
        return cls(model_object._table, command)

    def as_string(self):
        """Returns the string representation of the confis as it has to appear
        in the sphinx config"""
        template = Environment().from_string("""
source {{cls.name}}
{
    type                =   xmlpipe
    xmlpipe_command     =   {{ cls.command }}

    {% for attr_name, attr_type in cls.attributes %}
    {{ attr_type }}     =   {{ attr_name }}
    {% endfor %}

    {% for name in cls.fields %}
    xmlpipe_field       =   {{ name }}
    {% endfor %}
}

index {{cls.name}}
{
    source              =   {{ cls.name }}
    path                =   {{config.options['data_path']}}/sphinx/{{cls.name}}
}
        """)
        return template.render(cls=self, config=CONFIG)


class BaseSQLSource(object):
    """Sphinx allows inheritance in data sources. having the SQL settings for
    each model object would be too redundant since the only changing attributes
    are the SQL query itself and the various attributes.
    """

    #: Name of a data source needs to be unique and the best way seems to be to
    #: resuse the _table attribute of tryton which is guaranteed to exists and
    #: be unique for every model that has a database representation (in other
    #: words every object other than wizards and reports).
    #:
    #: For the Base Source this defaults to `base_source` and any
    #: :class:`SQLDataSource` which inherits from :class:`BaseSQLSource` will use the
    #: settings from this instance
    name = 'base_source'

    #: data source type. mandatory, no default value. The possible types are
    #: mysql, pgsql and this can be inferred from the config
    type = None

    #: All the following database settings (except :attr:`db`) can be obtained
    #: from `trytond.config`.
    sql_host = None
    sql_user = None
    sql_pass = None
    sql_db = None
    sql_port = None


    @classmethod
    def from_tryton_config(cls, database_name):
        """Creates a :class:`BaseSQLSource` from the current tryton configuration
        in the environment.

        :param database_name: The database name to use in the database source.
                              Equivalent to setting :attr:`sql_db`
        """
        self = cls()

        self.type = {
            'postgresql': 'pgsql',
            'mysql': 'mysql',
            }.get(CONFIG.options['db_type'])
        self.sql_host = CONFIG.options['db_host']
        self.sql_port = CONFIG.options['db_port']

        self.sql_user = CONFIG.options['db_user']
        self.sql_pass = CONFIG.options['db_password']

        self.sql_db = database_name

        return self

    def as_string(self):
        """Returns the string representation of the config as it has to appear
        int he sphinx.conf
        """
        template = Environment().from_string("""
source {{name}}
{
    # data source type. mandatory, no default value
    # known types are mysql, pgsql, mssql, xmlpipe, xmlpipe2, odbc
    type        = {{type}}

    sql_host    = {{sql_host}}
    sql_user    = {{sql_user}}
    sql_pass    = {{sql_pass}}
    sql_db      = {{sql_db}}
    sql_port    = {{sql_port}}

    }
        """)
        return template.render(
            name=self.name,
            type=self.type,
            sql_host=self.sql_host,
            sql_user=self.sql_user,
            sql_pass=self.sql_pass,
            sql_db=self.sql_db,
            sql_port=self.sql_port
            )


class SQLDataSource(object):
    """This class represents a `sphinx data source
    <http://sphinxsearch.com/docs/2.0.1/sources.html>`_.

    The data to be indexed can generally come from very different sources:
    SQL databases, plain text files, HTML files, mailboxes, and so on. From
    Sphinx point of view, the data it indexes is a set of structured documents,
    each of which has the same set of fields. This is biased towards SQL, where
    each row correspond to a document, and each column to a field.

    Int he case of tryton the data source basically represents a combination of
    the database backend (name and credentials), a `ModelSQL <>`_ object and
    its `_table` representation.


    The possible arguments are:

    `name`: Name of a data source. (needs to be unique)
            .. tip::
                the best way seems to be to resuse the _table attribute of
                tryton which is guaranteed to exists and be unique for every
                model that has a database representation (in other words every
                object other than wizards and reports)

    `sql_query`: The main document fetch query.
    `attributes`: A :class:`dict` of field names as keys and type as values
                  eg {'name': 'sql_field_string'}
    `sql_query_range` : Range query setup, query that must return min and max
                        ID values optional, default is empty
    `sql_range_step`: Range query step (Default: 1024)
    """


    def __init__(self, name, sql_query, attributes,
            sql_query_range=None, sql_range_step=1024):
        self.name = name
        self.sql_query = sql_query
        self.attributes = attributes
        self.sql_query_range = sql_query_range
        self.sql_range_step = sql_range_step

    @classmethod
    def from_model(cls, model_object, base_source = None):
        """Creates and returns a new data source from a given model

        :param model_object: The instance of a model as obtained from the
                             `trytond.pool.Pool`
        :param base_source: The base_source to inherit from. Must be an
                            instance of :class:`BaseSQLSource`
        """
        assert isinstance(model_object, ModelSQL), \
            "model_object must be an instance of ModelSQL"
        if base_source:
            assert isinstance(base_source, BaseSQLSource), \
                "base_source must be an instance of BaseSQLSource (got %s)" % type(
                    base_source)

        attributes = {}
        for name, field in model_object._columns.iteritems():
            if field.select != 1:
                continue
            try:
                attributes[name] = guess_type(field)
            except ValueError:
                # Ignore if a value error is raised because its a field which
                # sphinx doesnt know the proper type for conversion
                continue

        sql_query = ""
        sql_query_range = 'SELECT MIN(id),MAX(id) FROM "%s"' \
            % model_object._table

        if attributes:
            # Construct the SQL query if attributes do exist
            sql_query = ['SELECT "%s"."id" AS "id",' % model_object._table]
            sql_query.append(", ".join([
                '"%s"."%s" AS "%s"' % (model_object._table, name, name) \
                    for name in attributes.keys()
                ]))
            sql_query.append('FROM "%s"' % model_object._table)
            sql_query.extend([
                'WHERE',
                '"%s"."id" >= $start' % model_object._table,
                'AND',
                '"%s"."id" <= $end' % model_object._table,
                ])

        # Build the data source name
        data_source_name = model_object._table
        if base_source:
            data_source_name = "%s : %s" % (data_source_name, base_source.name)

        # Create a new instance of Data Source with the data we have
        return cls(
            name = data_source_name,
            sql_query = ' '.join(sql_query),
            attributes = attributes,
            sql_query_range = sql_query_range,
            )

    def as_string(self):
        """Returns the string representation of the config as it has to appear
        in the sphinx.conf
        """
        # TODO: Morphology
        # TODO: An indexer for each language ???
        # TODO: Check the realtime indexing
        template = Environment().from_string("""
source {{cls.name}}
{
    sql_query           = {{cls.sql_query}}

    {% if cls.sql_query_range %}
    sql_query_range     = {{cls.sql_query_range}}
    sql_range_step      = {{cls.sql_range_step}}
    {% endif %}

    {% for attr_name, attr_type in cls.attributes.iteritems() %}
    {{attr_type}}       = {{attr_name}}
    {% endfor %}
    }

{% set name_without_parent = cls.name.split(':')[0] %}

index {{name_without_parent}}
{
    source              = {{name_without_parent}}
    path                = {{config.options['data_path']}}/sphinx/{{name_without_parent}}
    charset_type        = utf-8
    }
        """)
        return template.render(cls=self, config=CONFIG)
