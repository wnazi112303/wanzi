import pygame
import sys
import math
import random

# 初始化Pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("蓝色粒子爱心")

# 颜色定义
BLACK = (0, 0, 0)
BLUE_LIGHT = (100, 180, 255)
BLUE_MEDIUM = (50, 120, 220)
BLUE_DARK = (20, 80, 180)

# 粒子类
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = random.choice([BLUE_LIGHT, BLUE_MEDIUM, BLUE_DARK])
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.distance = random.randint(1, 3)
        self.original_x = x
        self.original_y = y
        self.sin_offset = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.time = 0

    def update(self):
        # 粒子围绕原始位置移动
        self.time += 0.05
        pulse = math.sin(self.time * self.pulse_speed + self.sin_offset) * 5
        
        # 计算新位置
        self.x = self.original_x + math.cos(self.angle) * self.distance * pulse
        self.y = self.original_y + math.sin(self.angle) * self.distance * pulse
        
        # 随机改变角度，使运动更自然
        self.angle += random.uniform(-0.05, 0.05)

    def draw(self):
        # 绘制粒子
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
        # 添加发光效果
        glow_size = self.size * 2
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color[:3], 30), (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))

# 创建爱心形状的粒子
def create_heart_particles(center_x, center_y, size):
    particles = []
    for t in range(0, 628, 2):  # 0 到 2π，步长为0.02
        t = t / 100
        # 爱心参数方程
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        
        # 缩放和定位
        x = center_x + x * size
        y = center_y - y * size  # 注意这里是减号，因为屏幕坐标系y轴向下
        
        # 在每个点周围添加多个粒子，使爱心更饱满
        for _ in range(random.randint(1, 3)):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            particles.append(Particle(x + offset_x, y + offset_y))
    
    return particles

# 创建爱心粒子
heart_particles = create_heart_particles(WIDTH // 2, HEIGHT // 2, 10)

# 主循环
clock = pygame.time.Clock()
heart_beat = 0
growing = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # 清屏
    screen.fill(BLACK)
    
    # 爱心跳动效果
    heart_beat += 0.03
    pulse_factor = 1 + 0.1 * math.sin(heart_beat)
    
    # 更新爱心大小
    if len(heart_particles) < 500 and random.random() < 0.1:
        new_particle = create_heart_particles(WIDTH // 2, HEIGHT // 2, 10 * pulse_factor)
        heart_particles.extend(new_particle[:5])  # 每次只添加几个粒子，避免突然变化
    
    # 更新和绘制所有粒子
    for particle in heart_particles:
        particle.update()
        particle.draw()
    
    # 添加一些随机飘动的粒子
    if random.random() < 0.1:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        heart_particles.append(Particle(x, y))
    
    # 限制粒子数量
    if len(heart_particles) > 800:
        heart_particles = heart_particles[:800]
    
    # 更新显示
    pygame.display.flip()
    clock.tick(60) 