"""
Renames materials to match the name of the texture file. 
Omits materials that do not have a texture.

Requires the Autodesk FBX Python SDK package to run.

Created by: Loonatic
Date: 2/16/25
"""

import os
import fbx

def rename_materials(fbx_file, output_file):
    manager = fbx.FbxManager.Create()
    importer = fbx.FbxImporter.Create(manager, "")
    
    if not importer.Initialize(fbx_file, -1, manager.GetIOSettings()):
        print(f"Failed to load FBX file {fbx_file}")
        return
    
    scene = fbx.FbxScene.Create(manager, "scene")
    importer.Import(scene)
    importer.Destroy()
    
    material_names = set()
    
    def get_texture_name(material):
        # Grabs name of the texture on the material if it exists.
        if material:
            diffuse_property = material.FindProperty(fbx.FbxSurfaceMaterial.sDiffuse)
            if diffuse_property.IsValid():
                for i in range(diffuse_property.GetSrcObjectCount()):
                    texture = diffuse_property.GetSrcObject(i)
                    if texture and isinstance(texture, fbx.FbxFileTexture):
                        return os.path.basename(texture.GetFileName())
        return False
        # return "SurfaceMaterial"
    
    def process_node(node):
        for i in range(node.GetMaterialCount()):
            material = node.GetMaterial(i)
            print(node.GetName())
            texture_name = get_texture_name(material)
            if not texture_name:
                continue
            print(f"texture_name - {texture_name}")
            new_name = os.path.splitext(texture_name)[0]
            print(f"new_name - {new_name}")

            # XXX: INTENTIONALLY COMPRESSES MATERIALS THAT DO NOT HAVE TEXTURES
            material.SetName(new_name)
            material_names.add(new_name)
            print(f"Renamed material to: {new_name}")
        
        for i in range(node.GetChildCount()):
            process_node(node.GetChild(i))
    
    root_node = scene.GetRootNode()
    if root_node:
        process_node(root_node)
    
    ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
    manager.SetIOSettings(ios)

    # Get the IOSettings object using GetIOSettings
    io_settings = manager.GetIOSettings()

    # Export settings
    io_settings.SetBoolProp(fbx.EXP_FBX_EMBEDDED, False)
    io_settings.SetBoolProp(fbx.EXP_FBX_MATERIAL, True)
    io_settings.SetBoolProp(fbx.EXP_FBX_TEXTURE, True)
    io_settings.SetBoolProp(fbx.EXP_FBX_ANIMATION, False)
    
    exporter = fbx.FbxExporter.Create(manager, "")
    print(f"IO Settings: {manager.GetIOSettings()}")
    if not exporter.Initialize(output_file, -1, io_settings):
        print(f"Failed to save FBX file for {output_file}")
        return
    
    exporter.Export(scene)
    exporter.Destroy()
    manager.Destroy()
    print(f"Saved updated FBX file: {output_file}")


# Traverse directories

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".fbx"):
            fbxFile = os.path.join(root, file)
            rename_materials(fbxFile, fbxFile)
