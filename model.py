import pyassimp
from pyassimp.postprocess import aiProcess_Triangulate, aiProcess_GenSmoothNormals, aiProcess_FlipUVs, aiProcess_CalcTangentSpace
import numpy as np
from mesh import Mesh
from utils import load_texture

class Model:
    def __init__(self, path, gamma=False):
        self.gammaCorrection = gamma
        self.meshes = []
        self.textures_loaded = []  # para evitar carregamento duplicado
        self.directory = ""
        self.load_model(path)
    
    def draw(self, shader):
        for mesh in self.meshes:
            mesh.draw(shader)
    
    def load_model(self, path):
        with pyassimp.load(path, processing=aiProcess_Triangulate | aiProcess_GenSmoothNormals | aiProcess_FlipUVs | aiProcess_CalcTangentSpace) as scene:
            if not scene or not scene.rootnode:
                print("ERROR::ASSIMP::", pyassimp.get_error())
                return
            self.directory = path.rsplit('/', 1)[0]
            self.process_node(scene.rootnode, scene)
    
    def process_node(self, node, scene, visited=None):
        if visited is None:
            visited = set()
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)
        for mesh in node.meshes:  # 'mesh' já é o objeto, não índice
            self.meshes.append(self.process_mesh(mesh, scene))
        for child in node.children:
            self.process_node(child, scene, visited)
    
    def process_mesh(self, mesh, scene):
        vertices = []
        indices = []
        textures = []
        
        # Processa vértices (incluindo tangente e bitangente)
        for i in range(mesh.vertices.shape[0]):
            vertex = {}
            # posição
            vertex['Position'] = mesh.vertices[i]
            # normais
            vertex['Normal'] = mesh.normals[i] if mesh.normals is not None else [0.0, 0.0, 0.0]
            # coordenadas de textura
            if mesh.texturecoords is not None and len(mesh.texturecoords) > 0:
                vertex['TexCoords'] = [mesh.texturecoords[0][i][0], mesh.texturecoords[0][i][1]]
            else:
                vertex['TexCoords'] = [0.0, 0.0]
            # tangentes
            if hasattr(mesh, 'tangents') and mesh.tangents is not None:
                vertex['Tangent'] = mesh.tangents[i]
            else:
                vertex['Tangent'] = [0.0, 0.0, 0.0]
            # bitangentes
            if hasattr(mesh, 'bitangents') and mesh.bitangents is not None:
                vertex['Bitangent'] = mesh.bitangents[i]
            else:
                vertex['Bitangent'] = [0.0, 0.0, 0.0]
            vertices.append(vertex)
        
        # Converte para array NumPy com dtype definido
        vertex_dtype = np.dtype([
            ('Position', np.float32, 3),
            ('Normal', np.float32, 3),
            ('TexCoords', np.float32, 2),
            ('Tangent', np.float32, 3),
            ('Bitangent', np.float32, 3)
        ])
        vertex_array = np.array([ (v['Position'], v['Normal'], v['TexCoords'], v['Tangent'], v['Bitangent']) for v in vertices ], dtype=vertex_dtype)
        
        # Processa índices
        for face in mesh.faces:
            indices.extend(face)
        indices = np.array(indices, dtype=np.uint32)
        
        # Processa materiais e texturas (incluindo normal maps)
        if mesh.materialindex < len(scene.materials):
            material = scene.materials[mesh.materialindex]
            diffuse_maps = self.load_material_textures(material, 'diffuse', "texture_diffuse")
            textures.extend(diffuse_maps)
            specular_maps = self.load_material_textures(material, 'specular', "texture_specular")
            textures.extend(specular_maps)
            normal_maps = self.load_material_textures(material, 'normals', "texture_normal")
            textures.extend(normal_maps)
        return Mesh(vertex_array, indices, textures)

    
    def load_material_textures(self, material, type_name, type_str):
        textures = []
        if hasattr(material, 'properties'):
            for prop in material.properties:
                # Tenta tratar prop como dicionário
                if isinstance(prop, dict):
                    key = prop.get("key")
                    if isinstance(key, bytes):
                        key = key.decode('utf-8')
                    if key == f"$tex.file[{type_name}]":
                        path = prop.get("data")
                        if isinstance(path, bytes):
                            path = path.decode('utf-8')
                        full_path = self.directory + "/" + path
                        already_loaded = next((t for t in self.textures_loaded if t['path'] == full_path), None)
                        if already_loaded:
                            textures.append(already_loaded)
                        else:
                            texture_id = load_texture(full_path)
                            print("Texture carregada:", full_path, texture_id)
                            tex = {'id': texture_id, 'type': type_str, 'path': full_path}
                            textures.append(tex)
                            self.textures_loaded.append(tex)
                else:
                    try:
                        key = prop.key.decode('utf-8')
                        if key == f"$tex.file[{type_name}]":
                            path = prop.data.decode('utf-8')
                            full_path = self.directory + "/" + path
                            already_loaded = next((t for t in self.textures_loaded if t['path'] == full_path), None)
                            if already_loaded:
                                textures.append(already_loaded)
                            else:
                                texture_id = load_texture(full_path)
                                print("Texture carregada:", full_path, texture_id)
                                tex = {'id': texture_id, 'type': type_str, 'path': full_path}
                                textures.append(tex)
                                self.textures_loaded.append(tex)
                    except Exception as e:
                        pass
        # Fallback: se for diffuse e não encontrou nenhuma textura, tenta carregar um arquivo padrão
        if type_name == 'diffuse' and len(textures) == 0:
            import os
            # Supomos que o diretório do modelo seja "models/Sun" e o arquivo padrão seja "Sun_texture.png"
            basename = os.path.basename(self.directory)
            fallback_path = os.path.join(self.directory, f"{basename}_texture.png")
            if os.path.isfile(fallback_path):
                texture_id = load_texture(fallback_path)
                print("Fallback texture loaded:", fallback_path, texture_id)
                tex = {'id': texture_id, 'type': type_str, 'path': fallback_path}
                textures.append(tex)
                self.textures_loaded.append(tex)
        return textures


