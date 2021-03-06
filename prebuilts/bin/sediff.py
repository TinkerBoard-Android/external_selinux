#!/usr/bin/python
# Copyright 2015-2016, Tresys Technology, LLC
#
# This file is part of SETools.
#
# SETools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# SETools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SETools.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import print_function
import setools
import argparse
import sys
import logging
from itertools import chain

parser = argparse.ArgumentParser(
    description="SELinux policy semantic difference tool.",
    epilog="If no differences are selected, all differences will be printed.")
parser.add_argument("POLICY1", help="Path to the first SELinux policy to diff.", nargs=1)
parser.add_argument("POLICY2", help="Path to the second SELinux policy to diff.", nargs=1)
parser.add_argument("--version", action="version", version=setools.__version__)
parser.add_argument("--stats", action="store_true", help="Display only statistics.")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Print extra informational messages")
parser.add_argument("--debug", action="store_true", dest="debug", help="Enable debugging.")

comp = parser.add_argument_group("component differences")
comp.add_argument("--common", action="store_true", help="Print common differences")
comp.add_argument("-c", "--class", action="store_true", help="Print class differences",
                  dest="class_")
comp.add_argument("-t", "--type", action="store_true", help="Print type differences",
                  dest="type_")
comp.add_argument("-a", "--attribute", action="store_true", help="Print type attribute differences")
comp.add_argument("-r", "--role", action="store_true", help="Print role differences")
comp.add_argument("-u", "--user", action="store_true", help="Print user differences")
comp.add_argument("-b", "--bool", action="store_true", help="Print Boolean differences",
                  dest="bool_")
comp.add_argument("--sensitivity", action="store_true", help="Print MLS sensitivity differences")
comp.add_argument("--category", action="store_true", help="Print MLS category differences")
comp.add_argument("--level", action="store_true", help="Print MLS level definition differences")

terule = parser.add_argument_group("type enforcement rule differences")
terule.add_argument("-A", "--allow", action="store_true", help="Print allow rule differences")
terule.add_argument("--neverallow", action="store_true", help="Print neverallow rule differences")
terule.add_argument("--auditallow", action="store_true", help="Print auditallow rule differences")
terule.add_argument("--dontaudit", action="store_true", help="Print dontaudit rule differences")
terule.add_argument("-T", "--type_trans", action="store_true",
                    help="Print type_transition rule differences")
terule.add_argument("--type_change", action="store_true", help="Print type_change rule differences")
terule.add_argument("--type_member", action="store_true",
                    help="Print type_member rule differences")

rbacrule = parser.add_argument_group("RBAC rule differences")
rbacrule.add_argument("--role_allow", action="store_true", help="Print role allow rule differences")
rbacrule.add_argument("--role_trans", action="store_true",
                      help="Print role_transition rule differences")

mlsrule = parser.add_argument_group("MLS rule differences")
mlsrule.add_argument("--range_trans", action="store_true",
                     help="Print range_transition rule differences")

labeling = parser.add_argument_group("labeling statement differences")
labeling.add_argument("--initialsid", action="store_true", help="Print initial SID differences")
labeling.add_argument("--fs_use", action="store_true", help="Print fs_use_* differences")
labeling.add_argument("--genfscon", action="store_true", help="Print genfscon differences")
labeling.add_argument("--netifcon", action="store_true", help="Print netifcon differences")
labeling.add_argument("--nodecon", action="store_true", help="Print nodecon differences")
labeling.add_argument("--portcon", action="store_true", help="Print portcon differences")

other = parser.add_argument_group("other differences")
other.add_argument("--default", action="store_true", help="Print default_* differences")
other.add_argument("--property", action="store_true",
                   help="Print policy property differences (handle_unknown, version, MLS)")
other.add_argument("--polcap", action="store_true", help="Print policy capability differences")

args = parser.parse_args()

all_differences = not any((args.class_, args.common, args.type_, args.attribute, args.role,
                           args.user, args.bool_, args.sensitivity, args.category, args.level,
                           args.allow, args.neverallow, args.auditallow, args.dontaudit,
                           args.type_trans, args.type_change, args.type_member, args.role_allow,
                           args.role_trans, args.range_trans, args.initialsid, args.genfscon,
                           args.netifcon, args.nodecon, args.portcon, args.fs_use, args.polcap,
                           args.property, args.default))

if args.debug:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s|%(levelname)s|%(name)s|%(message)s')
elif args.verbose:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
else:
    logging.basicConfig(level=logging.WARNING, format='%(message)s')

try:
    p1 = setools.SELinuxPolicy(args.POLICY1[0])
    p2 = setools.SELinuxPolicy(args.POLICY2[0])
    diff = setools.PolicyDifference(p1, p2)

    if all_differences or args.property:
        print("Policy Properties ({0} Modified)".format(len(diff.modified_properties)))

        if diff.modified_properties and not args.stats:
            for name, added, removed in sorted(diff.modified_properties, key=lambda x: x.property):
                print("      * {0} +{1} -{2}".format(name, added, removed))

        print()

    if all_differences or args.common:
        if diff.added_commons or diff.removed_commons or diff.modified_commons or args.common:
            print("Commons ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_commons), len(diff.removed_commons), len(diff.modified_commons)))
            if diff.added_commons and not args.stats:
                print("   Added Commons: {0}".format(len(diff.added_commons)))
                for c in sorted(diff.added_commons):
                    print("      + {0}".format(c))
            if diff.removed_commons and not args.stats:
                print("   Removed Commons: {0}".format(len(diff.removed_commons)))
                for c in sorted(diff.removed_commons):
                    print("      - {0}".format(c))
            if diff.modified_commons and not args.stats:
                print("   Modified Commons: {0}".format(len(diff.modified_commons)))
                for name, mod in sorted(diff.modified_commons.items()):
                    change = []
                    if mod.added_perms:
                        change.append("{0} Added permissions".format(len(mod.added_perms)))
                    if mod.removed_perms:
                        change.append("{0} Removed permissions".format(len(mod.removed_perms)))

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    for p in sorted(mod.added_perms):
                        print("          + {0}".format(p))
                    for p in sorted(mod.removed_perms):
                        print("          - {0}".format(p))
            print()

    if all_differences or args.class_:
        if diff.added_classes or diff.removed_classes or diff.modified_classes or args.class_:
            print("Classes ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_classes), len(diff.removed_classes), len(diff.modified_classes)))
            if diff.added_classes and not args.stats:
                print("   Added Classes: {0}".format(len(diff.added_classes)))
                for c in sorted(diff.added_classes):
                    print("      + {0}".format(c))
            if diff.removed_classes and not args.stats:
                print("   Removed Classes: {0}".format(len(diff.removed_classes)))
                for c in sorted(diff.removed_classes):
                    print("      - {0}".format(c))
            if diff.modified_classes and not args.stats:
                print("   Modified Classes: {0}".format(len(diff.modified_classes)))
                for name, mod in sorted(diff.modified_classes.items()):
                    change = []
                    if mod.added_perms:
                        change.append("{0} Added permissions".format(len(mod.added_perms)))
                    if mod.removed_perms:
                        change.append("{0} Removed permissions".format(len(mod.removed_perms)))

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    for p in sorted(mod.added_perms):
                        print("          + {0}".format(p))
                    for p in sorted(mod.removed_perms):
                        print("          - {0}".format(p))
            print()

    if all_differences or args.bool_:
        if diff.added_booleans or diff.removed_booleans or \
                diff.modified_booleans or args.bool_:
            print("Booleans ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_booleans), len(diff.removed_booleans),
                len(diff.modified_booleans)))
            if diff.added_booleans and not args.stats:
                print("   Added Booleans: {0}".format(len(diff.added_booleans)))
                for a in sorted(diff.added_booleans):
                    print("      + {0}".format(a))
            if diff.removed_booleans and not args.stats:
                print("   Removed Booleans: {0}".format(len(diff.removed_booleans)))
                for a in sorted(diff.removed_booleans):
                    print("      - {0}".format(a))
            if diff.modified_booleans and not args.stats:
                print("   Modified Booleans: {0}".format(len(diff.modified_booleans)))
                for name, mod in sorted(diff.modified_booleans.items()):
                    print("      * {0} (Modified default state)".format(name))
                    print("          + {0}".format(mod.added_state))
                    print("          - {0}".format(mod.removed_state))

            print()

    if all_differences or args.role:
        if diff.added_roles or diff.removed_roles or diff.modified_roles or args.role:
            print("Roles ({0} Added, {1} Removed, {2} Modified)".format(len(diff.added_roles),
                                                                        len(diff.removed_roles),
                                                                        len(diff.modified_roles)))
            if diff.added_roles and not args.stats:
                print("   Added Roles: {0}".format(len(diff.added_roles)))
                for r in sorted(diff.added_roles):
                    print("      + {0}".format(r))
            if diff.removed_roles and not args.stats:
                print("   Removed Roles: {0}".format(len(diff.removed_roles)))
                for r in sorted(diff.removed_roles):
                    print("      - {0}".format(r))
            if diff.modified_roles and not args.stats:
                print("   Modified Roles: {0}".format(len(diff.modified_roles)))
                for name, mod in sorted(diff.modified_roles.items()):
                    change = []
                    if mod.added_types:
                        change.append("{0} Added types".format(len(mod.added_types)))
                    if mod.removed_types:
                        change.append("{0} Removed types".format(len(mod.removed_types)))

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    for t in sorted(mod.added_types):
                        print("          + {0}".format(t))
                    for t in sorted(mod.removed_types):
                        print("          - {0}".format(t))
            print()

    if all_differences or args.type_:
        if diff.added_types or diff.removed_types or diff.modified_types or args.type_:
            print("Types ({0} Added, {1} Removed, {2} Modified)".format(len(diff.added_types),
                                                                        len(diff.removed_types),
                                                                        len(diff.modified_types)))
            if diff.added_types and not args.stats:
                print("   Added Types: {0}".format(len(diff.added_types)))
                for r in sorted(diff.added_types):
                    print("      + {0}".format(r))
            if diff.removed_types and not args.stats:
                print("   Removed Types: {0}".format(len(diff.removed_types)))
                for r in sorted(diff.removed_types):
                    print("      - {0}".format(r))
            if diff.modified_types and not args.stats:
                print("   Modified Types: {0}".format(len(diff.modified_types)))
                for name, mod in sorted(diff.modified_types.items()):
                    change = []
                    if mod.added_attributes:
                        change.append("{0} Added attributes".format(len(mod.added_attributes)))
                    if mod.removed_attributes:
                        change.append("{0} Removed attributes".format(len(mod.removed_attributes)))
                    if mod.added_aliases:
                        change.append("{0} Added aliases".format(len(mod.added_aliases)))
                    if mod.removed_aliases:
                        change.append("{0} Removed aliases".format(len(mod.removed_aliases)))
                    if mod.modified_permissive:
                        if mod.permissive:
                            change.append("Removed permissive")
                        else:
                            change.append("Added permissive")

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    if mod.added_attributes or mod.removed_attributes:
                        print("          Attributes:")
                    for t in sorted(mod.added_attributes):
                        print("          + {0}".format(t))
                    for t in sorted(mod.removed_attributes):
                        print("          - {0}".format(t))

                    if mod.added_aliases or mod.removed_aliases:
                        print("          Aliases:")
                    for t in sorted(mod.added_aliases):
                        print("          + {0}".format(t))
                    for t in sorted(mod.removed_aliases):
                        print("          - {0}".format(t))

            print()

    if all_differences or args.attribute:
        if diff.added_type_attributes or diff.removed_type_attributes or \
                diff.modified_type_attributes or args.attribute:
            print("Type Attributes ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_type_attributes), len(diff.removed_type_attributes),
                len(diff.modified_type_attributes)))
            if diff.added_type_attributes and not args.stats:
                print("   Added Type Attributes: {0}".format(len(diff.added_type_attributes)))
                for a in sorted(diff.added_type_attributes):
                    print("      + {0}".format(a))
            if diff.removed_type_attributes and not args.stats:
                print("   Removed Type Attributes: {0}".format(len(diff.removed_type_attributes)))
                for a in sorted(diff.removed_type_attributes):
                    print("      - {0}".format(a))
            if diff.modified_type_attributes and not args.stats:
                print("   Modified Type Attributes: {0}".format(len(diff.modified_type_attributes)))
                for name, mod in sorted(diff.modified_type_attributes.items()):
                    change = []
                    if mod.added_types:
                        change.append("{0} Added types".format(len(mod.added_types)))
                    if mod.removed_types:
                        change.append("{0} Removed types".format(len(mod.removed_types)))

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    for t in sorted(mod.added_types):
                        print("          + {0}".format(t))
                    for t in sorted(mod.removed_types):
                        print("          - {0}".format(t))
            print()

    if all_differences or args.user:
        if diff.added_users or diff.removed_users or diff.modified_users or args.user:
            print("Users ({0} Added, {1} Removed, {2} Modified)".format(len(diff.added_users),
                                                                        len(diff.removed_users),
                                                                        len(diff.modified_users)))
            if diff.added_users and not args.stats:
                print("   Added Users: {0}".format(len(diff.added_users)))
                for u in sorted(diff.added_users):
                    print("      + {0}".format(u))
            if diff.removed_users and not args.stats:
                print("   Removed Users: {0}".format(len(diff.removed_users)))
                for u in sorted(diff.removed_users):
                    print("      - {0}".format(u))
            if diff.modified_users and not args.stats:
                print("   Modified Users: {0}".format(len(diff.modified_users)))
                for name, mod in sorted(diff.modified_users.items()):
                    change = []
                    if mod.added_roles:
                        change.append("{0} Added roles".format(len(mod.added_roles)))
                    if mod.removed_roles:
                        change.append("{0} Removed roles".format(len(mod.removed_roles)))
                    if mod.removed_level:
                        change.append("Modified default level")
                    if mod.removed_range:
                        change.append("Modified range")

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    if mod.added_roles or mod.removed_roles:
                        print("          Roles:")
                    for t in sorted(mod.added_roles):
                        print("          + {0}".format(t))
                    for t in sorted(mod.removed_roles):
                        print("          - {0}".format(t))

                    if mod.removed_level:
                        print("          Default level:")
                        print("          + {0}".format(mod.added_level))
                        print("          - {0}".format(mod.removed_level))

                    if mod.removed_range:
                        print("          Range:")
                        print("          + {0}".format(mod.added_range))
                        print("          - {0}".format(mod.removed_range))
            print()

    if all_differences or args.category:
        if diff.added_categories or diff.removed_categories or diff.modified_categories \
                or args.category:
            print("Categories ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_categories), len(diff.removed_categories),
                len(diff.modified_categories)))
            if diff.added_categories and not args.stats:
                print("   Added Categories: {0}".format(len(diff.added_categories)))
                for c in sorted(diff.added_categories):
                    print("      + {0}".format(c))
            if diff.removed_categories and not args.stats:
                print("   Removed Categories: {0}".format(len(diff.removed_categories)))
                for c in sorted(diff.removed_categories):
                    print("      - {0}".format(c))
            if diff.modified_categories and not args.stats:
                print("   Modified Categories: {0}".format(len(diff.modified_categories)))
                for name, mod in sorted(diff.modified_categories.items()):
                    change = []
                    if mod.added_aliases:
                        change.append("{0} Added Aliases".format(len(mod.added_aliases)))
                    if mod.removed_aliases:
                        change.append("{0} Removed Aliases".format(len(mod.removed_aliases)))

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    print("          Aliases:")
                    for a in sorted(mod.added_aliases):
                        print("          + {0}".format(a))
                    for a in sorted(mod.removed_aliases):
                        print("          - {0}".format(a))

            print()

    if all_differences or args.sensitivity:
        if diff.added_sensitivities or diff.removed_sensitivities or diff.modified_sensitivities \
                or args.sensitivity:
            print("Sensitivities ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_sensitivities), len(diff.removed_sensitivities),
                len(diff.modified_sensitivities)))
            if diff.added_sensitivities and not args.stats:
                print("   Added Sensitivites: {0}".format(len(diff.added_sensitivities)))
                for s in sorted(diff.added_sensitivities):
                    print("      + {0}".format(s))
            if diff.removed_sensitivities and not args.stats:
                print("   Removed Sensitivities: {0}".format(len(diff.removed_sensitivities)))
                for s in sorted(diff.removed_sensitivities):
                    print("      - {0}".format(s))
            if diff.modified_sensitivities and not args.stats:
                print("   Modified Sensitivities: {0}".format(len(diff.modified_sensitivities)))
                for name, mod in sorted(diff.modified_sensitivities.items()):
                    change = []
                    if mod.added_aliases:
                        change.append("{0} Added Aliases".format(len(mod.added_aliases)))
                    if mod.removed_aliases:
                        change.append("{0} Removed Aliases".format(len(mod.removed_aliases)))

                    print("      * {0} ({1})".format(name, ", ".join(change)))
                    print("          Aliases:")
                    for a in sorted(mod.added_aliases):
                        print("          + {0}".format(a))
                    for a in sorted(mod.removed_aliases):
                        print("          - {0}".format(a))

            print()

    if all_differences or args.level:
        if diff.added_levels or diff.removed_levels or \
                diff.modified_levels or args.level:
            print("Levels ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_levels), len(diff.removed_levels),
                len(diff.modified_levels)))
            if diff.added_levels and not args.stats:
                print("   Added Levels: {0}".format(len(diff.added_levels)))
                for l in sorted(diff.added_levels):
                    print("      + {0}".format(l))
            if diff.removed_levels and not args.stats:
                print("   Removed Levels: {0}".format(len(diff.removed_levels)))
                for l in sorted(diff.removed_levels):
                    print("      - {0}".format(l))
            if diff.modified_levels and not args.stats:
                print("   Modified Levels: {0}".format(len(diff.modified_levels)))
                for level, added_categories, removed_categories, _ in sorted(diff.modified_levels,
                                                                             key=lambda x: x.level):
                    change = []
                    if added_categories:
                        change.append("{0} Added Categories".format(len(added_categories)))
                    if removed_categories:
                        change.append("{0} Removed Categories".format(len(removed_categories)))

                    print("      * {0} ({1})".format(level.sensitivity, ", ".join(change)))
                    for c in sorted(added_categories):
                        print("          + {0}".format(c))
                    for c in sorted(removed_categories):
                        print("          - {0}".format(c))
            print()

    if all_differences or args.allow:
        if diff.added_allows or diff.removed_allows or diff.modified_allows or args.allow:
            print("Allow Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_allows), len(diff.removed_allows), len(diff.modified_allows)))

            if diff.added_allows and not args.stats:
                print("   Added Allow Rules: {0}".format(len(diff.added_allows)))
                for r in sorted(diff.added_allows):
                    print("      + {0}".format(r))

            if diff.removed_allows and not args.stats:
                print("   Removed Allow Rules: {0}".format(len(diff.removed_allows)))
                for r in sorted(diff.removed_allows):
                    print("      - {0}".format(r))

            if diff.modified_allows and not args.stats:
                print("   Modified Allow Rules: {0}".format(len(diff.modified_allows)))

                for rule, added_perms, removed_perms, matched_perms in sorted(diff.modified_allows,
                                                                              key=lambda x: x.rule):
                    perms = " ".join(chain((p for p in matched_perms),
                                           ("+" + p for p in added_perms),
                                           ("-" + p for p in removed_perms)))
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} {{ {1} }};".format(
                        rule, perms)

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass
                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.neverallow:
        if diff.added_neverallows or diff.removed_neverallows or diff.modified_neverallows or \
                args.neverallow:
            print("Neverallow Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_neverallows), len(diff.removed_neverallows),
                len(diff.modified_neverallows)))

            if diff.added_neverallows and not args.stats:
                print("   Added Neverallow Rules: {0}".format(len(diff.added_neverallows)))
                for r in sorted(diff.added_neverallows):
                    print("      + {0}".format(r))

            if diff.removed_neverallows and not args.stats:
                print("   Removed Neverallow Rules: {0}".format(len(diff.removed_neverallows)))
                for r in sorted(diff.removed_neverallows):
                    print("      - {0}".format(r))

            if diff.modified_neverallows and not args.stats:
                print("   Modified Neverallow Rules: {0}".format(len(diff.modified_neverallows)))

                for rule, added_perms, removed_perms, matched_perms in sorted(
                        diff.modified_neverallows, key=lambda x: x.rule):
                    perms = " ".join(chain((p for p in matched_perms),
                                           ("+" + p for p in added_perms),
                                           ("-" + p for p in removed_perms)))
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} {{ {1} }};".format(
                        rule, perms)

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass
                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.auditallow:
        if diff.added_auditallows or diff.removed_auditallows or diff.modified_auditallows or \
                args.auditallow:
            print("Auditallow Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_auditallows), len(diff.removed_auditallows),
                len(diff.modified_auditallows)))

            if diff.added_auditallows and not args.stats:
                print("   Added Auditallow Rules: {0}".format(len(diff.added_auditallows)))
                for r in sorted(diff.added_auditallows):
                    print("      + {0}".format(r))

            if diff.removed_auditallows and not args.stats:
                print("   Removed Auditallow Rules: {0}".format(len(diff.removed_auditallows)))
                for r in sorted(diff.removed_auditallows):
                    print("      - {0}".format(r))

            if diff.modified_auditallows and not args.stats:
                print("   Modified Auditallow Rules: {0}".format(len(diff.modified_auditallows)))

                for rule, added_perms, removed_perms, matched_perms in sorted(
                        diff.modified_auditallows, key=lambda x: x.rule):
                    perms = " ".join(chain((p for p in matched_perms),
                                           ("+" + p for p in added_perms),
                                           ("-" + p for p in removed_perms)))
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} {{ {1} }};".format(
                        rule, perms)

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass
                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.dontaudit:
        if diff.added_dontaudits or diff.removed_dontaudits or diff.modified_dontaudits or \
                args.dontaudit:
            print("Dontaudit Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_dontaudits), len(diff.removed_dontaudits),
                len(diff.modified_dontaudits)))

            if diff.added_dontaudits and not args.stats:
                print("   Added Dontaudit Rules: {0}".format(len(diff.added_dontaudits)))
                for r in sorted(diff.added_dontaudits):
                    print("      + {0}".format(r))

            if diff.removed_dontaudits and not args.stats:
                print("   Removed Dontaudit Rules: {0}".format(len(diff.removed_dontaudits)))
                for r in sorted(diff.removed_dontaudits):
                    print("      - {0}".format(r))

            if diff.modified_dontaudits and not args.stats:
                print("   Modified Dontaudit Rules: {0}".format(len(diff.modified_dontaudits)))

                for rule, added_perms, removed_perms, matched_perms in sorted(
                        diff.modified_dontaudits, key=lambda x: x.rule):
                    perms = " ".join(chain((p for p in matched_perms),
                                           ("+" + p for p in added_perms),
                                           ("-" + p for p in removed_perms)))
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} {{ {1} }};".format(
                        rule, perms)

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass
                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.type_trans:
        if diff.added_type_transitions or diff.removed_type_transitions or \
                diff.modified_type_transitions or args.type_trans:
            print("Type_transition Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_type_transitions), len(diff.removed_type_transitions),
                len(diff.modified_type_transitions)))

            if diff.added_type_transitions and not args.stats:
                print("   Added Type_transition Rules: {0}".format(
                    len(diff.added_type_transitions)))
                for r in sorted(diff.added_type_transitions):
                    print("      + {0}".format(r))

            if diff.removed_type_transitions and not args.stats:
                print("   Removed Type_transition Rules: {0}".format(
                    len(diff.removed_type_transitions)))
                for r in sorted(diff.removed_type_transitions):
                    print("      - {0}".format(r))

            if diff.modified_type_transitions and not args.stats:
                print("   Modified Type_transition Rules: {0}".format(
                    len(diff.modified_type_transitions)))

                for rule, added_default, removed_default in sorted(diff.modified_type_transitions,
                                                                   key=lambda x: x.rule):
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} +{1} -{2}".format(
                        rule, added_default, removed_default)

                    try:
                        rule_string += " {0}".format(rule.filename)
                    except AttributeError:
                        pass

                    rule_string += ";"

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass

                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.type_change:
        if diff.added_type_changes or diff.removed_type_changes or \
                diff.modified_type_changes or args.type_change:
            print("Type_change Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_type_changes), len(diff.removed_type_changes),
                len(diff.modified_type_changes)))

            if diff.added_type_changes and not args.stats:
                print("   Added Type_change Rules: {0}".format(len(diff.added_type_changes)))
                for r in sorted(diff.added_type_changes):
                    print("      + {0}".format(r))

            if diff.removed_type_changes and not args.stats:
                print("   Removed Type_change Rules: {0}".format(len(diff.removed_type_changes)))
                for r in sorted(diff.removed_type_changes):
                    print("      - {0}".format(r))

            if diff.modified_type_changes and not args.stats:
                print("   Modified Type_change Rules: {0}".format(len(diff.modified_type_changes)))

                for rule, added_default, removed_default in sorted(diff.modified_type_changes,
                                                                   key=lambda x: x.rule):
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} +{1} -{2}".format(
                        rule, added_default, removed_default)

                    try:
                        rule_string += " {0}".format(rule.filename)
                    except AttributeError:
                        pass

                    rule_string += ";"

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass

                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.type_member:
        if diff.added_type_members or diff.removed_type_members or \
                diff.modified_type_members or args.type_member:
            print("Type_member Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_type_members), len(diff.removed_type_members),
                len(diff.modified_type_members)))

            if diff.added_type_members and not args.stats:
                print("   Added Type_member Rules: {0}".format(len(diff.added_type_members)))
                for r in sorted(diff.added_type_members):
                    print("      + {0}".format(r))

            if diff.removed_type_members and not args.stats:
                print("   Removed Type_member Rules: {0}".format(len(diff.removed_type_members)))
                for r in sorted(diff.removed_type_members):
                    print("      - {0}".format(r))

            if diff.modified_type_members and not args.stats:
                print("   Modified Type_member Rules: {0}".format(len(diff.modified_type_members)))

                for rule, added_default, removed_default in sorted(diff.modified_type_members,
                                                                   key=lambda x: x.rule):
                    rule_string = "{0.ruletype} {0.source} {0.target}:{0.tclass} +{1} -{2}".format(
                        rule, added_default, removed_default)

                    try:
                        rule_string += " {0}".format(rule.filename)
                    except AttributeError:
                        pass

                    rule_string += ";"

                    try:
                        rule_string += " [ {0} ]".format(rule.conditional)
                    except AttributeError:
                        pass

                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.role_allow:
        if diff.added_role_allows or diff.removed_role_allows or args.role_allow:
            print("Role allow Rules ({0} Added, {1} Removed)".format(
                len(diff.added_role_allows), len(diff.removed_role_allows)))

            if diff.added_role_allows and not args.stats:
                print("   Added Role allow Rules: {0}".format(
                    len(diff.added_role_allows)))
                for r in sorted(diff.added_role_allows):
                    print("      + {0}".format(r))

            if diff.removed_role_allows and not args.stats:
                print("   Removed Role allow Rules: {0}".format(
                    len(diff.removed_role_allows)))
                for r in sorted(diff.removed_role_allows):
                    print("      - {0}".format(r))

            print()

    if all_differences or args.role_trans:
        if diff.added_role_transitions or diff.removed_role_transitions or \
                diff.modified_role_transitions or args.role_trans:
            print("Role_transition Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_role_transitions), len(diff.removed_role_transitions),
                len(diff.modified_role_transitions)))

            if diff.added_role_transitions and not args.stats:
                print("   Added Role_transition Rules: {0}".format(
                    len(diff.added_role_transitions)))
                for r in sorted(diff.added_role_transitions):
                    print("      + {0}".format(r))

            if diff.removed_role_transitions and not args.stats:
                print("   Removed Role_transition Rules: {0}".format(
                    len(diff.removed_role_transitions)))
                for r in sorted(diff.removed_role_transitions):
                    print("      - {0}".format(r))

            if diff.modified_role_transitions and not args.stats:
                print("   Modified Role_transition Rules: {0}".format(
                    len(diff.modified_role_transitions)))

                for rule, added_default, removed_default in sorted(diff.modified_role_transitions,
                                                                   key=lambda x: x.rule):
                    rule_string = \
                        "{0.ruletype} {0.source} {0.target}:{0.tclass} +{1} -{2}".format(
                            rule, added_default, removed_default)

                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.range_trans:
        if diff.added_range_transitions or diff.removed_range_transitions or \
                diff.modified_range_transitions or args.range_trans:
            print("Range_transition Rules ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_range_transitions), len(diff.removed_range_transitions),
                len(diff.modified_range_transitions)))

            if diff.added_range_transitions and not args.stats:
                print("   Added Range_transition Rules: {0}".format(
                    len(diff.added_range_transitions)))
                for r in sorted(diff.added_range_transitions):
                    print("      + {0}".format(r))

            if diff.removed_range_transitions and not args.stats:
                print("   Removed Range_transition Rules: {0}".format(
                    len(diff.removed_range_transitions)))
                for r in sorted(diff.removed_range_transitions):
                    print("      - {0}".format(r))

            if diff.modified_range_transitions and not args.stats:
                print("   Modified Range_transition Rules: {0}".format(
                    len(diff.modified_range_transitions)))

                for rule, added_default, removed_default in sorted(diff.modified_range_transitions,
                                                                   key=lambda x: x.rule):
                    # added brackets around range change for clarity since ranges
                    # can have '-' and spaces.
                    rule_string = \
                        "{0.ruletype} {0.source} {0.target}:{0.tclass} +[{1}] -[{2}]".format(
                            rule, added_default, removed_default)

                    print("      * {0}".format(rule_string))

            print()

    if all_differences or args.initialsid:
        if diff.added_initialsids or diff.removed_initialsids or diff.modified_initialsids \
                or args.initialsid:
            print("Initial SIDs ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_initialsids), len(diff.removed_initialsids),
                len(diff.modified_initialsids)))
            if diff.added_initialsids and not args.stats:
                print("   Added Initial SIDs: {0}".format(len(diff.added_initialsids)))
                for s in sorted(diff.added_initialsids):
                    print("      + {0}".format(s.statement()))
            if diff.removed_initialsids and not args.stats:
                print("   Removed Initial SIDs: {0}".format(len(diff.removed_initialsids)))
                for s in sorted(diff.removed_initialsids):
                    print("      - {0}".format(s.statement()))
            if diff.modified_initialsids and not args.stats:
                print("   Modified Initial SIDs: {0}".format(len(diff.modified_initialsids)))
                for name, mod in sorted(diff.modified_initialsids.items()):
                    print("      * {0} +[{1.added_context}] -[{1.removed_context}];".format(
                          name, mod))

            print()

    if all_differences or args.fs_use:
        if diff.added_fs_uses or diff.removed_fs_uses or diff.modified_fs_uses \
                or args.fs_use:
            print("Fs_use ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_fs_uses), len(diff.removed_fs_uses),
                len(diff.modified_fs_uses)))
            if diff.added_fs_uses and not args.stats:
                print("   Added Fs_use: {0}".format(len(diff.added_fs_uses)))
                for s in sorted(diff.added_fs_uses):
                    print("      + {0}".format(s))
            if diff.removed_fs_uses and not args.stats:
                print("   Removed Fs_use: {0}".format(len(diff.removed_fs_uses)))
                for s in sorted(diff.removed_fs_uses):
                    print("      - {0}".format(s))
            if diff.modified_fs_uses and not args.stats:
                print("   Modified Fs_use: {0}".format(len(diff.modified_fs_uses)))
                for entry in sorted(diff.modified_fs_uses, key=lambda x: x.rule):
                    print("      * {0.ruletype} {0.fs} +[{1}] -[{2}];".format(
                          entry.rule, entry.added_context, entry.removed_context))

            print()

    if all_differences or args.genfscon:
        if diff.added_genfscons or diff.removed_genfscons or diff.modified_genfscons \
                or args.genfscon:
            print("Genfscons ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_genfscons), len(diff.removed_genfscons),
                len(diff.modified_genfscons)))
            if diff.added_genfscons and not args.stats:
                print("   Added Genfscons: {0}".format(len(diff.added_genfscons)))
                for s in sorted(diff.added_genfscons):
                    print("      + {0}".format(s))
            if diff.removed_genfscons and not args.stats:
                print("   Removed Genfscons: {0}".format(len(diff.removed_genfscons)))
                for s in sorted(diff.removed_genfscons):
                    print("      - {0}".format(s))
            if diff.modified_genfscons and not args.stats:
                print("   Modified Genfscons: {0}".format(len(diff.modified_genfscons)))
                for entry in sorted(diff.modified_genfscons, key=lambda x: x.rule):
                    print("      * genfscon {0.fs} {0.path} {0.filetype} +[{1}] -[{2}];".format(
                          entry.rule, entry.added_context, entry.removed_context))

            print()

    if all_differences or args.netifcon:
        if diff.added_netifcons or diff.removed_netifcons or \
                diff.modified_netifcons or args.netifcon:
            print("Netifcons ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_netifcons), len(diff.removed_netifcons),
                len(diff.modified_netifcons)))
            if diff.added_netifcons and not args.stats:
                print("   Added Netifcons: {0}".format(len(diff.added_netifcons)))
                for n in sorted(diff.added_netifcons):
                    print("      + {0}".format(n))
            if diff.removed_netifcons and not args.stats:
                print("   Removed Netifcons: {0}".format(len(diff.removed_netifcons)))
                for n in sorted(diff.removed_netifcons):
                    print("      - {0}".format(n))
            if diff.modified_netifcons and not args.stats:
                print("   Modified Netifcons: {0}".format(len(diff.modified_netifcons)))
                for entry in sorted(diff.modified_netifcons, key=lambda x: x.rule):
                    # This output is different than other statements because
                    # it becomes difficult to read if this was condensed
                    # into a single line, especially if both contexts
                    # are modified.
                    change = []
                    if entry.removed_context:
                        change.append("Modified Context")
                    if entry.removed_packet:
                        change.append("Modified Packet Context")

                    print("      * {0.netif} ({1})".format(entry.rule, ", ".join(change)))

                    if entry.removed_context:
                        print("          Context:")
                        print("             + {0}".format(entry.added_context))
                        print("             - {0}".format(entry.removed_context))
                    if entry.removed_packet:
                        print("          Packet Context:")
                        print("             + {0}".format(entry.added_packet))
                        print("             - {0}".format(entry.removed_packet))

            print()

    if all_differences or args.nodecon:
        if diff.added_nodecons or diff.removed_nodecons or diff.modified_nodecons \
                or args.nodecon:
            print("Nodecons ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_nodecons), len(diff.removed_nodecons),
                len(diff.modified_nodecons)))
            if diff.added_nodecons and not args.stats:
                print("   Added Nodecons: {0}".format(len(diff.added_nodecons)))
                for n in sorted(diff.added_nodecons):
                    print("      + {0}".format(n))
            if diff.removed_nodecons and not args.stats:
                print("   Removed Nodecons: {0}".format(len(diff.removed_nodecons)))
                for n in sorted(diff.removed_nodecons):
                    print("      - {0}".format(n))
            if diff.modified_nodecons and not args.stats:
                print("   Modified Nodecons: {0}".format(len(diff.modified_nodecons)))
                for con, added_context, removed_context in sorted(diff.modified_nodecons,
                                                                  key=lambda x: x.rule):
                    print("      * nodecon {0.address} {0.netmask} +[{1}] -[{2}];".format(
                          con, added_context, removed_context))

            print()

    if all_differences or args.portcon:
        if diff.added_portcons or diff.removed_portcons or diff.modified_portcons \
                or args.portcon:
            print("Portcons ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_portcons), len(diff.removed_portcons),
                len(diff.modified_portcons)))
            if diff.added_portcons and not args.stats:
                print("   Added Portcons: {0}".format(len(diff.added_portcons)))
                for n in sorted(diff.added_portcons):
                    print("      + {0}".format(n))
            if diff.removed_portcons and not args.stats:
                print("   Removed Portcons: {0}".format(len(diff.removed_portcons)))
                for n in sorted(diff.removed_portcons):
                    print("      - {0}".format(n))
            if diff.modified_portcons and not args.stats:
                print("   Modified Portcons: {0}".format(len(diff.modified_portcons)))
                for con, added_context, removed_context in sorted(diff.modified_portcons,
                                                                  key=lambda x: x.rule):
                    low, high = con.ports
                    if low == high:
                        print("      * portcon {0.protocol} {1} +[{2}] -[{3}];".format(
                              con, low, added_context, removed_context))
                    else:
                        print("      * portcon {0.protocol} {1}-{2} +[{3}] -[{4}];".format(
                              con, low, high, added_context, removed_context))

            print()

    if all_differences or args.polcap:
        if diff.added_polcaps or diff.removed_polcaps or args.polcap:
            print("Policy Capabilities ({0} Added, {1} Removed)".format(
                len(diff.added_polcaps), len(diff.removed_polcaps)))
            if diff.added_polcaps and not args.stats:
                print("   Added Policy Capabilities: {0}".format(len(diff.added_polcaps)))
                for n in sorted(diff.added_polcaps):
                    print("      + {0}".format(n))
            if diff.removed_polcaps and not args.stats:
                print("   Removed Policy Capabilities: {0}".format(len(diff.removed_polcaps)))
                for n in sorted(diff.removed_polcaps):
                    print("      - {0}".format(n))

            print()

    if all_differences or args.default:
        if diff.added_defaults or diff.removed_defaults or args.default:
            print("Defaults ({0} Added, {1} Removed, {2} Modified)".format(
                len(diff.added_defaults), len(diff.removed_defaults), len(diff.modified_defaults)))
            if diff.added_defaults and not args.stats:
                print("   Added Defaults: {0}".format(len(diff.added_defaults)))
                for d in sorted(diff.added_defaults):
                    print("      + {0}".format(d))
            if diff.removed_defaults and not args.stats:
                print("   Removed Defaults: {0}".format(len(diff.removed_defaults)))
                for d in sorted(diff.removed_defaults):
                    print("      - {0}".format(d))
            if diff.modified_defaults and not args.stats:
                print("   Modified Defaults: {0}".format(len(diff.modified_defaults)))
                for default, added_default, removed_default, added_range, removed_range in sorted(
                        diff.modified_defaults, key=lambda x: x.rule):
                    line = "      * {0.ruletype} {0.tclass} ".format(default)
                    if removed_default:
                        line += "+{0} -{1}".format(added_default, removed_default)
                    else:
                        line += default.default

                    if removed_range:
                        line += " +{0} -{1};".format(added_range, removed_range)
                    else:
                        try:
                            line += " {0};".format(default.default_range)
                        except AttributeError:
                            line += ";"
                    print(line)

            print()

except Exception as err:
    if args.debug:
        import traceback
        traceback.print_exc()
    else:
        print(err)

    sys.exit(1)
