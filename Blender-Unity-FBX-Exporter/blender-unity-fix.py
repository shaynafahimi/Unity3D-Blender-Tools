bl_info = {
    "name": "Unity Problem Fix",
    "category": "Object",
    "blender": (2, 80, 0),
    "location": "Object > Apply > Unity Fix",
}
import bpy
from math import pi
from mathutils import Vector
from mathutils import Matrix

class NOTHKE_OT_unity_rotation_fix(bpy.types.Operator):
    """Fixes rotation (swaps Y and Z axes) for exporting to Unity"""
    bl_idname = "object.unity_rotation_fix"
    bl_label = "Apply Unity Rotation Fix"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        original_active_object = context.view_layer.objects.active

        layer = context.view_layer
                        
        selected_objects = []
        for obj in context.selected_objects:
            selected_objects.append(obj)
            
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selected_objects:

            obj.select_set(True)
            layer.objects.active = obj
            
            original_rotation = [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]]
                  

            obj.rotation_euler = [0, 0, 0]

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False, properties=False)

 
            obj.rotation_euler[0] = pi * 90 / 180
            obj.rotation_euler[2] = pi * 180 / 180
            
            layer.objects.active = obj
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False, properties=False)
            
            obj.rotation_euler[0] = pi * -90 / 180
            obj.rotation_euler[1] = pi * -180 / 180
            
            obj.rotation_euler[0] -= original_rotation[0]
            obj.rotation_euler[1] += original_rotation[1]
            obj.rotation_euler[2] += original_rotation[2]
            
            bpy.context.view_layer.update()

            layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')
             
        for obj in selected_objects:
            obj.select_set(True)

        context.view_layer.objects.active = original_active_object

def menu_draw(self, context):
    layout = self.layout
    layout.operator("object.unity_rotation_fix", text="Unity Rotation Fix")

def register():
    bpy.utils.register_class(NOTHKE_OT_unity_rotation_fix)
    bpy.types.VIEW3D_MT_object_apply.append(menu_draw)

def unregister():
    bpy.utils.unregister_class(NOTHKE_OT_unity_rotation_fix)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_draw)

if __name__ == "__main__":
    register()