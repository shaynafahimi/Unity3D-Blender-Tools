bl_info = {
	"name": "Blender-VF-Exporter",
	"author": "Komeil Majidi /Shayna Fahimi ",
	"version": (1, 0, 0),
	"blender": (3, 3, 1),
	"location": "Scene > VF Tools > Exporter",
	"category": "3D View"}

import bpy
from bpy.app.handlers import persistent
import mathutils
import numpy as np

class VFDELIVERY_OT_file(bpy.types.Operator):
	bl_idname = "vfdelivery.file"
	bl_label = "Deliver File"
	bl_description = "Quickly export selected objects or collection to a specified directory"

	def execute(self, context):

		location = bpy.context.scene.vf_delivery_settings.file_location
		format = bpy.context.scene.vf_delivery_settings.file_type
		combined = True if bpy.context.scene.vf_delivery_settings.file_grouping == "COMBINED" else False
		file_format = "." + format.lower()
	
		uvmap_experimental = bpy.context.scene.vf_delivery_settings.uvmap_experimental

		mode = bpy.context.active_object.mode

		bpy.ops.object.mode_set(mode='OBJECT')

		if bpy.context.object and bpy.context.object.select_get():
			file_name = bpy.context.active_object.name
		else:
			file_name = bpy.context.collection.name
			for obj in bpy.context.collection.all_objects:
				obj.select_set(True)

		if format != "CSV":
			bpy.ops.ed.undo_push()

			for obj in bpy.context.selected_objects:
				if obj.type != "MESH":
					obj.select_set(False)

		if format == "ABC" or format == "FBX" or format == "GLB":

			bpy.ops.ed.undo_push()
			undo_steps = 1

			if bpy.context.preferences.addons['VF_delivery'].preferences.enable_uvmap_experimental and uvmap_experimental:

				for obj in bpy.context.selected_objects:
					if obj.type == "MESH":
						bpy.context.view_layer.objects.active = obj

						if len(obj.modifiers) > 0:
							bpy.ops.ed.undo_push()
							undo_steps += 1
							bpy.ops.object.apply_all_modifiers()

						if obj.data.attributes.get("UVMap") and obj.data.attributes.active.name == "UVMap":
							bpy.ops.ed.undo_push()
							undo_steps += 1
							bpy.ops.geometry.attribute_convert(mode='UV_MAP')

			for obj in bpy.context.selected_objects:
				if not combined:
					print("INDIVIDUAL")
					print("selected: " + str(len(bpy.context.selected_objects)))
					for selobj in bpy.context.selected_objects:
						selobj.select_set(False)
					obj.select_set(True)
					file_name = obj.name
					print("selected: " + str(len(bpy.context.selected_objects)))

				if format == "ABC":
					print("EXPORT: ABC")
					bpy.ops.wm.alembic_export(
						filepath=location + file_name + file_format,
						check_existing=False, 
						start=0,
						end=0,
						xsamples=1,
						gsamples=1,
						selected=True,
						visible_objects_only=False,
						flatten=False,
						uvs=True,
						packuv=False,
						normals=True,
						vcolors=True, 
						orcos=True,
						face_sets=False,
						subdiv_schema=False,
						apply_subdiv=False,
						curves_as_mesh=False,
						use_instancing=True,
						global_scale=1.0,
						triangulate=False,
						quad_method='SHORTEST_DIAGONAL',
						ngon_method='BEAUTY',
						export_hair=True,
						export_particles=True,
						export_custom_properties=False, 
						evaluation_mode='RENDER')

				elif format == "FBX":
					print("EXPORT: FBX")
					bpy.ops.export_scene.fbx(
						filepath=location + file_name + file_format,
						check_existing=False,
						use_selection=True,
						use_visible=True,
						use_active_collection=False, 

						global_scale=1.0,
						apply_unit_scale=True,
						apply_scale_options='FBX_SCALE_NONE', 
						use_space_transform=True,
						axis_forward='-Z',
						axis_up='Y',
						object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'},
						bake_space_transform=True, 

						use_mesh_modifiers=True,
						use_mesh_modifiers_render=True,
						mesh_smooth_type='OFF',
						use_subsurf=False,
						use_mesh_edges=False,
						use_tspace=False,
						use_triangles=True, 
						use_custom_props=False,

						use_armature_deform_only=True,
						add_leaf_bones=False, 
						primary_bone_axis='X', 
						secondary_bone_axis='Y', 
						armature_nodetype='NULL',

						bake_anim=True,
						bake_anim_use_all_bones=True,
						bake_anim_use_nla_strips=True,
						bake_anim_use_all_actions=True,
						bake_anim_force_startend_keying=True,
						bake_anim_step=1.0,
						bake_anim_simplify_factor=1.0,

						path_mode='AUTO',
						embed_textures=False,
						batch_mode='OFF',
						use_batch_own_dir=False,
						use_metadata=True)

				elif format == "GLB":
					print("EXPORT: GLB")
					bpy.ops.export_scene.gltf(
						filepath=location + file_name + file_format,
						check_existing=False, 
						export_format='GLB',
						export_copyright='',

						export_image_format='JPEG',
						export_texcoords=True,
						export_normals=True,
						export_draco_mesh_compression_enable=True,
						export_draco_mesh_compression_level=6,
						export_draco_position_quantization=14,
						export_draco_normal_quantization=10,
						export_draco_texcoord_quantization=12,
						export_draco_color_quantization=10,
						export_draco_generic_quantization=12,

						export_tangents=False,
						export_materials='EXPORT',
						export_colors=True,
						use_mesh_edges=False,
						use_mesh_vertices=False,
						export_cameras=False,

						use_selection=True,
						use_visible=True,
						use_renderable=True,
						use_active_collection=False, 
						use_active_scene=False,

						export_extras=False,
						export_yup=True,
						export_apply=True,

						export_animations=True,
						export_frame_range=True,
						export_frame_step=1,
						export_force_sampling=True,
						export_nla_strips=True,
						export_def_bones=True,
						export_optimize_animation_size=True,
						export_current_frame=False,
						export_skins=True,
						export_all_influences=False,

						export_morph=True,
						export_morph_normal=True,
						export_morph_tangent=False,

						export_lights=False,
						will_save_settings=False,
						filter_glob='*.glb;*.gltf')

				if combined:
					break

			for i in range(undo_steps):
				bpy.ops.ed.undo()
		elif format == "STL":
			batch = 'OFF' if combined else 'OBJECT'
			output = location + file_name + file_format if combined else location
			bpy.ops.export_mesh.stl(
				filepath=output,
				ascii=False,
				check_existing=False, # Dangerous!
				use_selection=True,
				batch_mode=batch,

				global_scale=1.0,
				use_scene_unit=False,
				use_mesh_modifiers=True,

				axis_forward='Y',
				axis_up='Z',
				filter_glob='*.stl')

		elif format == "CSV":

			frame_current = bpy.context.scene.frame_current

			frame_start = bpy.context.scene.frame_start
			frame_end = bpy.context.scene.frame_end
			space = bpy.context.scene.vf_delivery_settings.csv_position

			for obj in bpy.context.selected_objects:

				array = [["x","y","z"]]
				for i in range(frame_start, frame_end + 1):
					bpy.context.scene.frame_set(i)
					loc, rot, scale = obj.matrix_world.decompose() if space == "WORLD" else obj.matrix_local.decompose()
					array.append([loc.x, loc.y, loc.z])

				np.savetxt(
					location + obj.name + file_format,
					array,
					delimiter =",",
					newline='\n',
					fmt ='% s'
					)

			bpy.context.scene.frame_set(frame_current)

		if format != "CSV":
			bpy.ops.ed.undo()

		bpy.ops.object.mode_set(mode=mode)
		return {'FINISHED'}


class vfDeliveryPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__


	enable_uvmap_experimental: bpy.props.BoolProperty(
		name='Enable experimental UVMap conversion',
		description='Attempts to convert the first named attribute output from a Geometry Nodes modifier into a UV map recognisable by file exporters',
		default=False)


	def draw(self, context):
		layout = self.layout
		layout.prop(self, "enable_uvmap_experimental")

class vfDeliverySettings(bpy.types.PropertyGroup):
	file_type: bpy.props.EnumProperty(
		name='Pipeline',
		description='Sets the format for delivery output',
		items=[
			('ABC', 'ABC — Static', 'Export Alembic binary file from frame 0'),
			('FBX', 'FBX — Unity3D', 'Export FBX binary file for Unity'),
			('GLB', 'GLB — ThreeJS', 'Export GLTF compressed binary file for ThreeJS'),
			('STL', 'STL — 3D Printing', 'Export individual STL file of each selected object for 3D printing'),
			('CSV', 'CSV — Position', 'Export CSV file of the selected object\'s position for all frames within the render range')
			],
		default='STL')
	file_location: bpy.props.StringProperty(
		name="Delivery Location",
		description="Delivery location for all exported files",
		default="/",
		maxlen=4096,
		subtype="DIR_PATH")
	uvmap_experimental: bpy.props.BoolProperty(
		name="Convert UVMap Attribute",
		description="Attempts to export UVMap data by applying all modifiers and converting any \"UVMap\" named attributes to an actual UV map",
		default=False)
	file_grouping: bpy.props.EnumProperty(
		name='Grouping',
		description='Sets combined or individual file outputs',
		items=[
			('COMBINED', 'Combined', 'Export selection in one file'),
			('INDIVIDUAL', 'Individual', 'Export selection as individual files')
			],
		default='COMBINED')
	csv_position: bpy.props.EnumProperty(
		name='Position',
		description='Sets local or world space coordinates',
		items=[
			('WORLD', 'World', 'World space'),
			('LOCAL', 'Local', 'Local object space')
			],
		default='WORLD')

class VFTOOLS_PT_delivery(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VF Tools'
	bl_order = 0
	bl_options = {'DEFAULT_CLOSED'}
	bl_label = "Delivery"
	bl_idname = "VFTOOLS_EXPORTER"

	@classmethod
	def poll(cls, context):
		return True

	def draw_header(self, context):
		try:
			layout = self.layout
		except Exception as exc:
			print(str(exc) + " | Error in VF Delivery panel header")

	def draw(self, context):
		try:
			file_format = "." + context.scene.vf_delivery_settings.file_type.lower()
			button_enable = True
			button_icon = "FILE"
			button_title = ''
			show_group = True
			show_uvmap = bpy.context.preferences.addons['VF_delivery'].preferences.enable_uvmap_experimental
			show_csv = False
			object_count = 0

			if bpy.context.object and bpy.context.object.select_get():
				if context.scene.vf_delivery_settings.file_type == "CSV":
					object_count = len(bpy.context.selected_objects)
				else:
					object_count = [obj.type for obj in bpy.context.selected_objects].count("MESH")

				button_icon = "OUTLINER_OB_MESH"

				if (object_count > 1 and context.scene.vf_delivery_settings.file_grouping == "COMBINED" and not context.scene.vf_delivery_settings.file_type == "CSV"):
					button_title = bpy.context.active_object.name + file_format
				elif object_count == 1:
					if bpy.context.active_object.type != "MESH" and context.scene.vf_delivery_settings.file_grouping == "INDIVIDUAL":
						for obj in bpy.context.selected_objects:
							if obj.type == "MESH":
								button_title = obj.name + file_format
					else:
						button_title = bpy.context.active_object.name + file_format
				else:
					button_title = str(object_count) + " files"

			else:
				if context.scene.vf_delivery_settings.file_type == "CSV":
					object_count = len(bpy.context.collection.all_objects)
				else:
					object_count = [obj.type for obj in bpy.context.collection.all_objects].count("MESH")

				button_icon = "OUTLINER_COLLECTION"

				if context.scene.vf_delivery_settings.file_grouping == "COMBINED" and not context.scene.vf_delivery_settings.file_type == "CSV":
					button_title = bpy.context.collection.name + file_format
				else:
					button_title = str(object_count) + " files"

			if object_count == 0:
				button_enable = False
				button_icon = "X"
				if context.scene.vf_delivery_settings.file_type == "CSV":
					button_title = "Select object"
				else:
					button_title = "Select mesh"

			if context.scene.vf_delivery_settings.file_type == "CSV":
				show_group = False
				show_uvmap = False
				show_csv = True
			elif context.scene.vf_delivery_settings.file_type == "STL":
				show_uvmap = False
			layout = self.layout
			layout.use_property_decorate = False # No animation

			layout.prop(context.scene.vf_delivery_settings, 'file_location', text='')
			layout.prop(context.scene.vf_delivery_settings, 'file_type', text='')

			if show_uvmap:
				layout.prop(context.scene.vf_delivery_settings, 'uvmap_experimental')

			if show_group:
				layout.prop(context.scene.vf_delivery_settings, 'file_grouping', expand=True)

			if show_csv:
				layout.prop(context.scene.vf_delivery_settings, 'csv_position', expand=True)

			if button_enable:
				layout.operator(VFDELIVERY_OT_file.bl_idname, text=button_title, icon=button_icon)
			else:
				disabled = layout.row()
				disabled.active = False
				disabled.enabled = False
				disabled.operator(VFDELIVERY_OT_file.bl_idname, text=button_title, icon=button_icon)

		except Exception as exc:
			print(str(exc) + " | Error in VF Delivery panel")

classes = (VFDELIVERY_OT_file, vfDeliveryPreferences, vfDeliverySettings, VFTOOLS_PT_delivery)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.vf_delivery_settings = bpy.props.PointerProperty(type=vfDeliverySettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.vf_delivery_settings

if __name__ == "__main__":
	register()