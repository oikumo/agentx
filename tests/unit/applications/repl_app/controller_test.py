import unittest

from agent_x.applications.repl_app.controller import Controller

# ── Helpers ──────────────────────────────────────────────────────────────────


class ConcreteController(Controller):
    """Minimal concrete subclass – Controller has no abstract methods so any
    subclass (or Controller itself) can be instantiated directly."""

    pass


# ── Tests ─────────────────────────────────────────────────────────────────────


class ControllerTest(unittest.TestCase):
    def test_controller_is_abstract_base_class(self):
        # Controller inherits from ABC. Even though it defines no abstract
        # methods, it still serves as the architectural base for all controllers.
        # We verify the inheritance chain is intact.
        import abc

        self.assertTrue(issubclass(Controller, abc.ABC))

    def test_concrete_subclass_can_be_instantiated(self):
        # Because Controller declares no @abstractmethod, a concrete subclass
        # needs no additional implementation to be constructable.
        controller = ConcreteController()
        self.assertIsInstance(controller, Controller)

    def test_controller_init_does_not_raise(self):
        # __init__ is a simple `pass`; instantiation must be side-effect-free.
        controller = ConcreteController()
        self.assertIsNotNone(controller)
