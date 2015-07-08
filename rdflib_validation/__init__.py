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


class ValidationError(Exception):
    pass


# FIXME: these need to give useful messages when printed.

class DomainMismatch(ValidationError):
    pass


class RangeMismatch(ValidationError):
    pass


class DisjointClassMembership(ValidationError):
    pass


def validate_object_properties(data, schema):
    result = []

    # Find all owl:ObjectProperty instances.
    #  - that's not easy because you might have a subproperty of
    #    an owl:ObjectProperty that doesn't specify its own
    #    domain and range restrictions but inherits those from
    #    its parent.
    #  - maybe rdflib/owl-rl can help here?
    #       - try it!
    properties = schema[:rdflib.RDF.type:rdflib.OWL.ObjectProperty]
    # Find every triple that specifies that property.
    for prop in properties:
        prop_range = schema[prop:rdflib.RDFS.range:]
        prop_domain = schema[prop:rdflib.RDFS.domain:]

        # FIXME: what if there is no range or domain defined?

        subject_object_pairs = data[:prop:]
        for resource, value in subject_object_pairs:
            if resource not in prop_range:
                result.append(RangeMismatch())
            if value not in prop_domain:
                result.append(DomainMismatch())

        print list(subject_object_pairs)
    # Check the domain and range.

    return result


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
