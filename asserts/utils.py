# Importando bibliotecas
from OpenGL.GL import *
from PIL import Image

def load_texture(path):
    """
    Classe que carrega e processa um modelo 3D utilizando pyassimp.
    """
    image = Image.open(path)
    image = image.convert("RGBA")
    img_data = image.tobytes("raw", "RGBA", 0, -1)
    texture_id = glGenTextures(1)

    # Carrega a textura
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Configura a textura
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    # Gera o mipmap
    glGenerateMipmap(GL_TEXTURE_2D)
    
    # Configura as propriedades da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    # Desvincula a textura
    glBindTexture(GL_TEXTURE_2D, 0)
    
    # Retorna o ID da textura
    return texture_id