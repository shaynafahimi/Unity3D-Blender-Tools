bl_info = {
	"name": "Unity FBX format",
	"version": (1, 3, 1),
	"blender": (2, 80, 0),
	"location": "File > Export > Unity FBX",
	"category": "Import-Export",
}


import bpy
import mathutils
import math
import bpy, re
import numpy as np
shared_data = dict()
hidden_collections = []
hidden_objects = []
disabled_collections = []
disabled_objects = []


def unhide_collections(col):
	global hidden_collections
	global disabled_collections

	if col.exclude:
		return
	hidden = [item for item in col.children if not item.exclude and item.hide_viewport]
	for item in hidden:
		item.hide_viewport = False

	hidden_collections.extend(hidden)

	disabled = [item for item in col.children if not item.exclude and item.collection.hide_viewport]
	for item in disabled:
		item.collection.hide_viewport = False

	disabled_collections.extend(disabled)

	for item in col.children:
		unhide_collections(item)


def unhide_objects():
	global hidden_objects
	global disabled_objects

	view_layer_objects = [ob for ob in bpy.data.objects if ob.name in bpy.context.view_layer.objects]

	for ob in view_layer_objects:
		if ob.hide_get():
			hidden_objects.append(ob)
			ob.hide_set(False)
		if ob.hide_viewport:
			disabled_objects.append(ob)
			ob.hide_viewport = False


def make_single_user_data():
	global shared_data

	for ob in bpy.data.objects:
		if ob.data and ob.data.users > 1:
			if ob.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}:
				users = [user for user in bpy.data.objects if user.data == ob.data]

				modifiers = 0
				for user in users:
					modifiers += len([mod for mod in user.modifiers if mod.show_viewport])
				if modifiers == 0:
					shared_data[ob.name] = ob.data

			ob.data = ob.data.copy()


def apply_object_modifiers():
	bpy.ops.object.select_all(action='DESELECT')
	for ob in bpy.data.objects:
		if ob.name in bpy.context.view_layer.objects:
			bypass_modifiers = False
			for mod in ob.modifiers:
				if mod.type == 'ARMATURE':
					bypass_modifiers = True
			if not bypass_modifiers:
				ob.select_set(True)

	if bpy.ops.object.convert.poll():
		bpy.ops.object.convert(target='MESH')


def reset_parent_inverse(ob):
	if (ob.parent):
		mat_world = ob.matrix_world.copy()
		ob.matrix_parent_inverse.identity()
		ob.matrix_basis = ob.parent.matrix_world.inverted() @ mat_world


def apply_rotation(ob):
	bpy.ops.object.select_all(action='DESELECT')
	ob.select_set(True)
	bpy.ops.object.transform_apply(location = False, rotation = True, scale = False)


def fix_object(ob):
	if ob.name in bpy.context.view_layer.objects:

		reset_parent_inverse(ob)

		mat_original = ob.matrix_local.copy()
		ob.matrix_local = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

		apply_rotation(ob)

		ob.matrix_local = mat_original @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

	for child in ob.children:
		fix_object(child)


def export_unity_fbx(context, filepath, active_collection, selected_objects, deform_bones, leaf_bones, primary_bone_axis, secondary_bone_axis):
	global shared_data
	global hidden_collections
	global hidden_objects
	global disabled_collections
	global disabled_objects

	print("Preparing 3D model for Unity...")

	root_objects = [item for item in bpy.data.objects if (item.type == "EMPTY" or item.type == "MESH" or item.type == "ARMATURE") and not item.parent]

	bpy.ops.ed.undo_push(message="Prepare Unity FBX")

	shared_data = dict()
	hidden_collections = []
	hidden_objects = []
	disabled_collections = []
	disabled_objects = []

	selection = bpy.context.selected_objects

	bpy.ops.object.mode_set(mode="OBJECT")

	unhide_collections(bpy.context.view_layer.layer_collection)
	unhide_objects()

	make_single_user_data()

	apply_object_modifiers()

	try:
		for ob in root_objects:
			print(ob.name)
			fix_object(ob)

		for item in shared_data:
			bpy.data.objects[item].data = shared_data[item]

		bpy.context.view_layer.update()

		for ob in hidden_objects:
			ob.hide_set(True)
		for ob in disabled_objects:
			ob.hide_viewport = True

		for col in hidden_collections:
			col.hide_viewport = True
		for col in disabled_collections:
			col.collection.hide_viewport = True

		bpy.ops.object.select_all(action='DESELECT')
		for ob in selection:
			ob.select_set(True)


		params = dict(filepath=filepath, apply_scale_options='FBX_SCALE_UNITS', object_types={'EMPTY', 'MESH', 'ARMATURE'}, use_active_collection=active_collection, use_selection=selected_objects, use_armature_deform_only=deform_bones, add_leaf_bones=leaf_bones, primary_bone_axis=primary_bone_axis, secondary_bone_axis=secondary_bone_axis)

		print("Invoking default FBX Exporter:", params)
		bpy.ops.export_scene.fbx(**params)

	except Exception as e:
		bpy.ops.ed.undo_push(message="")
		bpy.ops.ed.undo()
		bpy.ops.ed.undo_push(message="Export Unity FBX")
		print(e)
		print("File not saved.")
		return {'FINISHED'}


	bpy.ops.ed.undo_push(message="")
	bpy.ops.ed.undo()
	bpy.ops.ed.undo_push(message="Export Unity FBX")
	print("FBX file for Unity saved.")
	return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportUnityFbx(Operator, ExportHelper):
	"""FBX exporter compatible with Unity's coordinate and scaling system"""
	bl_idname = "export_scene.unity_fbx"
	bl_label = "Export Unity FBX"
	bl_options = {'UNDO_GROUPED'}
	filename_ext = ".fbx"

	filter_glob: StringProperty(
		default="*.fbx",
		options={'HIDDEN'},
		maxlen=255,  
	)


	active_collection: BoolProperty(
		name="Active Collection Only",
		description="Export objects in the active collection only (and its children). May be combined with Selected Objects Only.",
		default=False,
	)

	selected_objects: BoolProperty(
		name="Selected Objects Only",
		description="Export selected objects only. May be combined with Active Collection Only.",
		default=False,
	)

	deform_bones: BoolProperty(
		name="Only Deform Bones",
		description="Only write deforming bones (and non-deforming ones when they have deforming children)",
		default=False,
	)

	leaf_bones: BoolProperty(
		name="Add Leaf Bones",
		description="Append a final bone to the end of each chain to specify last bone length (use this when you intend to edit the armature from exported data)",
		default=False,
	)

	primary_bone_axis: EnumProperty(
			name="Primary Bone Axis",
			items=(('X', "X Axis", ""),
					('Y', "Y Axis", ""),
					('Z', "Z Axis", ""),
					('-X', "-X Axis", ""),
					('-Y', "-Y Axis", ""),
					('-Z', "-Z Axis", ""),
					),
			default='Y',
			)
	secondary_bone_axis: EnumProperty(
			name="Secondary Bone Axis",
			items=(('X', "X Axis", ""),
					('Y', "Y Axis", ""),
					('Z', "Z Axis", ""),
					('-X', "-X Axis", ""),
					('-Y', "-Y Axis", ""),
					('-Z', "-Z Axis", ""),
					),
			default='X',
			)

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.label(text = "Selection")
		row = layout.row()
		row.prop(self, "active_collection")
		row = layout.row()
		row.prop(self, "selected_objects")
		row = layout.row()
		row.label(text = "Armatures")
		row = layout.row()
		row.prop(self, "deform_bones")
		row = layout.row()
		row.prop(self, "leaf_bones")
		row = layout.row()
		row.label(text = "Bone Axes")
		row = layout.row()
		row.prop(self, "primary_bone_axis")
		row = layout.row()
		row.prop(self, "secondary_bone_axis")


	def execute(self, context):
		return export_unity_fbx(context, self.filepath, self.active_collection, self.selected_objects, self.deform_bones, self.leaf_bones, self.primary_bone_axis, self.secondary_bone_axis)

def menu_func_export(self, context):
	self.layout.operator(ExportUnityFbx.bl_idname, text="Unity FBX (.fbx)")


def register():
	bpy.utils.register_class(ExportUnityFbx)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ExportUnityFbx)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def report (self, item, error_or_info):
    self.report({error_or_info}, item)


def popup (lines, icon, title):
    def draw(self, context):
        for line in lines:
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def list_to_visual_list (list):
    return ", ".join(list)

    
def make_active_only (obj):
    bpy.ops.object.mode_set (mode='OBJECT')
    bpy.ops.object.select_all (action='DESELECT')
    obj.select_set (True)
    bpy.context.view_layer.objects.active = obj

    
def make_active (obj):
    bpy.context.view_layer.objects.active = obj  


def sn (line):
    for c in '/\:*?"<>|.,= '+"'":
        line = line.replace (c, '_')
    return (line)


def get_active_action (obj):
    if obj.animation_data is not None:
        return obj.animation_data.action


def is_str_blank (s):
    return s.replace (" ", "") == ""


def detect_mirrored_uvs (bm, uv_index):
    uv_layer = bm.loops.layers.uv[uv_index]
    mirrored_face_count = 0
    for face in bm.faces:
        uvs = [tuple(loop[uv_layer].uv) for loop in face.loops]
        x_coords, y_coords = zip (*uvs)
        result = 0.5 * np.array (np.dot(x_coords, np.roll(y_coords, 1)) - np.dot(y_coords, np.roll(x_coords, 1)))
        if result > 0:
            mirrored_face_count += 1
            break
    if mirrored_face_count > 0:
        return True
    else:
        return False


def clear_transformation (object):
    for c in object.constraints:
        c.mute = True
    object.location = [0, 0, 0]
    object.scale = [1, 1, 1]
    object.rotation_quaternion = [1, 0, 0, 0]
    object.rotation_euler = [0, 0, 0]
    object.rotation_axis_angle = [0, 0, 1, 0]

    
def clear_transformation_matrix (object):
    for c in object.constraints:
        c.mute = True
    object.matrix_world = Matrix()


def _gather_images(node_tree, images):
    for node in node_tree.nodes:
        if node.type == 'TEX_IMAGE' or node.type == 'TEX_ENVIRONMENT':
            images.add(node.image)
        elif node.type == 'GROUP':
            _gather_images(node.node_tree, images)


def gather_images_from_nodes (node_tree):
    images = set()
    _gather_images(node_tree, images)
    return set (images)


def reset_all_pose_bones(rig):
    zero_vec = (0, 0, 0)
    zero_quat = (1, 0, 0, 0)
    one_vec = (1, 1, 1)
    zero_axis_angle = (0, 0, 1, 0)

    for pbone in rig.pose.bones:
        pbone.location = zero_vec
        rm = pbone.rotation_mode
        if rm == "QUATERNION":
            pbone.rotation_quaternion = zero_quat
        elif rm == "AXIS_ANGLE":
            pbone.rotation_axis_angle = zero_axis_angle
        else:
            pbone.rotation_euler = zero_vec
        pbone.scale = one_vec


def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def clear_blender_collection(collection):
    for item in collection:
        collection.remove(item)


def set_active_action (obj, action):
    if getattr (obj, "animation_data") == None:
        obj.animation_data_create ()
    reset_all_pose_bones(obj)
    obj.animation_data.action = action


def can_be_converted_to_number (string):
    try:
        int(string)
        return True
    except:
        return False


def remove_dot_plus_three_numbers (name):
    if len(name) < 4:
        return name
    elif name[-4] == '.' and can_be_converted_to_number (name[-3:]):
        return name[:-4]
    else:
        return name


def make_lod_object_name_pattern():
    return re.compile("(.*)[_\\s]lod_?(\\d+)$", re.IGNORECASE)

def get_name_and_lod_index(lod_pattern, name):
    finds = re.findall(lod_pattern, name)
    if len(finds) == 1:
        info = finds[0]
        return (info[0], int(info[1]))
    else:
        return None


def set_bone_parent(ebones, name, parent_name):
    ebone = ebones.get(name)
    if ebone is not None:
        if parent_name == None:
            ebone.parent = None      
        else:
            ebone.parent = ebones.get(parent_name)

if __name__ == "__main__":
	register()

	# test call
	bpy.ops.export_scene.unity_fbx('INVOKE_DEFAULT')
