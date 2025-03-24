from OpenGL.GL import *
import ctypes

class Mesh:
    def __init__(self, vertices, indices, textures):
        # vertices: lista de Vertex (pode ser um array numpy estruturado)
        # indices: lista de inteiros
        # textures: lista de dicionários com campos: id, type, path
        self.vertices = vertices
        self.indices = indices
        self.textures = textures
        self.setup_mesh()
    
    def setup_mesh(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        stride = self.vertices.strides[0]
        # Posição: 3 floats, offset 0
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        # Normais: 3 floats, offset 12 bytes
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        # TexCoords: 2 floats, offset 24 bytes
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        # Tangentes: 3 floats, offset 32 bytes (24+8? Precisamos calcular)
        # Como cada float tem 4 bytes, o offset para Tangent será: 3*4 + 3*4 + 2*4 = 32 bytes
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(32))
        # Bitangentes: 3 floats, offset = 32 + 12 = 44 bytes
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(44))

        glBindVertexArray(0)

    
    def draw(self, shader):
        # Supondo que cada textura possui o campo 'type' que pode ser "texture_diffuse" ou "texture_specular", etc.
        diffuse_nr  = 1
        specular_nr = 1
        for i, tex in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + i)
            name = tex['type']
            number = ""
            if name == "texture_diffuse":
                number = str(diffuse_nr)
                diffuse_nr += 1
            elif name == "texture_specular":
                number = str(specular_nr)
                specular_nr += 1
            # Combine o nome para formar o uniform (por exemplo, "texture_diffuse1")
            uniform_name = (name + number).encode()
            glUniform1i(glGetUniformLocation(shader.ID, uniform_name), i)
            glBindTexture(GL_TEXTURE_2D, tex['id'])
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glActiveTexture(GL_TEXTURE0)
