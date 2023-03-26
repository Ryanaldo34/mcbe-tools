from dataclasses import dataclass, field
from typing import Any, TypedDict, Callable, Annotated, get_type_hints, get_origin, get_args
from abc import ABC, abstractmethod
from addons.errors import CustomComponentExistsError, ComponentPropertyTypeError, BadDataInputExcep
import importlib, os

_PropertyType = str | float | int | bool

@dataclass
class Range:
    """Annotates a range type for a component property"""
    min: int | float
    max: int | float

Vector = list[float, float, float]

class CustomComponent(ABC):
    @staticmethod
    @abstractmethod
    def get_name() -> str:
        ...

    @abstractmethod
    def build_self(self, *, root: dict[str, Any], properties: dict[str, Any]) -> None:
        """When the project is built, a behavior file is parsed and any instances of this custom component are compiled"""
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

def verify_component_properties(builder: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]):
    def wrapper(ref: CustomComponent, *args, **kwargs):
        passed_properties = kwargs['properties']
        annotations = get_type_hints(ref, include_extras=True)
        for prop, expected_t in annotations.items():
            passed_value = passed_properties.get(prop)
            t_args = get_args(expected_t)
            t_origin = get_origin(expected_t)
            # if there is not a default value for a property not passed into the custom component
            default_property_value = getattr(ref, prop, None)
            if passed_value is None and default_property_value is None:
                raise ValueError(f'{prop} is a required property on the custom component: {ref.get_name()}')
            if passed_value is None:
                passed_properties[prop] = default_property_value
                continue
            # vanilla types that are not annotated
            if t_origin is None:
                if not isinstance(passed_value, expected_t):
                    raise ComponentPropertyTypeError(prop, type(passed_value), expected_t)
                continue
            elif t_origin is Annotated:
                main_t, *annotation_t = t_args
                if main_t == int or main_t == float:
                    r: Range = annotation_t[0]
                    assert isinstance(r, Range), 'A number can only be annotated as a Range'
                    if not isinstance(passed_value, int) and not isinstance(passed_value, float):
                        raise ComponentPropertyTypeError(prop, type(passed_value), f'number in range {r.min} to {r.max}')
                    if not passed_value >= r.min or not passed_value <= r.max:
                        raise ComponentPropertyTypeError(prop, type(passed_value), f'Is a number but must be in range {r.min} to {r.max}')
            elif t_origin is list or expected_t is list:
                is_vector = True if len(t_args) == 3 else False
                assert len(t_args) == 1, 'A list in a custom component can only be of one type'
                if not all([isinstance(el, t_args[0]) for el in passed_value]):
                    raise ComponentPropertyTypeError(prop, type(passed_value), expected_t)
                if is_vector and len(passed_value) != 3:
                    raise ComponentPropertyTypeError(prop, type(passed_value), 'Was expecting a vector with a length of 3')
            else:
                raise ValueError(f"{t_origin} cannot be an annotated type for a custom component property")

        builder(ref, *args, **kwargs)
    return wrapper
        
component_registry = CustomComponentRegistry()
component_registry.register_components()