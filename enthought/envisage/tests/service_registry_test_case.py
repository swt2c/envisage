""" Tests for the service registry. """


# Standard library imports.
import unittest

# Enthought library imports.
from enthought.envisage.api import ServiceRegistry
from enthought.traits.api import HasTraits, Int, Interface, implements


class ServiceRegistryTestCase(unittest.TestCase):
    """ Tests for the service registry. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.service_registry = ServiceRegistry()

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """
        
        return
    
    ###########################################################################
    # Tests.
    ###########################################################################

    def test_get_services(self):
        """ get services """

        class IFoo(Interface):
            pass

        class Foo(HasTraits):
            implements(IFoo)

        # Register a service.
        foo = Foo()
        self.service_registry.register_service(IFoo, foo)

        # Look it up again.
        services = self.service_registry.get_services(IFoo)
        self.assertEqual([foo], services)

        class IBar(Interface):
            pass

        # Lookup a non-existent service.
        services = self.service_registry.get_services(IBar)
        self.assertEqual([], services)
        
        return

    def test_get_services_with_query(self):
        """ get services with query """

        class IFoo(Interface):
            price = Int

        class Foo(HasTraits):
            implements(IFoo)

        # Register two services.
        #
        # This one shows how the object's attributes are used when evaluating
        # a query.
        foo = Foo(price=100)
        self.service_registry.register_service(IFoo, foo)

        # This one shows how properties can be specified that *take precedence*
        # over the object's attributes when evaluating a query.
        goo = Foo(price=10)
        self.service_registry.register_service(IFoo, goo, {'price' : 200})

        # Create a query that doesn't match any registered object.
        services = self.service_registry.get_services(IFoo, 'color == "red"')
        self.assertEqual([], services)

        # Create a query that matches one of the registered objects.
        services = self.service_registry.get_services(IFoo, 'price <= 100')
        self.assertEqual([foo], services)

        # Create a query that matches both registered objects.
        services = self.service_registry.get_services(IFoo, 'price >= 100')
        self.assert_(foo in services)
        self.assert_(goo in services)
        self.assertEqual(2, len(services))
        
        class IBar(Interface):
            pass

        # Lookup a non-existent service.
        services = self.service_registry.get_services(IBar, 'price <= 100')
        self.assertEqual([], services)

        return

    def test_get_service(self):
        """ get service """

        class IFoo(Interface):
            pass

        class Foo(HasTraits):
            implements(IFoo)

        # Register two services.
        foo = Foo()
        self.service_registry.register_service(IFoo, foo)

        goo = Foo()
        self.service_registry.register_service(IFoo, goo)

        # Look up one of them!
        service = self.service_registry.get_service(IFoo)
        self.assert_(foo is service or goo is service)

        class IBar(Interface):
            pass

        # Lookup a non-existent service.
        service = self.service_registry.get_service(IBar)
        self.assertEqual(None, service)
        
        return

    def test_get_service_with_query(self):
        """ get service with query """

        class IFoo(Interface):
            price = Int

        class Foo(HasTraits):
            implements(IFoo)

        # Register two services.
        #
        # This one shows how the object's attributes are used when evaluating
        # a query.
        foo = Foo(price=100)
        self.service_registry.register_service(IFoo, foo)

        # This one shows how properties can be specified that *take precedence*
        # over the object's attributes when evaluating a query.
        goo = Foo(price=10)
        self.service_registry.register_service(IFoo, goo, {'price' : 200})

        # Create a query that doesn't match any registered object.
        service = self.service_registry.get_service(IFoo, 'price < 100')
        self.assertEqual(None, service)

        # Create a query that matches one of the registered objects.
        service = self.service_registry.get_service(IFoo, 'price <= 100')
        self.assertEqual(foo, service)

        # Create a query that matches both registered objects.
        service = self.service_registry.get_service(IFoo, 'price >= 100')
        self.assert_(foo is service or goo is service)
        
        class IBar(Interface):
            pass

        # Lookup a non-existent service.
        service = self.service_registry.get_service(IBar, 'price <= 100')
        self.assertEqual(None, service)

        return

    def test_get_service_properties(self):
        """ get service properties """

        class IFoo(Interface):
            price = Int

        class Foo(HasTraits):
            implements(IFoo)

        # Register two services.
        #
        # This one has no properties.
        foo = Foo(price=100)
        foo_id = self.service_registry.register_service(IFoo, foo)

        # This one has properties.
        goo = Foo(price=10)
        goo_id = self.service_registry.register_service(
            IFoo, goo, {'price' : 200}
        )

        # Get the properties.
        foo_properties = self.service_registry.get_service_properties(foo_id)
        self.assertEqual({}, foo_properties)

        goo_properties = self.service_registry.get_service_properties(goo_id)
        self.assertEqual(200, goo_properties['price'])

        # Update the properties.
        foo_properties['price'] = 300
        goo_properties['price'] = 500
        
        # Get the properties again.
        foo_properties = self.service_registry.get_service_properties(foo_id)
        self.assertEqual(300, foo_properties['price'])

        goo_properties = self.service_registry.get_service_properties(goo_id)
        self.assertEqual(500, goo_properties['price'])

        # Try to get the properties of a non-existent service.
        self.failUnlessRaises(
            ValueError, self.service_registry.get_service_properties, -1
        )
        
        return

    def test_unregister_service(self):
        """ unregister service """

        class IFoo(Interface):
            price = Int

        class Foo(HasTraits):
            implements(IFoo)

        # Register two services.
        #
        # This one shows how the object's attributes are used when evaluating
        # a query.
        foo = Foo(price=100)
        foo_id = self.service_registry.register_service(IFoo, foo)

        # This one shows how properties can be specified that *take precedence*
        # over the object's attributes when evaluating a query.
        goo = Foo(price=10)
        goo_id = self.service_registry.register_service(
            IFoo, goo, {'price' : 200}
        )

        # Create a query that doesn't match any registered object.
        service = self.service_registry.get_service(IFoo, 'price < 100')
        self.assertEqual(None, service)

        # Create a query that matches one of the registered objects.
        service = self.service_registry.get_service(IFoo, 'price <= 100')
        self.assertEqual(foo, service)

        # Create a query that matches both registered objects.
        service = self.service_registry.get_service(IFoo, 'price >= 100')
        self.assert_(foo is service or goo is service)

        #### Now do some unregistering! ####

        # Unregister 'foo'.
        self.service_registry.unregister_service(foo_id)
        
        # This query should no longer match any of the registered objects.
        service = self.service_registry.get_service(IFoo, 'price <= 100')
        self.assertEqual(None, service)

        # Unregister 'goo'.
        self.service_registry.unregister_service(goo_id)
        
        # This query should no longer match any of the registered objects.
        service = self.service_registry.get_service(IFoo, 'price >= 100')
        self.assertEqual(None, service)

        # Try to unregister a non-existent service.
        self.failUnlessRaises(
            ValueError, self.service_registry.unregister_service, -1
        )

        return

    def test_service_factory(self):
        """ service factory """

        class IFoo(Interface):
            price = Int

        class Foo(HasTraits):
            implements(IFoo)

        # Register a service factory. A service factory is any callable that
        # takes the properties as keyword arguments. In this case we just use
        # a class that has traits.
        self.service_registry.register_service(IFoo, Foo, {'price' : 100})
        
        # Create a query that matches the registered object.
        service = self.service_registry.get_service(IFoo, 'price <= 100')
        self.assertNotEqual(None, service)
        self.assertEqual(Foo, type(service))

        # Make sure that the object created by the factory is cached (i.e. we
        # get the same object back from now on!).
        service2 = self.service_registry.get_service(IFoo, 'price <= 100')
        self.assert_(service is service2)

        return

#### EOF ######################################################################