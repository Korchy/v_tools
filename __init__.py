# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/v_tools/

from . import v_tools_ops
from . import v_tools_ui
from . import v_tools_props


bl_info = {
    'name': 'VTools',
    'category': 'All',
    'author': '1D, fork by Nikita Akimov',
    'version': (1, 0, 0),
    'blender': (2, 93, 0),
    'location': 'View 3D window - N panel - VTools',
    'wiki_url': '',
    'tracker_url': '',
    'description': 'Selective fork of the 1D Scripts'
}


def register():
    v_tools_props.register()
    v_tools_ops.register()
    v_tools_ui.register()


def unregister():
    v_tools_ui.unregister()
    v_tools_ops.unregister()
    v_tools_props.unregister()


if __name__ == '__main__':
    register()
