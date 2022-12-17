#Copyright (C) 2022 Komeil Majidi.
import bpy
import bmesh
import numpy as np
from mathutils import Vector;
import math;
import os;

class VATSettingsProperties(bpy.types.PropertyGroup):
    maxValue: bpy.props.FloatProperty(name="Max Value",default = 5 );
    minValue: bpy.props.FloatProperty(name="Min Value",default =-5);
    exportNormal : bpy.props.BoolProperty(name="Export Normal",default=True);
    exportVertex : bpy.props.BoolProperty(name="Export Vertex",default=True);
    outputPath : bpy.props.StringProperty(name="Output Path",default = "D:\\Output\\",subtype='DIR_PATH');
    items = [
            ('0', 'UV0', ""),
            ('1', 'UV1', ""),
            ('2', 'UV2', ""),
            ('3', 'UV3', ""),
            ('4', 'UV4', ""),
            ('5', 'UV5', ""),
            ('6', 'UV6', ""),
            ('7', 'UV7', ""),
        ]
    formatItem = [
            ('PNG', 'PNG', ""),
            ('jpg', 'JPEG', ""),
            ('TARGA', 'TARGA', ""),
            ('HDR', 'HDR', ""),
            ('OPEN_EXR', 'OPEN_EXR', "")
        ]
    colorSpaceItem = [
            ('Gamma', 'Gamma', ""),
            ('Linear', 'Linear', "")
        ]
    writeModeItem = [
            ('SingleRaw', 'SingleRaw', ""),
            ('MultipleRaw', 'MultipleRaw', "")
        ]
    WriteUvID: bpy.props.EnumProperty(
        items=items,
        name="UV ",
        default=None,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)
    fileFormat: bpy.props.EnumProperty(
        items=formatItem,
        default=None,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)
        
    colorSpace: bpy.props.EnumProperty(
        items=colorSpaceItem,
        default=None,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)
        
    writeMode: bpy.props.EnumProperty(
        items=writeModeItem,
        default=None,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)
    
class VATPanel(bpy.types.Panel):
    """VAT Panel"""
    bl_label = "Vertex Animation Texture"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        scene = context.scene
        settings =  scene.VAT_Settings
        
        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")
                
        row = layout.row()
        row.prop(settings,"minValue");
        row.prop(settings,"maxValue");
        
        row = layout.row()
        row.prop(settings,"exportVertex");
        row.prop(settings,"exportNormal");
                
        row = layout.row()
        row.prop(settings,"WriteUvID");
        
        row = layout.row()
        row.prop(settings,"fileFormat");
        
        row = layout.row()
        row.prop(settings,"colorSpace");
        
        row = layout.row()
        row.prop(settings,"writeMode");
        
        if(settings.writeMode=='MultipleRaw'):
            row = layout.row()
            row.prop(settings,"resolution");
                        
        row = layout.row()
        row.prop(settings,"outputPath");
                    
        row = layout.row()
        row.operator("object.generate_vat")

class GenerateVATOperator(bpy.types.Operator):
    
    bl_idname = "object.generate_vat"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        scene = context.scene
        settings =  scene.VAT_Settings
                 
        maxValue = settings.maxValue;
        minValue = settings.minValue;
        frameNumber = scene.frame_end-abs(scene.frame_start)+1;
        frameStart = scene.frame_start;
        
        powValue = 1;
        
        if(settings.colorSpace=='Gamma'):
            powValue = 2.2;
        elif(settings.colorSpace=='Linear'):
            powValue =1;
        print(settings.colorSpace);    
        ExportNormal = settings.exportNormal;
        ExportVertex = settings.exportVertex;

        rangeValue = maxValue-minValue;
        formatDic = {'PNG':'png',
                     'TARGA':'tga',
                     'HDR':'hdr',
                     'OPEN_EXR':'exr'
                     }
        print(frameNumber);
        
        

        if(not os.path.exists(settings.outputPath)):
            os.makedirs(settings.outputPath);
   
        if(settings.outputPath[len(settings.outputPath)-1] !='/' and settings.outputPath[len(settings.outputPath)-1] !='\\'):
            settings.outputPath +='\\';
            
        
        def to01(v):
            if(v>maxValue):
                return 1;
            if(v<minValue):
                return 0;
            return (v-minValue)/rangeValue;


        def createImage(name,w,h,alpha):
            img = bpy.data.images.get(name);
            if(img!=None):
                bpy.data.images.remove(img);
                img = None;
            img = bpy.data.images.new(name, width=w, height=h, alpha=alpha, float_buffer=True);
            img.colorspace_settings.name = 'Raw'
            return img;
    
        me = context.object.data;
        object = context.object;
        dg = context.evaluated_depsgraph_get();

        if(dg==None):
            print("dg is none!!");
        
        bpy.context.scene.frame_set(frameStart);
        bm = bmesh.new();
        bm.from_mesh(me);
        bmesh.ops.triangulate(bm, faces=bm.faces);


        vertNum =len(bm.faces)*3

        unitOffset = 1.0 /vertNum;
        half_offset = unitOffset*(0.5);
                        
        id = 0;
        uv_layer = bm.loops.layers.uv.active;
              
        uvNumber = len(bm.loops.layers.uv.values());
        uvIndex = (int(settings.WriteUvID))+1;
        if(uvNumber<uvIndex):
            for i in range(uvNumber,uvIndex):
                bm.loops.layers.uv.new();
        
        uvIndex = 0;
        for uv in bm.loops.layers.uv.values():
            if(str(uvIndex) == (settings.WriteUvID)):
                uv_layer = uv;
                break;
           uvIndex =uvIndex+1;
        uv_layer = bm.loops.layers.uv.values()[uvIndex-1];
        
        
        if(settings.writeMode=='SingleRaw'):
            for f in bm.faces:
                for loop_data in f.loops:
                    loop_data[uv_layer].uv.x = id*unitOffset+half_offset;
                    loop_data[uv_layer].uv.y = 0.0;
                    id = id +1;
        elif(settings.writeMode=='MultipleRaw'):
            yunitoffset = 1.0/( math.ceil(vertNum*1.0/settings.resolution)*frameNumber)
            xunitoffset = 1.0/( settings.resolution)
            yhalf_offset=0.5*yunitoffset;
            xhalf_offset=0.5*xunitoffset;
            
            for f in bm.faces:
                for loop_data in f.loops:
                    loop_data[uv_layer].uv.x = (id%settings.resolution)*xunitoffset + xhalf_offset;
                    loop_data[uv_layer].uv.y = (int)(id/settings.resolution)*yunitoffset + yhalf_offset;
                    id = id +1;
        
        bm.to_mesh(me);       
        
        space = 0;
        if(settings.writeMode=='SingleRaw'):
            width = vertNum;
            height = frameNumber;
            space = 0;
        elif(settings.writeMode=='MultipleRaw'):
            width = settings.resolution;
            height = math.ceil(vertNum*1.0/settings.resolution)*frameNumber;
            space =  math.ceil(vertNum*1.0/settings.resolution)*settings.resolution-vertNum;
            space = space*4;
            
        print("space= %s" % space);
        print("Verts Number = %s" % vertNum);
        print("width = %s" % width);
        print("height = %s" % height);
             
        if(ExportVertex):
            vertex_data = np.ones(width*height*4);
            vimg = createImage("Vertex_Texture",width,height,False);
        if(ExportNormal):
            normal_data = np.ones(width*height*4);
            nimg = createImage("Normal_Texture",width,height,False);

        index = 0;
                 
        for frame in range(frameNumber):
            for f in bm.faces:
                for v in f.verts:         
                    if(ExportVertex):
                        wm = object.matrix_world.copy()
                        pos = object.matrix_world;
                        x = to01(pos.x);
                        y = to01(pos.y);
                        z = to01(pos.z);
                        vertex_data[index  ] = math.pow(x,powValue);
                        vertex_data[index+1] = math.pow(z,powValue);
                        vertex_data[index+2] = math.pow(y,powValue);
                        vertex_data[index+3] = 1;
                    if(ExportNormal):
                        vn = v.normal;
                        normal_data[index  ] = math.pow((vn.x+1)/2.0,powValue);
                        normal_data[index+1] = math.pow((vn.z+1)/2.0,powValue);
                        normal_data[index+2] = math.pow((vn.y+1)/2.0,powValue);
                        normal_data[index+3] = 1;
                                
                    index =index+4;
            index = index + space;        
            bm = bmesh.new();
            bm.from_object(object,dg);
            bmesh.ops.triangulate(bm, faces=bm.faces);
            bpy.context.scene.frame_set(frameStart + frame+1);

        if(ExportVertex):
            vimg.pixels[:] = vertex_data;
            vimg.file_format = settings.fileFormat;
            vimg.filepath_raw = settings.outputPath+"VertexTexture."+formatDic[settings.fileFormat];
            vimg.save();
        if(ExportNormal):    
            nimg.pixels[:] = normal_data;
            nimg.file_format = settings.fileFormat;
            nimg.filepath_raw = settings.outputPath+"NormalTexture."+formatDic[settings.fileFormat];
            nimg.save();
            
        del bm
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GenerateVATOperator);
    bpy.utils.register_class(VATPanel);
    bpy.utils.register_class(VATSettingsProperties);
    bpy.types.Scene.VAT_Settings = bpy.props.PointerProperty(type = VATSettingsProperties)

def unregister():
    bpy.utils.unregister_class(GenerateVATOperator);
    bpy.utils.unregister_class(VATPanel);
    bpy.utils.unregister_class(VATSettingsProperties);
    del bpy.types.Scene.VAT_Settings


if __name__ == "__main__":
    register()


