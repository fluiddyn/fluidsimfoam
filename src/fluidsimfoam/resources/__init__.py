"""Subpackage containing potential templates (actually empty for now)

"""

import jinja2


class BaseTemplates:
    @property
    def env(self):
        return jinja2.Environment(
            loader=jinja2.PackageLoader("fluidsimfoam", "resources"),
            undefined=jinja2.StrictUndefined,
            keep_trailing_newline=True,
        )

    def get_base_template(self, name):
        """Get a template from ``fluidsimfoam.resources``."""
        return self.env.get_template(name)


_templates = BaseTemplates()

get_base_template = _templates.get_base_template
