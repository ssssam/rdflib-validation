# -*- encoding=utf8 -*-
# Copyright (C) 2015  Codethink Limited
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


import rdflib
import RDFClosure


class ValidationError(Exception):
    pass


# FIXME: these need to give useful messages when printed.

class DomainMismatch(ValidationError):
    pass


class RangeMismatch(ValidationError):
    pass


class DisjointClassMembership(ValidationError):
    pass


class UnknownClassError(ValidationError):
    pass


class UnknownPropertyError(ValidationError):
    pass


def validate(data, schema):
    '''Validate the contents of 'data' against 'schema'.

    FIXME: closed-world, ontology, blah.

    Returns a list of exception instances, all of which will be a subclass of
    ValidationError.

    '''
    assert isinstance(data, rdflib.Graph)
    assert isinstance(schema, rdflib.Graph)

    result = []
    result.extend(validate_object_properties(data, schema))

    return result


def expand_type_statements(data, schema):
    '''Return all explicit and implied rdf:type statements.

    Some type information will be explicitly defined in the input data. But
    usually there is more information that is implied by rdf:subClassOf
    statements in the schema, but not explicitly stated.

    Using the 'RDFClosure' OWL-RL reasoner we can generate a new graph which
    contains both the explicit and the implied rdf:type statements, then return
    a new graph containing all this information.

    Here is an example of a schema and some data:

        :Animal a owl:Class.
        :Monkey a owl:Class ;
            rdfs:subClassOf :Animal.

        :pequeño a :Monkey .

    Given that example, this function would return the following graph:

        :pequeño a :Animal .
        :pequeño a :Monkey .

    '''
    # Since 'data' may be huge, put the rdf:type statements into their own
    # graph first, and run the reasoner across that.
    type_statements_with_schema = rdflib.Graph()

    # FIXME: creating subgraphs in RDFLib is a real pain, unless I'm missing
    # something.

    for subject, object in data[:rdflib.RDF.type:]:
        type_statements_with_schema.add((subject, rdflib.RDF.type, object))

    # FIXME: maybe we should just add the rdf:subClassOf statements from
    # the schema?
    for statement in schema[::]:
        type_statements_with_schema.add(statement)

    reasoner = RDFClosure.DeductiveClosure(
        closure_class=RDFClosure.RDFS_OWLRL_Semantics,
        rdfs_closure=True)
    reasoner.expand(type_statements_with_schema)

    type_statements = rdflib.Graph()
    for subject, object in type_statements_with_schema[:rdflib.RDF.type:]:
        type_statements.add((subject, rdflib.RDF.type, object))

    return type_statements


def validate_object_properties(data, schema):
    result = []

    all_type_statements = expand_type_statements(data, schema)

    # Find all owl:ObjectProperty instances.
    #  - that's not easy because you might have a subproperty of
    #    an owl:ObjectProperty that doesn't specify its own
    #    domain and range restrictions but inherits those from
    #    its parent.

    properties = schema[:rdflib.RDF.type:rdflib.OWL.ObjectProperty]
    # Find every triple that specifies that property.
    for prop in properties:
        prop_range = set(schema[prop:rdflib.RDFS.range:])
        prop_domain = set(schema[prop:rdflib.RDFS.domain:])

        # FIXME: what if there is no range or domain defined?

        subject_object_pairs = data[:prop:]
        for resource, value in subject_object_pairs:
            resource_classes = set(
                all_type_statements[resource:rdflib.RDF.type:])
            value_classes = set(
                all_type_statements[value:rdflib.RDF.type:])

            if not prop_domain.intersection(resource_classes):
                print '%s not in %s' % (resource_classes, prop_domain)
                print 'intersection: %s' % prop_domain.intersection(resource_classes)
                result.append(DomainMismatch())
            if not prop_range.intersection(value_classes):
                result.append(RangeMismatch())

    return result
