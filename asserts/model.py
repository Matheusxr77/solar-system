import os
import logging
import numpy as np
import pyassimp
from pyassimp.postprocess import (
    aiProcess_Triangulate,
    aiProcess_GenSmoothNormals,
    aiProcess_FlipUVs,
    aiProcess_CalcTangentSpace,
)
from asserts.mesh import Mesh
from asserts.utils import load_texture

logging.basicConfig(level=logging.INFO)

class Model:
    """
    Classe que carrega e processa um modelo 3D utilizando pyassimp.
    """

    def __init__(self, path: str, gamma: bool = False):
        """
        Inicializa o modelo e carrega o arquivo especificado.

        :param path: Caminho para o arquivo do modelo.
        :param gamma: Habilita correção gama se True.
        """
        self.gammaCorrection: bool = gamma
        self.meshes: list[Mesh] = []
        self.textures_loaded: list[dict] = []  # Evita carregamento duplicado de texturas
        self.directory: str = ""
        self.load_model(path)

    def draw(self, shader):
        """
        Desenha o modelo chamando o método draw de cada mesh.
        
        :param shader: Shader utilizado para renderização.
        """
        for mesh in self.meshes:
            mesh.draw(shader)

    def load_model(self, path: str) -> None:
        """
        Carrega o modelo a partir do arquivo e processa a cena.

        :param path: Caminho para o arquivo do modelo.
        """
        with pyassimp.load(
            path,
            processing=(
                aiProcess_Triangulate
                | aiProcess_GenSmoothNormals
                | aiProcess_FlipUVs
                | aiProcess_CalcTangentSpace
            ),
        ) as scene:
            if not scene or not scene.rootnode:
                logging.error("ERROR::ASSIMP:: %s", pyassimp.get_error())
                return
            self.directory = os.path.dirname(path)
            self.process_node(scene.rootnode, scene)

    def process_node(self, node, scene, visited: set = None) -> None:
        """
        Processa recursivamente cada nó da cena.

        :param node: Nó atual da cena.
        :param scene: Cena carregada pelo pyassimp.
        :param visited: Conjunto de IDs de nós visitados (para evitar loops).
        """
        if visited is None:
            visited = set()
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)

        for mesh in node.meshes:
            processed_mesh = self.process_mesh(mesh, scene)
            self.meshes.append(processed_mesh)

        for child in node.children:
            self.process_node(child, scene, visited)

    def process_mesh(self, mesh, scene) -> Mesh:
        """
        Processa uma mesh do modelo e extrai vértices, índices e texturas.

        :param mesh: Objeto mesh do pyassimp.
        :param scene: Cena carregada.
        :return: Objeto Mesh processado.
        """
        vertices = []
        indices = []
        textures = []

        # Processa vértices
        for i in range(mesh.vertices.shape[0]):
            vertex = {}
            # Posição
            vertex["Position"] = mesh.vertices[i]
            # Normais
            if mesh.normals is not None and len(mesh.normals) > i:
                vertex["Normal"] = mesh.normals[i]
            else:
                vertex["Normal"] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            # Coordenadas de textura
            if mesh.texturecoords is not None and len(mesh.texturecoords) > 0:
                vertex["TexCoords"] = [mesh.texturecoords[0][i][0], mesh.texturecoords[0][i][1]]
            else:
                vertex["TexCoords"] = [0.0, 0.0]
            # Tangentes
            if hasattr(mesh, "tangents") and mesh.tangents is not None and len(mesh.tangents) > i:
                vertex["Tangent"] = mesh.tangents[i]
            else:
                vertex["Tangent"] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            # Bitangentes
            if hasattr(mesh, "bitangents") and mesh.bitangents is not None and len(mesh.bitangents) > i:
                vertex["Bitangent"] = mesh.bitangents[i]
            else:
                vertex["Bitangent"] = np.array([0.0, 0.0, 0.0], dtype=np.float32)

            vertices.append(vertex)

        # Converte os vértices para um array NumPy com dtype definido
        vertex_dtype = np.dtype(
            [
                ("Position", np.float32, 3),
                ("Normal", np.float32, 3),
                ("TexCoords", np.float32, 2),
                ("Tangent", np.float32, 3),
                ("Bitangent", np.float32, 3),
            ]
        )
        vertex_array = np.array(
            [
                (
                    v["Position"],
                    v["Normal"],
                    v["TexCoords"],
                    v["Tangent"],
                    v["Bitangent"],
                )
                for v in vertices
            ],
            dtype=vertex_dtype,
        )

        # Processa índices a partir de cada face
        for face in mesh.faces:
            indices.extend(face)
        indices = np.array(indices, dtype=np.uint32)

        # Processa materiais e texturas
        if mesh.materialindex < len(scene.materials):
            material = scene.materials[mesh.materialindex]
            diffuse_maps = self.load_material_textures(material, "diffuse", "texture_diffuse")
            textures.extend(diffuse_maps)
            specular_maps = self.load_material_textures(material, "specular", "texture_specular")
            textures.extend(specular_maps)
            normal_maps = self.load_material_textures(material, "normals", "texture_normal")
            textures.extend(normal_maps)
            # Adiciona o carregamento dos height maps (ou ambient maps)
            height_maps = self.load_material_textures(material, "ambient", "texture_height")
            textures.extend(height_maps)

        return Mesh(vertex_array, indices, textures)

    def load_material_textures(self, material, type_name: str, type_str: str) -> list:
        """
        Carrega as texturas de um material de acordo com o tipo especificado.

        :param material: Material do pyassimp.
        :param type_name: Nome do tipo de textura (por exemplo, 'diffuse').
        :param type_str: String que identifica o tipo na shader (por exemplo, "texture_diffuse").
        :return: Lista de texturas carregadas.
        """
        textures = []
        if hasattr(material, "properties"):
            for prop in material.properties:
                # Inicializa key e data
                key = None
                data = None

                if isinstance(prop, dict):
                    key = prop.get("key")
                    if isinstance(key, bytes):
                        key = key.decode("utf-8")
                    data = prop.get("data")
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                else:
                    try:
                        key = prop.key.decode("utf-8")
                        data = prop.data.decode("utf-8")
                    except Exception:
                        continue

                if key == f"$tex.file[{type_name}]":
                    full_path = os.path.join(self.directory, data)
                    already_loaded = next((t for t in self.textures_loaded if t["path"] == full_path), None)
                    if already_loaded:
                        textures.append(already_loaded)
                    else:
                        texture_id = load_texture(full_path)
                        logging.info("Texture carregada: %s (ID: %s)", full_path, texture_id)
                        tex = {"id": texture_id, "type": type_str, "path": full_path}
                        textures.append(tex)
                        self.textures_loaded.append(tex)

        # Fallback: se for diffuse e nenhuma textura for encontrada, tenta carregar um arquivo padrão
        if type_name == "diffuse" and len(textures) == 0:
            basename = os.path.basename(self.directory)
            fallback_path = os.path.join(self.directory, f"{basename}_texture.png")
            if os.path.isfile(fallback_path):
                texture_id = load_texture(fallback_path)
                logging.info("Fallback texture loaded: %s (ID: %s)", fallback_path, texture_id)
                tex = {"id": texture_id, "type": type_str, "path": fallback_path}
                textures.append(tex)
                self.textures_loaded.append(tex)
        return textures
