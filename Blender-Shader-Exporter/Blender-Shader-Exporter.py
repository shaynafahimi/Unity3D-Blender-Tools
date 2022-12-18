import bpy
import json

from bpy.types import GizmoGroupProperties, IntProperty, Operator

class Ops():
    """A class to host Static Methods"""
    @staticmethod
    def json2File(filename: str, jsonString: str):

        f = open(f"{filename}.json", "w")
        f.write(jsonString)
        pass

    @staticmethod
    def serialize2Json(serializableField):
        return json.dumps(serializableField)

    @staticmethod
    def print_IgonredMaterial(materialName: str):
        print(f"[x] Ignored  material: {materialName}")

class object3D():
    name = ""

class Texture():
    texture: str
    isAlpha: bool

    def __init__(self):
        self.texture = ""
        self.isAlpha = False


class TextureSet():
    diffuse = Texture()
    alpha = Texture()
    metal = Texture()
    roughness = Texture()
    specular = Texture()
    normal = Texture()
    subsurface = Texture()

    def assignTexture(self, texturemap: str, texture: str, isAlpha: bool):
        """assigns the Textures

        Args:
        - texturemap (str) - valid options are:
            - diffuse
            - alpha
            - roughness
            - specular
            - metal
            - normal
            - subsurface

        - texture (str): 
            - the texture to be added

        - isAlpha (bool):
            - is the texture used in a alpha channel?
        """
        newTexture = Texture()

        newTexture.isAlpha = isAlpha
        newTexture.texture = texture

        if (texturemap.lower().__contains__("diffuse")):
            self.diffuse = newTexture

        elif (texturemap.lower().__contains__("alpha")):
            self.alpha = newTexture

        elif (texturemap.lower().__contains__("roughness")):
            self.roughness = newTexture

        elif (texturemap.lower().__contains__("specular")):
            self.specular = newTexture

        elif (texturemap.lower() .__contains__("metal")):
            self.metal = newTexture

        elif (texturemap.lower().__contains__("normal")):
            self.normal = newTexture

        elif (texturemap.lower() .__contains__("subsurface")):
            self.subsurface = newTexture
        pass

    def serialize(self):
        """ returns a dict of variable - names:value"""
        dict = {"map_diffuse": self.diffuse.__dict__, "map_alpha": self.alpha.__dict__, "map_roughness": self.roughness.__dict__,
                "map_specular": self.specular.__dict__, "map_metal": self.metal.__dict__, "map_normal": self.normal.__dict__, "map_subsurface": self.subsurface.__dict__}

        return dict

    pass


class Materialvalues:
    diffuse = 0
    alpha = 0
    metal = 0
    roughness = 0
    specular = 0
    normal = 0
    subsurface = 0

    def assignValues(self, valuename, value: float):
        """assigns the Values

        Args:
        - texturemap (str) - valid options are:
            - diffuse
            - alpha
            - roughness
            - specular
            - metal
            - normal
            - subsurface

        - valuename ( str):
            - the name of the value to be added
        - value (float): 
            - the texture to be added
        """

        if (valuename.lower().__contains__("diffuse")):
            self.diffuse = value

        elif (valuename.lower().__contains__("alpha")):
            self.alpha = value

        elif (valuename.lower().__contains__("roughness")):
            self.roughness = value

        elif (valuename.lower().__contains__("specular")):
            self.specular = value

        elif (valuename.lower() .__contains__("metal")):
            self.metal = value

        elif (valuename.lower().__contains__("normal")):
            self.normal = value

        elif (valuename.lower() .__contains__("subsurface")):
            self.subsurface = value
        pass

    def serialize(self):
        """ returns a dict of variable - names:value"""
        dict = {"val_diffuse": self.diffuse, "val_alpha": self.alpha, "val_roughness": self.roughness,
                "val_specular": self.specular, "val_metal": self.metal, "val_normal": self.normal, "val_subsurface": self.subsurface}
        return dict
    pass

class Material:
    """ { "name":"stringName", "maps":{TextureMaps}, "values":{MaterialValues}}"""

    name = ""
    type = ""
    texturemaps = TextureSet()
    materialvalues = Materialvalues()

    def serialize(self):
        """ returns a dict with all variables.
        Serializes texturemaps and materialvalues"""

        dict = {
            "name": self.name,
            "type": self.type,
            "maps": self.texturemaps.serialize(),
            "values": self.materialvalues.serialize()
        }
        return dict


class Link_obj_mtl:
    objectname = ""
    materialSlot = 0
    material = ""

    def serialize(self):
        """ returns a dict of strings: {object, materialSlot, materialvariable}"""

        dict = {"Object": self.objectname,
                "materialSlot": self.materialSlot, "material": self.material}
        return dict

class File():
    objects = [object3D]
    materials = [Material]
    links = [Link_obj_mtl]
    File = {"objects": [objects], "materials": [materials], "Links": [links]}

    @staticmethod
    def SaveFile(filename: str, extension: str, content: str):
        """ Write a String to a specified file"""
        f = open(f"{filename}.{extension}", "w")
        f.write(content)
        f.close()

    @staticmethod
    def saveJson(filename: str, extension: str, content: str):
        """Writes objects, materials, Links to a File"""
        f = open(f"{filename}.{extension}", "w")
        f.write(content)
        f.close()


class MaterialExporter:

    def getObjectList(self):
        """returns a list of Objects [str] in a Blend file"""
        object_list = []
        objects = bpy.data.objects

        for object in objects:
            if len(object.material_slots.items()) == 0:
                objects.remove(object)
                continue

            object_list.append(object.name)

        return object_list

    def getMaterialList(self):  # ok
        """
        ### Returns
        a list of Materials in a Blend file
        """

        material_list = []

        for material in bpy.data.materials:
            if material.users != 0:
                material_list.append(material.name)

        return material_list

    def getObjMaterials(self, object: str):
        """ 
        a List of materials for the given object. 
        ### Returns
        A List of Materials,Sorted by Slot Number"""

        materials = []
        if (bpy.data.objects[object] != None):
            return materials

        for slot in bpy.data.objects[object].material_slots:
            materials.append(slot.name)

        return materials

    def findGroupNode(self, material: str):
        """Find the Group node, attached to  MaterialOutput->Surface 
        - parameters:
            - A valid material string"""

        groupNode = ""
        groupNodeName = ""
        nodeTree = bpy.data.materials[material].node_tree

        if nodeTree == None:
            return groupNode

        for node in nodeTree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                surfaceLinks = node.inputs['Surface'].links

                if len(surfaceLinks) >= 1:
                    surfaceNode = surfaceLinks[0].from_node

                    if surfaceNode.type == 'GROUP':
                        groupNode = surfaceNode
                        break
                    else:
                        groupNode = None
                        break
        return groupNode

    def findTextures(self, material: str):
        """ Get the Textures attached to the Group Node """

        def get_other_Node(Socket):
            return Socket.links[0].from_socket.node

        def get_other_Socket(Socket):
            """
            Returns the name of the other Socket 
            """
            return Socket.links[0].from_socket.name

        def get_node_Texture(node):
            """ 
            Returns the name of a image form a texturenode, without path
            """
            texturepath = ""
            if node.type == 'TEX_IMAGE':
                texturepath = bpy.path.basename(node.image.filepath)

            return texturepath

        def get_AlphaOrNot(socket):
            """
            Returns if the Socket name Is a alpha Socket or not
            """
            isAlpha = False
            if (socket.lower() == "alpha"):
                isAlpha = True
            else:
                isAlpha = False

            return isAlpha

        textureSet = TextureSet()

        if (bpy.data.materials[material] == None):
            Ops.print_IgonredMaterial(material)
            return textureSet

        nodeTree = bpy.data.materials[material].node_tree
        if(nodeTree == None):
            Ops.print_IgonredMaterial(material)
            return textureSet

        groupNode = self.findGroupNode(material)

        if groupNode == None:
            Ops.print_IgonredMaterial(material)
            return textureSet

        validSockets = {}

        for input in bpy.data.materials[material].node_tree.nodes[groupNode.name].inputs:
            if(len(input.links) != 0):
                validSockets[input.name] = input

        for socket in validSockets:

            otherNode = get_other_Node(validSockets[socket])
            otherSocket = get_other_Socket(validSockets[socket])

            texturenode = get_node_Texture(otherNode)
            isalpha = get_AlphaOrNot(otherSocket)
            textureSet.assignTexture(socket, get_node_Texture(
                otherNode), get_AlphaOrNot(otherSocket))

        return textureSet

    def findValues(self, material: str):
        """ Get Node group values of UNconnected & Matching PBR Nodes """

        values = Materialvalues()
        if (bpy.data.materials[material] == None):
            Ops.print_IgonredMaterial(material)
            return values
        nodeTree = bpy.data.materials[material].node_tree
        if(nodeTree == None):
            Ops.print_IgonredMaterial(material)
            return values
        groupNode = self.findGroupNode(material)
        if groupNode == None:
            Ops.print_IgonredMaterial(material)
            return values
        valueSockets = {}

        for input in bpy.data.materials[material].node_tree.nodes[groupNode.name].inputs:
            if(len(input.links) == 0):
                if(input.type == 'VALUE'):
                    value = input.default_value

                    values.assignValues(input.name, value)

        return values

    def findShaderType(self, material: str):
        shaderType = "Default"

        grpNode = self.findGroupNode(material=material)
        if(grpNode == None or grpNode == ""):
            pass
        else:
            shaderType = grpNode.node_tree.name

        return shaderType

    def createMaterial(self, name: str, materialtype: str, textures: TextureSet, values: Materialvalues):
        material = Material()

        material.name = name
        material.type = materialtype
        material.texturemaps = textures
        material.materialvalues = values

        return material

    def create_ObjMtl_Link(self, objects):
        """Create the Links Between Material and Object and Material Slot"""
        Links = []

        for obj in objects:
            i = 0
            while i < len(bpy.data.objects[obj].material_slots):
                newLink = Link_obj_mtl()

                newLink.objectname = obj
                newLink.material = bpy.data.objects[obj].material_slots[i].material.name
                newLink.materialSlot = i

                Links.append(newLink.serialize())

                i += 1
            pass
        return Links

    def createMaterialMappings(self):
        """ create material mappings to be put in json File """
        mappings = []

        for material in self.getMaterialList():
            newmat = Material()
        out = {}
        out["materials"] = mappings

        return out

    def initializeMaterials(self, material_List: str):
        """ 
        Initialize Materials of type objMaterial() from a materialList (string).

        Find Textures, Values and the Type from the 1st Grp Node, attached to MaterialOutput->Surface
        Shader type -> Grp Node Name
        """
        materials = []

        for material in material_List:
            newmaterial = Material()

            newmaterial.name = material
            newmaterial.texturemaps = self.findTextures(material)

            newmaterial.materialvalues = self.findValues(material)
            newmaterial.type = self.findShaderType(material)

            materials.append(newmaterial.serialize())

        return materials

    def run(self):
        """ execute the whole operation"""

        object_list = self.getObjectList()     
        material_list = self.getMaterialList(
        materials = self.initializeMaterials(material_list)

        obj_material_links = self.create_ObjMtl_Link(object_list)

        Content = {
            "objects": object_list,
            "materials": materials,
            "links": obj_material_links
        }

        File.SaveFile("leFile", "json", json.dumps(Content))
        pass


def main():
    print("Shader exporter")
    program = MaterialExporter()
    print("exporting ...")
    program.run()
    print("SHADER EXPORTER: FINISHED")
    return


classes = []
if __name__ == "__main__":
    main()