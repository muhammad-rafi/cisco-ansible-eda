# filter_plugins/type_conversion.py

class FilterModule:
    def filters(self):
        return {
            'to_int': self.to_int
        }

    def to_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

# class FilterModule:
#     def filters(self):
#         def convert_to_int(value, default=0):
#             """
#             Attempts to convert a value to an integer, returns a default value if conversion fails.

#             Args:
#                 value: The value to convert.
#                 default: The default value to return in case of conversion failure (defaults to 0).

#             Returns:
#                 The integer value if conversion is successful, otherwise the default value.
#             """
#             try:
#                 return int(value)
#             except ValueError:
#                 return default

#         return {'convert_to_int': convert_to_int}
