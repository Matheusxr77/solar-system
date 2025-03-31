from OpenGL.GL import *
import glm

class Shader:
    def __init__(self, vertex_path, fragment_path, geometry_path=None):
        # Lê os arquivos dos shaders
        with open(vertex_path, 'r') as file:
            vertex_code = file.read()
        with open(fragment_path, 'r') as file:
            fragment_code = file.read()
        
        geometry_code = None
        if geometry_path is not None:
            with open(geometry_path, 'r') as file:
                geometry_code = file.read()
        
        # Compila o shader de vértice
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_code)
        glCompileShader(vertex_shader)
        self.check_compile_errors(vertex_shader, "VERTEX")
        
        # Compila o shader de fragmento
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_code)
        glCompileShader(fragment_shader)
        self.check_compile_errors(fragment_shader, "FRAGMENT")
        
        # Compila o shader de geometria, se fornecido
        if geometry_path is not None and geometry_code is not None:
            geometry_shader = glCreateShader(GL_GEOMETRY_SHADER)
            glShaderSource(geometry_shader, geometry_code)
            glCompileShader(geometry_shader)
            self.check_compile_errors(geometry_shader, "GEOMETRY")
        
        # Cria o programa de shader e anexa os shaders compilados
        self.ID = glCreateProgram()
        glAttachShader(self.ID, vertex_shader)
        glAttachShader(self.ID, fragment_shader)
        if geometry_path is not None and geometry_code is not None:
            glAttachShader(self.ID, geometry_shader)
        glLinkProgram(self.ID)
        self.check_compile_errors(self.ID, "PROGRAM")
        
        # Deleta os shaders, pois já estão linkados no programa
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        if geometry_path is not None and geometry_code is not None:
            glDeleteShader(geometry_shader)
    
    def use(self):
        """Ativa o programa de shader."""
        glUseProgram(self.ID)
    
    def set_bool(self, name, value):
        glUniform1i(glGetUniformLocation(self.ID, name.encode()), int(value))
    
    def set_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.ID, name.encode()), value)
    
    def set_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.ID, name.encode()), value)
    
    def set_vec2(self, name, x, y):
        glUniform2f(glGetUniformLocation(self.ID, name.encode()), x, y)
    
    def set_vec2v(self, name, vec):
        glUniform2fv(glGetUniformLocation(self.ID, name.encode()), 1, glm.value_ptr(vec))
    
    def set_vec3(self, name, x, y, z):
        glUniform3f(glGetUniformLocation(self.ID, name.encode()), x, y, z)
    
    def set_vec3v(self, name, vec):
        glUniform3fv(glGetUniformLocation(self.ID, name.encode()), 1, glm.value_ptr(vec))
    
    def set_vec4(self, name, x, y, z, w):
        glUniform4f(glGetUniformLocation(self.ID, name.encode()), x, y, z, w)
    
    def set_vec4v(self, name, vec):
        glUniform4fv(glGetUniformLocation(self.ID, name.encode()), 1, glm.value_ptr(vec))
    
    def set_mat2(self, name, mat):
        glUniformMatrix2fv(glGetUniformLocation(self.ID, name.encode()), 1, GL_FALSE, glm.value_ptr(mat))
    
    def set_mat3(self, name, mat):
        glUniformMatrix3fv(glGetUniformLocation(self.ID, name.encode()), 1, GL_FALSE, glm.value_ptr(mat))
    
    def set_mat4(self, name, mat):
        glUniformMatrix4fv(glGetUniformLocation(self.ID, name.encode()), 1, GL_FALSE, glm.value_ptr(mat))
    
    def check_compile_errors(self, shader, type):
        """
        Verifica e exibe mensagens de erro durante a compilação e o link dos shaders/programas.
        
        :param shader: ID do shader ou programa.
        :param type: Tipo, por exemplo "VERTEX", "FRAGMENT", "GEOMETRY" ou "PROGRAM".
        """
        if type != "PROGRAM":
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if not success:
                info_log = glGetShaderInfoLog(shader)
                print(f"ERROR::SHADER_COMPILATION_ERROR of type: {type}\n{info_log.decode()}\n -- --------------------------------------------------- -- ")
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if not success:
                info_log = glGetProgramInfoLog(shader)
                print(f"ERROR::PROGRAM_LINKING_ERROR of type: {type}\n{info_log.decode()}\n -- --------------------------------------------------- -- ")
