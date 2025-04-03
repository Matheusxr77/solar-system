# Importando bibliotecas
import numpy as np
import ctypes
from OpenGL.GL import *

# Define a estrutura de cada vértice da malha
vertex_dtype = np.dtype([
    ('Position', np.float32, 3),
    ('Normal', np.float32, 3),
    ('TexCoords', np.float32, 2),
    ('Tangent', np.float32, 3),
    ('Bitangent', np.float32, 3),
    ('BoneIDs', np.int32, 4),
    ('Weights', np.float32, 4) 
])

class Mesh:
    def __init__(self, vertices, indices, textures):
        """
        :param vertices: Array NumPy estruturado com os campos:
                         'Position', 'Normal', 'TexCoords', 'Tangent', 'Bitangent',
                         'BoneIDs' e 'Weights' (os dois últimos são opcionais).
        :param indices: Array NumPy de índices (np.uint32).
        :param textures: Lista de dicionários com chaves 'id', 'type' e 'path'.
        """
        self.vertices = vertices
        self.indices = indices
        self.textures = textures
        self.setup_mesh()

    def setup_mesh(self):
        # Gera os buffers e o Vertex Array Object (VAO)
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        stride = self.vertices.strides[0]

        # Atributo: Posição (3 floats)
        offset = self.vertices.dtype.fields['Position'][1]
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))

        # Atributo: Normal (3 floats)
        offset = self.vertices.dtype.fields['Normal'][1]
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))

        # Atributo: Coordenadas de textura (2 floats)
        offset = self.vertices.dtype.fields['TexCoords'][1]
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))

        # Atributo: Tangente (3 floats)
        offset = self.vertices.dtype.fields['Tangent'][1]
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))

        # Atributo: Bitangente (3 floats)
        offset = self.vertices.dtype.fields['Bitangent'][1]
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))

        # Se existir, configura os atributos de IDs dos ossos (4 inteiros)
        if 'BoneIDs' in self.vertices.dtype.names:
            offset = self.vertices.dtype.fields['BoneIDs'][1]
            glEnableVertexAttribArray(5)
            glVertexAttribIPointer(5, 4, GL_INT, stride, ctypes.c_void_p(offset))

        # Se existir, configura os atributos dos pesos dos ossos (4 floats)
        if 'Weights' in self.vertices.dtype.names:
            offset = self.vertices.dtype.fields['Weights'][1]
            glEnableVertexAttribArray(6)
            glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))

        # Desvincula o VAO e os buffers
        glBindVertexArray(0)

    def draw(self, shader):
        """
        Renderiza a malha utilizando o shader fornecido.
        
        :param shader: Objeto shader com atributo 'ID' (identificador do programa OpenGL).
        """
        diffuse_nr  = 1
        specular_nr = 1
        normal_nr   = 1
        height_nr   = 1

        # Ativa e configura as texturas de acordo com seu tipo
        for i, tex in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + i)
            name = tex['type']

            # Define o número da textura baseado no tipo
            if name == "texture_diffuse":
                number = str(diffuse_nr)
                diffuse_nr += 1
            elif name == "texture_specular":
                number = str(specular_nr)
                specular_nr += 1
            elif name == "texture_normal":
                number = str(normal_nr)
                normal_nr += 1
            elif name == "texture_height":
                number = str(height_nr)
                height_nr += 1
            else:
                number = ""

            # Forma o nome do uniform, por exemplo, "texture_diffuse1"
            uniform_name = (name + number).encode('utf-8')
            glUniform1i(glGetUniformLocation(shader.ID, uniform_name), i)
            glBindTexture(GL_TEXTURE_2D, tex['id'])

        # Renderiza os triângulos
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # Reseta o slot de textura ativa
        glActiveTexture(GL_TEXTURE0)