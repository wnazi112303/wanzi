import pygame
import sys
import math
import random
import colorsys

# 初始化Pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("增强版蓝色粒子爱心")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 粒子类
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(1.5, 4.5)
        self.original_size = self.size
        # 使用HSV色彩空间创建更丰富的蓝色渐变
        hue = random.uniform(0.55, 0.65)  # 蓝色范围的色相
        saturation = random.uniform(0.7, 1.0)
        value = random.uniform(0.7, 1.0)
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        self.color = (int(r * 255), int(g * 255), int(b * 255))
        self.alpha = random.randint(150, 255)
        
        self.speed = random.uniform(0.2, 1.5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.distance = random.uniform(1, 4)
        self.original_x = x
        self.original_y = y
        self.sin_offset = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.01, 0.04)
        self.time = random.uniform(0, 100)  # 随机初始时间使粒子不同步
        
        # 粒子生命周期
        self.life = random.uniform(0.7, 1.0)
        self.fade_speed = random.uniform(0.001, 0.005)
        
        # 轨迹点
        self.trail = []
        self.trail_length = random.randint(3, 8)

    def update(self, mouse_pos=None, attract=False):
        # 更新时间
        self.time += 0.05
        
        # 基础脉动
        pulse = math.sin(self.time * self.pulse_speed + self.sin_offset) * 5
        
        # 计算新位置
        self.x = self.original_x + math.cos(self.angle) * self.distance * pulse
        self.y = self.original_y + math.sin(self.angle) * self.distance * pulse
        
        # 鼠标交互 - 吸引或排斥粒子
        if mouse_pos and attract:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            distance = max(math.sqrt(dx*dx + dy*dy), 0.1)
            
            if distance < 150:  # 只影响鼠标附近的粒子
                force = 0.5 / distance
                self.x += dx * force
                self.y += dy * force
                
                # 增加粒子大小
                self.size = min(self.original_size * 1.5, self.original_size + 2)
            else:
                # 恢复原始大小
                self.size = max(self.size - 0.1, self.original_size)
        
        # 随机改变角度，使运动更自然
        self.angle += random.uniform(-0.03, 0.03)
        
        # 更新粒子生命周期
        self.life -= self.fade_speed
        if self.life <= 0:
            self.life = random.uniform(0.7, 1.0)
            # 重置位置
            self.original_x += random.uniform(-1, 1)
            self.original_y += random.uniform(-1, 1)
        
        # 添加轨迹点
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

    def draw(self):
        # 绘制轨迹
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = int(i / len(self.trail) * self.alpha * 0.5)
                trail_color = (*self.color, alpha)
                trail_size = self.size * (i / len(self.trail))
                
                # 创建轨迹表面
                trail_surface = pygame.Surface((int(trail_size * 2), int(trail_size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, trail_color, 
                                  (int(trail_size), int(trail_size)), 
                                  max(1, int(trail_size)))
                
                screen.blit(trail_surface, 
                           (int(self.trail[i][0] - trail_size), 
                            int(self.trail[i][1] - trail_size)))
        
        # 绘制粒子
        particle_color = (*self.color, int(self.alpha * self.life))
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, particle_color, 
                          (int(self.size), int(self.size)), 
                          int(self.size))
        
        # 添加发光效果
        glow_size = self.size * 3
        glow_surface = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
        glow_color = (*self.color, int(30 * self.life))
        pygame.draw.circle(glow_surface, glow_color, 
                          (int(glow_size), int(glow_size)), 
                          int(glow_size))
        
        # 绘制到屏幕
        screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))
        screen.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

# 创建爱心形状的粒子
def create_heart_particles(center_x, center_y, size, density=1):
    particles = []
    step = max(1, int(3 / density))  # 根据密度调整步长
    
    for t in range(0, 628, step):  # 0 到 2π
        t = t / 100
        # 爱心参数方程
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        
        # 缩放和定位
        x = center_x + x * size
        y = center_y - y * size  # 注意这里是减号，因为屏幕坐标系y轴向下
        
        # 在每个点周围添加多个粒子，使爱心更饱满
        for _ in range(random.randint(1, int(2 * density))):
            offset_x = random.uniform(-3, 3) * density
            offset_y = random.uniform(-3, 3) * density
            particles.append(Particle(x + offset_x, y + offset_y))
    
    return particles

# 创建背景粒子
def create_background_particles(count):
    particles = []
    for _ in range(count):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        particles.append(Particle(x, y))
    return particles

# 创建爱心粒子
heart_particles = create_heart_particles(WIDTH // 2, HEIGHT // 2, 10, 1.5)
background_particles = create_background_particles(100)

# 主循环
clock = pygame.time.Clock()
heart_beat = 0
growing = True
attract_mode = False
font = pygame.font.SysFont(None, 24)

# 渐变背景
def draw_gradient_background():
    # 创建渐变背景
    for y in range(0, HEIGHT, 2):
        # 从深蓝到黑色的渐变
        color_value = y / HEIGHT
        color = (0, int(10 * (1 - color_value)), int(30 * (1 - color_value)))
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 切换吸引模式
            attract_mode = not attract_mode
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 重新生成爱心
                heart_particles = create_heart_particles(WIDTH // 2, HEIGHT // 2, 10, 1.5)
    
    # 获取鼠标位置
    mouse_pos = pygame.mouse.get_pos()
    
    # 绘制渐变背景
    draw_gradient_background()
    
    # 爱心跳动效果
    heart_beat += 0.03
    pulse_factor = 1 + 0.15 * math.sin(heart_beat)
    
    # 更新爱心大小
    if random.random() < 0.05:
        new_size = 10 * pulse_factor
        new_particles = create_heart_particles(WIDTH // 2, HEIGHT // 2, new_size, 0.5)
        heart_particles.extend(new_particles[:10])  # 每次只添加几个粒子
    
    # 更新和绘制所有粒子
    all_particles = background_particles + heart_particles
    for particle in all_particles:
        particle.update(mouse_pos, attract_mode)
        particle.draw()
    
    # 添加一些随机飘动的粒子
    if random.random() < 0.05:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        background_particles.append(Particle(x, y))
    
    # 限制粒子数量
    if len(heart_particles) > 1000:
        heart_particles = heart_particles[:1000]
    if len(background_particles) > 200:
        background_particles = background_particles[:200]
    
    # 显示提示信息
    info_text = "点击鼠标: 切换吸引模式 | 空格键: 重新生成爱心"
    info_surface = font.render(info_text, True, WHITE)
    screen.blit(info_surface, (10, HEIGHT - 30))
    
    # 显示当前模式
    mode_text = "吸引模式: " + ("开启" if attract_mode else "关闭")
    mode_surface = font.render(mode_text, True, WHITE)
    screen.blit(mode_surface, (10, 10))
    
    # 更新显示
    pygame.display.flip()
    clock.tick(60) 