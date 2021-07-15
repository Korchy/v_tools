# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/v_tools/

from bpy.props import BoolProperty, PointerProperty, IntProperty, FloatProperty
from bpy.types import PropertyGroup, WindowManager
from bpy.utils import register_class, unregister_class


class V_TOOLS_Props(PropertyGroup):

    loop_resolve_relative: BoolProperty(
        name='Loop Improve Relative',
        default=True
    )
    loop_resolve_step: IntProperty(
        name='Step',
        default=5,
        min=3
    )
    loop_resolve_dist: FloatProperty(
        name='Dist',
        default=1.0,
        min=1e-4,
        precision=4
    )


def register():
    register_class(V_TOOLS_Props)
    WindowManager.v_tools_props = PointerProperty(type=V_TOOLS_Props)


def unregister():
    del WindowManager.v_tools_props
    unregister_class(V_TOOLS_Props)
