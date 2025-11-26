class DynamicConfig:
    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(
                    self, key, DynamicConfig(value)
                )  # Recursively convert nested dictionaries
            elif isinstance(value, list):
                # Handle lists of dictionaries or other types
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_list.append(DynamicConfig(item))
                    else:
                        new_list.append(item)
                setattr(self, key, new_list)
            else:
                setattr(self, key, value)
