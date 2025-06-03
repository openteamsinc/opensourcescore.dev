from dataclasses import fields, is_dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)


class TypescriptGenerator:
    def __init__(self):
        self.processed_classes = set()
        self.type_definitions = []
        self.custom_type_mappings = {}

    def register(self, cls, tstype: str):
        """Register a custom Python type to TypeScript type mapping."""
        self.custom_type_mappings[cls] = tstype
        return self

    def update(self, cls):
        """Add a new dataclass to the generator."""
        if not is_dataclass(cls):
            raise ValueError(f"{cls.__name__} is not a dataclass")

        # Skip if already processed to avoid duplicates
        if cls in self.processed_classes:
            return self

        # Process the class and add its TypeScript definition
        ts_def = self._create_typescript_for_class(cls)
        if ts_def and ts_def not in self.type_definitions:
            self.type_definitions.append(ts_def)

        return self

    def dump(self):
        """Return the complete TypeScript definitions as a string."""
        if not self.type_definitions:
            return ""
        return "\n\n".join(self.type_definitions)

    def _create_typescript_for_class(self, cls):
        """Generate TypeScript type definition for a dataclass."""
        if cls in self.processed_classes:
            return ""  # Avoid infinite recursion with circular references

        self.processed_classes.add(cls)

        type_hints = get_type_hints(cls)
        class_fields = fields(cls)

        # Map Python types to TypeScript types
        ts_fields = []

        for field in class_fields:
            field_name = field.name
            field_type = type_hints[field_name]

            ts_type = self._python_type_to_typescript(field_type)

            # Handle nested dataclasses
            if is_dataclass(field_type) and field_type != cls:
                self.update(field_type)

            # Handle optional/union types with nested dataclasses
            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                for arg in args:
                    if is_dataclass(arg) and arg != cls:
                        self.update(arg)

            ts_fields.append(f"  {field_name}: {ts_type}")

        ts_definition = (
            f"export type {cls.__name__} = {{\n" + ",\n".join(ts_fields) + "\n}"
        )
        return ts_definition

    def _python_type_to_typescript(self, py_type):
        """Convert Python type to TypeScript type."""
        # Check for custom type mappings first
        if py_type in self.custom_type_mappings:
            return self.custom_type_mappings[py_type]

        # Handle primitive types
        if py_type is str:
            return "string"
        elif py_type is int or py_type is float:
            return "number"
        elif py_type is bool:
            return "boolean"
        elif py_type is None or py_type is type(None):
            return "null"
        elif py_type is Any:
            return "any"

        # Handle dataclasses (references)
        if is_dataclass(py_type):
            return py_type.__name__

        # Handle generics
        origin = get_origin(py_type)
        if origin is not None:
            args = get_args(py_type)

            # Handle lists/arrays
            if origin is list or origin is List:
                if args:
                    inner_type = self._python_type_to_typescript(args[0])
                    return f"{inner_type}[]"
                return "any[]"

            # Handle dictionaries
            elif origin is dict or origin is Dict:
                if len(args) >= 2:
                    key_type = self._python_type_to_typescript(args[0])
                    value_type = self._python_type_to_typescript(args[1])

                    # In TypeScript, only string, number, and symbol can be used as index types
                    if key_type in ["string", "number"]:
                        return f"{{ [key: {key_type}]: {value_type} }}"
                    else:
                        return f"Record<{key_type}, {value_type}>"
                return "Record<string, any>"

            # Handle optional types
            elif origin is Union:
                # Check if it's an Optional (Union with None)
                if type(None) in args:
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        return f"{self._python_type_to_typescript(non_none_args[0])} | null"

                # Regular union type
                ts_types = [self._python_type_to_typescript(arg) for arg in args]
                return " | ".join(ts_types)

            # Handle tuples
            elif origin is tuple or origin is Tuple:
                if not args:
                    return "[]"
                # Handle variable-length tuples (Tuple[X, ...])
                elif len(args) == 2 and args[1] is Ellipsis:
                    return f"{self._python_type_to_typescript(args[0])}[]"
                else:
                    ts_types = [self._python_type_to_typescript(arg) for arg in args]
                    return f"[{', '.join(ts_types)}]"

            # Handle Optional directly
            elif origin is Optional:
                if args:
                    return f"{self._python_type_to_typescript(args[0])} | null"
                return "any | null"

        # Default to any for unknown types
        return "any"
