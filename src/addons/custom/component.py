from dataclasses import dataclass, field
from typing import Any, TypedDict, Callable
from abc import ABC, abstractmethod
from addons.errors import CustomComponentExistsError, ComponentPropertyTypeError, BadDataInputExcep
import importlib, os

class CustomComponent(ABC):
    @staticmethod
    @abstractmethod
    def get_name() -> str:
        ...

    @abstractmethod
    def build_self(self, *, root: dict[str, Any], properties: dict[str, Any]) -> None:
        """When the project is built, a behavior file is parsed and any instances of this custom component are compiledd"""
        # set variable properties in the data as the key of the properties
        ...

@dataclass(frozen=True)
class CustomComponentRegistry:
    _data: dict[str, CustomComponent] = field(init=True, default_factory=dict)
    namespace: str = 'custom'

    def __register_component(self, component: CustomComponent) -> None:
        """Adds a custom component object to the registry"""
        self._data[component.get_name()] = component

    def register_components(self) -> None:
        """Loops through and dyanmically loads custom components to the registry"""
        custom_components = [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.dirname(__file__), 'components')) if os.path.basename(f) != '__init__.py' and os.path.basename(f).endswith('.py')]
        for component_name in custom_components:
            try:
                module = importlib.import_module(f'addons.custom.components.{component_name}')
                if not hasattr(module, 'Component'):
                    raise BadDataInputExcep(f'The file: {component_name} does not have a proper custom component declared!')
                else:
                    Component: CustomComponent = getattr(module, 'Component')
                    new_component = Component
                    self.__register_component(new_component)
            except ModuleNotFoundError:
                print(f'An invalid file was found in {component_name}')
                raise
        
    def get_component(self, component_name: str) -> CustomComponent:
        """Returns a custom component object from the registry"""
        component: CustomComponent = self._data.get(component_name)
        if component is None:
            print(self._data)
            raise CustomComponentExistsError(component_name)

        return component

def verify_component_properties(builder: Callable):
    def wrapper(ref: CustomComponent, *args, **kwargs):
        annotations = ref.__annotations__
        passed_properties = kwargs['properties']

        for prop, expected_type in annotations.items():
            passed_property = passed_properties.get(prop)

            if passed_property is None:
                default = getattr(ref, prop, None)

                if default is None: # if the required property was not declared and doesn't have a default value
                    raise BadDataInputExcep(f'{prop} is a required field in the component: {ref.name} and no value was provided!')
                else:
                    passed_properties[prop] = default

            if not isinstance(passed_properties[prop], expected_type):
                raise ComponentPropertyTypeError(prop, type(passed_property), expected_type)

        builder(ref, *args, **kwargs)

    return wrapper
        
component_registry = CustomComponentRegistry()
component_registry.register_components()