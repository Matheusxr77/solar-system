import glm

# Constantes padrão
YAW = -195.1
PITCH = -22.9
SPEED = 2.5
SENSITIVITY = 0.1
ZOOM = 45.0

class Camera:
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), up=glm.vec3(0.0, 1.0, 0.0), yaw=YAW, pitch=PITCH):
        self.Position = position
        self.WorldUp = up
        self.Yaw = yaw
        self.Pitch = pitch
        self.Front = glm.vec3(0.0, 0.0, -1.0)
        self.MovementSpeed = SPEED
        self.MouseSensitivity = SENSITIVITY
        self.Zoom = ZOOM
        # Novo atributo para controlar a sensibilidade do scroll
        self.ScrollSensitivity = 1.0
        self.update_camera_vectors()
    
    def get_view_matrix(self):
        return glm.lookAt(self.Position, self.Position + self.Front, self.Up)
    
    def process_keyboard(self, direction, deltaTime):
        velocity = self.MovementSpeed * deltaTime
        if direction == "FORWARD":
            self.Position += self.Front * velocity
        if direction == "BACKWARD":
            self.Position -= self.Front * velocity
        if direction == "LEFT":
            self.Position -= self.Right * velocity
        if direction == "RIGHT":
            self.Position += self.Right * velocity

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.MouseSensitivity
        yoffset *= self.MouseSensitivity

        self.Yaw += xoffset
        self.Pitch += yoffset

        if constrain_pitch:
            if self.Pitch > 89.0:
                self.Pitch = 89.0
            if self.Pitch < -89.0:
                self.Pitch = -89.0

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset):
        # Multiplica o yoffset pela sensibilidade definida
        self.MovementSpeed += yoffset 
        if self.MovementSpeed < 1.0:
            self.MovementSpeed = 1.0
        if self.MovementSpeed > 100.0:
            self.MovementSpeed = 100.0

    def update_camera_vectors(self):
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        front.y = glm.sin(glm.radians(self.Pitch))
        front.z = glm.sin(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        self.Front = glm.normalize(front)
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp))
        self.Up = glm.normalize(glm.cross(self.Right, self.Front))
