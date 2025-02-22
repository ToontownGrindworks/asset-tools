import os
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
from ordered_set import OrderedSet

def rename_materials_gltf(gltf_file, output_file, compress_materials=False):
    # compress_materials will trunicate materials that share identical textures
    gltf = GLTF2().load(gltf_file)
    
    material_names = OrderedSet()
    
    def get_texture_name(material):
        if material.pbrMetallicRoughness and material.pbrMetallicRoughness.baseColorTexture:
            texture_index = material.pbrMetallicRoughness.baseColorTexture.index
            if texture_index is not None and texture_index < len(gltf.textures):
                texture_name = gltf.images[gltf.textures[texture_index].source].name
                return os.path.basename(texture_name) if texture_name else False
        return False
    
    for material in gltf.materials:
        texture_name = get_texture_name(material)
        # Just keep original name for now
        if not texture_name:
            continue
        new_name = os.path.splitext(texture_name)[0]
        
        if not compress_materials:
            counter = 1
            while new_name in material_names:
                new_name = f"{texture_name}_{counter}"
                counter += 1
        
        material.name = new_name
        material_names.add(new_name)
        print(f"Renamed material to: {new_name}")

    gltf.save(output_file)
    
# Traverse directories
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".glb") or file.endswith(".gltf"):
            gltfFile = os.path.join(root, file)
            rename_materials_gltf(gltfFile, gltfFile)
