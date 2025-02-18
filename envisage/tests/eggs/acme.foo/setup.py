# (C) Copyright 2007-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
# Major package imports.
from setuptools import setup, find_packages

setup(
    name="acme.foo",
    version="0.1a1",
    author="Enthought, Inc",
    author_email="info@enthought.com",
    license="BSD",
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    namespace_packages=["acme", "acme.foo"],
    install_requires=[],
    entry_points="""

    [envisage.plugins]
    acme.foo = acme.foo.foo_plugin:FooPlugin

    """,
)
