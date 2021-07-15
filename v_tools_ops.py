# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/v_tools/

from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from .v_tools import VTools


class V_TOOLS_OT_loop_resolve(Operator):
    bl_idname = 'v_tools.loop_resolve'
    bl_label = 'Loop Improve'
    bl_description = 'Resolve loop density by Bezier in vertex mode or split edges in edges mode'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.window_manager.v_tools_props.loop_resolve_relative:
            VTools.loop_resolve(
                context=context,
                STEP=context.window_manager.v_tools_props.loop_resolve_step,
                dist=None
            )
        else:
            VTools.loop_resolve(
                context=context,
                STEP=context.window_manager.v_tools_props.loop_resolve_step,
                dist=context.window_manager.v_tools_props.loop_resolve_dist
            )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return bool(context.active_object)


def register():
    register_class(V_TOOLS_OT_loop_resolve)


def unregister():
    unregister_class(V_TOOLS_OT_loop_resolve)
