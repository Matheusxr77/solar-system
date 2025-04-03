import glm
from enum import Enum

# Enum para os movimentos da câmera
class CameraMovement(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

# Constantes padrão
YAW = -195.1
PITCH = -22.9
SPEED = 300
SENSITIVITY = 0.1
ZOOM = 45.0

class Camera:
    """
    Classe que simula uma câmera para o sistema solar, processando entradas
    do teclado e do mouse e atualizando os vetores de orientação.
    """
    def __init__(self, 
                 position: glm.vec3 = glm.vec3(0.0, 0.0, 0.0), 
                 up: glm.vec3 = glm.vec3(0.0, 1.0, 0.0), 
                 yaw: float = YAW, 
                 pitch: float = PITCH):
        self.Position: glm.vec3 = position
        self.WorldUp: glm.vec3 = up
        self.Yaw: float = yaw
        self.Pitch: float = pitch
        self.Front: glm.vec3 = glm.vec3(0.0, 0.0, -1.0)
        self.MovementSpeed: float = SPEED
        self.MouseSensitivity: float = SENSITIVITY
        self.Zoom: float = ZOOM
        self.update_camera_vectors()
    
    def get_view_matrix(self) -> glm.mat4:
        """
        Retorna a matriz de visualização calculada com base na posição da câmera,
        no vetor frontal e no vetor up.
        """
        return glm.lookAt(self.Position, self.Position + self.Front, self.Up)
    
    def process_keyboard(self, direction: CameraMovement, deltaTime: float):
        """
        Processa a entrada do teclado para mover a câmera.
        
        :param direction: Movimento (FORWARD, BACKWARD, LEFT, RIGHT)
        :param deltaTime: Tempo decorrido (para manter a consistência do movimento)
        """
        velocity = self.MovementSpeed * deltaTime
        if direction == CameraMovement.FORWARD:
            self.Position += self.Front * velocity
        elif direction == CameraMovement.BACKWARD:
            self.Position -= self.Front * velocity
        elif direction == CameraMovement.LEFT:
            self.Position -= self.Right * velocity
        elif direction == CameraMovement.RIGHT:
            self.Position += self.Right * velocity

    def process_mouse_movement(self, xoffset: float, yoffset: float, constrain_pitch: bool = True):
        """
        Processa o movimento do mouse para atualizar os ângulos Yaw e Pitch.
        
        :param xoffset: Deslocamento horizontal do mouse.
        :param yoffset: Deslocamento vertical do mouse.
        :param constrain_pitch: Se verdadeiro, limita o Pitch para evitar flips.
        """
        xoffset *= self.MouseSensitivity
        yoffset *= self.MouseSensitivity

        self.Yaw += xoffset
        self.Pitch += yoffset

        # Limita o ângulo do pitch para evitar a inversão da câmera
        if constrain_pitch:
            self.Pitch = max(min(self.Pitch, 89.0), -89.0)

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset: float):
        """
        Processa o scroll do mouse para ajustar o zoom (FOV).
        
        :param yoffset: Deslocamento do scroll (positivo ou negativo)
        """
        self.Zoom -= yoffset
        self.Zoom = max(min(self.Zoom, 45.0), 1.0)

    def update_camera_vectors(self):
        """
        Atualiza os vetores da câmera com base nos ângulos de Euler (Yaw e Pitch).
        """
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        front.y = glm.sin(glm.radians(self.Pitch))
        front.z = glm.sin(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        self.Front = glm.normalize(front)
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp))
        self.Up = glm.normalize(glm.cross(self.Right, self.Front))
    
    def __repr__(self):
        return (f"Camera(Position={self.Position}, Front={self.Front}, Up={self.Up}, "
                f"Yaw={self.Yaw}, Pitch={self.Pitch}, Zoom={self.Zoom})")
