from OpenGL.GL import *
import glm

class Shader:
    def __init__(self, vertex_path, fragment_path, geometry_path=None):
        # Lê os arquivos dos shaders
        with open(vertex_path, 'r') as file:
            vertex_code = file.read()
        with open(fragment_path, 'r') as file:
            fragment_code = file.read()
        # Compila os shaders
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_code)
        glCompileShader(vertex_shader)
        self.check_compile_errors(vertex_shader, "VERTEX")
        
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_code)
        glCompileShader(fragment_shader)
        self.check_compile_errors(fragment_shader, "FRAGMENT")
        
        # Cria o programa de shader
        self.ID = glCreateProgram()
        glAttachShader(self.ID, vertex_shader)
        glAttachShader(self.ID, fragment_shader)
        glLinkProgram(self.ID)
        self.check_compile_errors(self.ID, "PROGRAM")
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
    
    def use(self):
        glUseProgram(self.ID)
    
    def set_bool(self, name, value):
        glUniform1i(glGetUniformLocation(self.ID, name.encode()), int(value))
    
    def set_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.ID, name.encode()), value)
    
    def set_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.ID, name.encode()), value)
    
    def set_mat4(self, name, mat):
        glUniformMatrix4fv(glGetUniformLocation(self.ID, name.encode()), 1, GL_FALSE, glm.value_ptr(mat))
    
    def check_compile_errors(self, shader, type):
        if type != "PROGRAM":
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if not success:
                info_log = glGetShaderInfoLog(shader)
                print(f"ERROR::SHADER_COMPILATION_ERROR of type: {type}\n{info_log.decode()}")
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if not success:
                info_log = glGetProgramInfoLog(shader)
                print(f"ERROR::PROGRAM_LINKING_ERROR of type: {type}\n{info_log.decode()}")
