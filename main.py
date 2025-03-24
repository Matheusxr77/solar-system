import glfw
from OpenGL.GL import *
import glm
import time

from shader import Shader
from model import Model
from camera import Camera

WIDTH, HEIGHT = 1200, 800

# Configure a câmera para visualizar a cena (ajuste conforme necessário)
camera = Camera(glm.vec3(0.0, 0.0, 150.0))
ultimo_x, ultimo_y = WIDTH / 2, HEIGHT / 2
first_mouse = True

last_frame_time = 0.0
delta_time = 0.0

# Fatores de conversão:
# - Para tamanhos (escala): usamos 0.05 (como do C++ original)
# - Para distâncias (órbita): usamos 0.5 para aumentar o espaçamento
planetas = {
    'Sun': {'dist': 0, 'escala': 50 * 0.05, 'vel': 0},
    'Mercury': {'dist': 27.5 * 0.5, 'escala': 10 * 0.05, 'vel': 4},
    'Venus': {'dist': 42 * 0.5,   'escala': 15 * 0.05, 'vel': 1.5},
    'Earth': {'dist': 46 * 0.5,   'escala': 17 * 0.05, 'vel': 1},
    'Moon': {'dist': 28.5 * 0.5,   'escala': 8.5 * 0.05, 'vel': 1, 'parent': 'Earth'},
    'Mars': {'dist': 70 * 0.5,   'escala': 13 * 0.05, 'vel': 2},
    'Jupiter': {'dist': 50 * 0.5, 'escala': 45 * 0.05, 'vel': 0.25},
    'Saturn': {'dist': 80 * 0.5,  'escala': 42 * 0.05, 'vel': 0.1667},
    'Uranus': {'dist': 140 * 0.5, 'escala': 30 * 0.05, 'vel': 0.125},
    'Neptune': {'dist': 200 * 0.5, 'escala': 29 * 0.05, 'vel': 0.1},
}

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

def mouse_callback(window, xpos, ypos):
    global ultimo_x, ultimo_y, first_mouse
    if first_mouse:
        ultimo_x, ultimo_y = xpos, ypos
        first_mouse = False
    xoffset = xpos - ultimo_x
    yoffset = ultimo_y - ypos
    ultimo_x, ultimo_y = xpos, ypos
    camera.process_mouse_movement(xoffset, yoffset)

def scroll_callback(window, xoffset, yoffset):
    camera.process_mouse_scroll(yoffset)

def process_input(window):
    global delta_time
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard("FORWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard("BACKWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard("LEFT", delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard("RIGHT", delta_time)

def main():
    global last_frame_time, delta_time
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    window = glfw.create_window(WIDTH, HEIGHT, "Sistema Solar Completo", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    glEnable(GL_DEPTH_TEST)
    
    # Carrega o shader que aplica textura
    shader = Shader("shaders/model_loading.vert", "shaders/model_loading.frag")
    
    # Carrega os modelos
    modelos = {
        'Sun': Model("models/Sun/Sun.obj"),
        'Mercury': Model("models/Mercury/Mercury.obj"),
        'Venus': Model("models/Venus/Venus.obj"),
        'Earth': Model("models/Earth/Earth.obj"),
        'Moon': Model("models/Moon/Moon.obj"),
        'Mars': Model("models/Mars/Mars.obj"),
        'Jupiter': Model("models/Jupiter/Jupiter.obj"),
        'Saturn': Model("models/Saturn/Saturn.obj"),
        'Uranus': Model("models/Uranus/Uranus.obj"),
        'Neptune': Model("models/Neptune/Neptune.obj"),
        'Background': Model("models/Background/Background.obj")
    }
    
    print("Modelos carregados com sucesso.")
    
    positions = {}
    
    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame_time
        last_frame_time = current_frame
        
        process_input(window)
        
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        projection = glm.perspective(glm.radians(camera.Zoom), WIDTH/HEIGHT, 0.1, 1000.0)
        view = camera.get_view_matrix()
        
        shader.use()
        shader.set_mat4("projection", projection)
        shader.set_mat4("view", view)
        
        # Desenha o Background (estrelas)
        model_bg = glm.mat4(1.0)
        model_bg = glm.translate(model_bg, glm.vec3(0.0, 0.0, -200.0))
        model_bg = glm.scale(model_bg, glm.vec3(500.0))
        shader.set_mat4("model", model_bg)
        modelos['Background'].draw(shader)
        
        # Desenha os planetas
        # O Sol fica fixo no centro; usamos os valores do dicionário para escala
        positions['Sun'] = glm.vec3(0)
        model_sol = glm.mat4(1.0)
        model_sol = glm.scale(model_sol, glm.vec3(planetas['Sun']['escala']))
        shader.set_mat4("model", model_sol)
        modelos['Sun'].draw(shader)
        
        # Desenha os outros planetas com órbitas simples
        for planeta, dados in planetas.items():
            if planeta == 'Sun':
                continue
            angulo = current_frame * dados['vel']
            x = dados['dist'] * glm.cos(angulo)
            z = dados['dist'] * glm.sin(angulo)
            
            # Se for a Lua, orbita a Terra
            if planeta == 'Moon':
                parent_pos = positions.get(dados['parent'], glm.vec3(0))
                posicao = glm.vec3(x, 0, z) + parent_pos
            else:
                posicao = glm.vec3(x, 0, z)
            positions[planeta] = posicao

            model_planeta = glm.mat4(1.0)
            model_planeta = glm.translate(model_planeta, posicao)
            model_planeta = glm.scale(model_planeta, glm.vec3(dados['escala']))
            shader.set_mat4("model", model_planeta)
            modelos[planeta].draw(shader)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()
