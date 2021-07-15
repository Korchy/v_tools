# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/v_tools/

from bpy.types import Panel
from bpy.utils import register_class, unregister_class


class V_TOOLS_PT_edges_loops(Panel):
    bl_idname = 'V_TOOLS_PT_edges_loops'
    bl_label = 'Edges/Loops'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VTools'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.operator('v_tools.loop_resolve', icon='MOD_SIMPLIFY')
        if context.window_manager.v_tools_props.loop_resolve_relative:
            box.prop(
                data=context.window_manager.v_tools_props,
                property='loop_resolve_step'
            )
        else:
            box.prop(
                data=context.window_manager.v_tools_props,
                property='loop_resolve_dist'
            )
        box.prop(
            data=context.window_manager.v_tools_props,
            property='loop_resolve_relative',
            toggle=True
        )


def register():
    register_class(V_TOOLS_PT_edges_loops)


def unregister():
    unregister_class(V_TOOLS_PT_edges_loops)
