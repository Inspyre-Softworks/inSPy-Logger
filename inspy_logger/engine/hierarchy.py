class HierarchyManager:
    """Own child registration and lookup for an InspyLogger."""

    def __init__(self, owner):
        self.owner = owner
        self.children = []

    def clear(self):
        self.children.clear()

    def names(self):
        return [child.name for child in self.children]

    def find(self, name, case_sensitive=True, exact_match=False):
        results = []
        search_name = name if case_sensitive else name.lower()

        for child in self.children:
            child_name = child.name if case_sensitive else child.name.lower()
            if exact_match and search_name == child_name:
                return child
            if not exact_match and search_name in child_name:
                results.append(child)
        return results

    def get_child(self, name, console_level=None, file_level=None, **kwargs):
        current_logger = self.owner

        for part in name.split("."):
            full_name = f"{current_logger.name}.{part}"
            found = current_logger.find_child_by_name(full_name, exact_match=True)
            if found:
                current_logger = found
                continue

            child_kwargs = dict(kwargs)
            child_kwargs.setdefault("no_file_logging", current_logger.no_file_logging)
            child_kwargs.setdefault("file_path", current_logger.file_path.parent)
            child_kwargs.setdefault("file_name", current_logger.file_path.name)
            child = current_logger.__class__(
                name=full_name,
                console_level=(
                    current_logger.console_level
                    if console_level is None
                    else console_level
                ),
                file_level=(
                    current_logger.file_level if file_level is None else file_level
                ),
                parent=current_logger,
                **child_kwargs,
            )
            current_logger.children.append(child)
            current_logger = child

        return current_logger
