# Importando bibliotecas
from PIL import Image
import numpy as np
import io

def stbi_load(filename, desired_channels=0):
    """
    Carrega uma imagem de um arquivo.

    Args:
        filename (str): Caminho para o arquivo de imagem.
        desired_channels (int): Se > 0, converte para esse número de canais (1,3,4).

    Retorna:
        (numpy.ndarray, width, height, channels)
    """
    with Image.open(filename) as img:
        # Converte para o número de canais desejado, se for o caso
        img = _convert_channels(img, desired_channels)
        data = np.array(img)
        h, w = data.shape[:2]
        c = data.shape[2] if data.ndim == 3 else 1
        return data, w, h, c

def stbi_load_from_memory(buffer, desired_channels=0):
    """
    Carrega uma imagem a partir de um buffer (bytes) em memória.

    Args:
        buffer (bytes): Dados da imagem em bytes.
        desired_channels (int): Se > 0, converte para esse número de canais (1,3,4).

    Retorna:
        (numpy.ndarray, width, height, channels)
    """
    with Image.open(io.BytesIO(buffer)) as img:
        img = _convert_channels(img, desired_channels)
        data = np.array(img)
        h, w = data.shape[:2]
        c = data.shape[2] if data.ndim == 3 else 1
        return data, w, h, c

def stbi_info(filename):
    """
    Retorna informações básicas (largura, altura, número de canais) de uma imagem.

    Args:
        filename (str): Caminho para o arquivo de imagem.

    Retorna:
        (width, height, channels)
    """
    with Image.open(filename) as img:
        w, h = img.size
        c = _mode_to_channels(img.mode)
        return w, h, c

def stbi_image_free(data):
    """
    Em Python, não é necessário liberar memória manualmente.
    Esta função é um placeholder para manter a interface parecida com o stb_image.
    """
    pass

# Funções auxiliares

def _convert_channels(img, desired_channels):
    """
    Converte a imagem (Pillow Image) para o número de canais desejado (1,3,4).
    """
    if desired_channels == 0:
        # 0 => mantém o modo nativo
        # Se for P, converte para RGBA
        if img.mode == 'P':
            img = img.convert('RGBA')
        elif img.mode not in ['L','RGB','RGBA']:
            # Caso precise, converte para RGB por padrão
            img = img.convert('RGB')
    else:
        if desired_channels == 1:
            img = img.convert('L')
        elif desired_channels == 3:
            img = img.convert('RGB')
        elif desired_channels == 4:
            img = img.convert('RGBA')
    return img

def _mode_to_channels(mode):
    """
    Converte o modo Pillow para número de canais.
    """
    if mode == 'L':
        return 1
    elif mode == 'RGB':
        return 3
    elif mode == 'RGBA':
        return 4
    elif mode == 'P':
        return 1  # Paleta => 1 canal (ou 4 se convertido)
    else:
        return 3  # fallback