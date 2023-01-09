#Copyright (C) 2022 Komeil Majidi.
import bpy
import bmesh
import numpy as np
from mathutils import Vector;
import math;
from lmath import box_create, box_expand_point



maxValue = 5;
minValue = -5;
frameNumber = 5;
frameStart = 0;

ExportNormal = True;
ExportVertex = True;

rangeValue = maxValue-minValue;

me = bpy.context.object.data;
object = bpy.context.object;
dg = bpy.context.evaluated_depsgraph_get();

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

    return img;

if(dg==None):
    print("none!");

bpy.context.scene.frame_set(0);
bm = bmesh.new();
bm.from_object(object,dg);
bmesh.ops.triangulate(bm, faces=bm.faces);


vertNum =len(bm.faces)*3

unitOffset = 1.0 /vertNum;
half_offset = unitOffset*(0.5);

id = 0;

uv_layer = bm.loops.layers.uv.active;

for f in bm.faces:
    for loop_data in f.loops:
        loop_data[uv_layer].uv.x = id*unitOffset+half_offset;
        loop_data[uv_layer].uv.y = 0.0;
        id = id +1;
bm.to_mesh(me);       

width = vertNum;
height = frameNumber;

print("Vertex Number = %s" % vertNum);
print("width = %s" % width);
print("height = %s" % height);

if(ExportVertex):
    vertex_data = np.ones(width*height*4);
    vimg = createImage("Vertex_Texture",width,height,False);
if(ExportNormal):
    normal_data = np.ones(width*height*4);
    nimg = createImage("Normal_Texture",width,height,False);

index = 0;
 
   

for frame in range(height):
    for f in bm.faces:
        for v in f.verts:         

            if(ExportVertex):
                wm = object.matrix_world.copy()
                pos = object.matrix_world@v.co;

                x = to01(pos.x);
                y = to01(pos.y);
                z = to01(pos.z);
                vertex_data[index  ] = x;
                vertex_data[index+1] = y;
                vertex_data[index+2] = z;
                vertex_data[index+3] = 1;

            if(ExportNormal):
                vn = v.normal;
                normal_data[index  ] = (vn.x+1)/2.0;
                normal_data[index+1] = (vn.y+1)/2.0;
                normal_data[index+2] = (vn.z+1)/2.0;
                normal_data[index+3] = 1;
                        
            index =index+4;
        
    bm = bmesh.new();
    bm.from_object(object,dg);
    bmesh.ops.triangulate(bm, faces=bm.faces);

    bpy.context.scene.frame_set(frameStart + frame);

   
if(ExportVertex):
    vimg.pixels[:] = vertex_data;
if(ExportNormal):    
    nimg.pixels[:] = normal_data;

del bm

def parse_obj(filename, swapyz=False):
    print("parsing " + filename)

    vertices = []
    faces = []

    box = box_create()

    for line in open(filename, "r"):
        if line.startswith('#'): continue

        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = list(map(float, values[1:4]))
            if swapyz:
                v = v[0], v[2], v[1]
            box_expand_point(box, v)
            vertices.append(v)
        elif values[0] == 'f':
            v0 = int(values[1].split('/')[0]) - 1
            v1 = int(values[2].split('/')[0]) - 1
            v2 = int(values[3].split('/')[0]) - 1
            faces.append((v0, v1, v2))

    model = {
        'vertices': vertices,
        'vertex_count': len(vertices),
        'faces': faces,
        'face_count': len(faces),
        'box': box
    }

    return model