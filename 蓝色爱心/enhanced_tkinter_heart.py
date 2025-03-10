import tkinter as tk
import random
import math
from colorsys import hsv_to_rgb

# 窗口设置
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = "black"

# 粒子设置
MIN_PARTICLE_SIZE = 0.5
MAX_PARTICLE_SIZE = 1.8

# 重力和风力设置
GRAVITY = 0.03
WIND_STRENGTH = 0.02
WIND_CHANGE_SPEED = 0.005

# 立体效果设置
DEPTH_LAYERS = 5  # 深度层数
DEPTH_SCALE = 0.85  # 每层缩小比例
DEPTH_OPACITY_SCALE = 0.8  # 每层透明度减少比例
LIGHT_DIRECTION = [0.5, -0.5, 0.7]  # 光源方向 [x, y, z]
LIGHT_INTENSITY = 1.2  # 光照强度

class Particle:
    def __init__(self, canvas, x, y, is_heart_particle=True, depth_layer=0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.is_heart_particle = is_heart_particle
        self.depth_layer = depth_layer  # 深度层 (0是最前面)
        
        # 根据深度层调整大小
        base_size = random.uniform(MIN_PARTICLE_SIZE, MAX_PARTICLE_SIZE)
        self.size = base_size * (DEPTH_SCALE ** depth_layer)
        self.original_size = self.size
        
        # 使用HSV色彩空间创建蓝色渐变
        if is_heart_particle:
            # 根据深度层调整色相，创造深度感
            base_hue = random.uniform(0.55, 0.65)  # 基础蓝色范围
            hue_shift = 0.03 * depth_layer  # 深度层越深，色相偏移越大
            hue = max(0.5, min(0.7, base_hue - hue_shift))  # 限制在蓝色范围内
            
            # 根据深度层调整饱和度和亮度
            saturation = random.uniform(0.7, 1.0) * (0.9 ** depth_layer)
            value = random.uniform(0.7, 1.0) * (0.85 ** depth_layer)
            
            # 计算光照效果
            if depth_layer < 2:  # 只对前面的层应用高光
                # 随机生成粒子的法向量 (模拟表面朝向)
                nx = random.uniform(-1, 1)
                ny = random.uniform(-1, 1)
                nz = random.uniform(0.5, 1)  # 主要朝向观察者
                
                # 归一化法向量
                norm = math.sqrt(nx*nx + ny*ny + nz*nz)
                nx, ny, nz = nx/norm, ny/norm, nz/norm
                
                # 计算光照强度 (法向量与光源方向的点积)
                light_dot = nx*LIGHT_DIRECTION[0] + ny*LIGHT_DIRECTION[1] + nz*LIGHT_DIRECTION[2]
                light_factor = max(0.2, min(1.0, 0.5 + light_dot * LIGHT_INTENSITY))
                
                # 应用光照
                value = min(1.0, value * light_factor)
        else:
            # 背景粒子
            hue = random.uniform(0.5, 0.7)
            saturation = random.uniform(0.5, 0.9)
            value = random.uniform(0.5, 0.9)
        
        r, g, b = hsv_to_rgb(hue, saturation, value)
        
        # 根据深度层调整透明度
        alpha = int(255 * (DEPTH_OPACITY_SCALE ** depth_layer))
        
        # 转换为Tkinter颜色格式
        self.color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        self.alpha = alpha  # 存储透明度值用于发光效果
        
        # 运动参数
        self.angle = random.uniform(0, 2 * math.pi)
        self.distance = random.uniform(0.8, 3) * (0.9 ** depth_layer)  # 深层粒子移动距离更小
        self.sin_offset = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.02, 0.05) * (1.1 ** depth_layer)  # 深层粒子脉动更快
        self.time = random.uniform(0, 100)
        
        # 飘落参数
        self.fall_speed = random.uniform(0.1, 0.5) * (0.8 ** depth_layer)  # 深层粒子下落更慢
        self.horizontal_speed = 0
        self.is_falling = False
        self.fall_delay = random.randint(100, 500)
        self.fall_counter = 0
        
        # 生命周期
        self.life = random.uniform(0.7, 1.0)
        self.fade_speed = random.uniform(0.001, 0.003)
        
        # 创建粒子
        self.id = canvas.create_oval(
            x - self.size, y - self.size,
            x + self.size, y + self.size,
            fill=self.color, outline=""
        )
        
        # 创建发光效果
        glow_size = self.size * (1.3 + 0.1 * depth_layer)  # 深层粒子发光效果更大
        glow_width = max(0.2, 0.3 * (DEPTH_OPACITY_SCALE ** depth_layer))  # 深层粒子发光轮廓更细
        
        # 创建内发光
        self.glow_id = canvas.create_oval(
            x - glow_size, y - glow_size,
            x + glow_size, y + glow_size,
            fill="", outline=self.color, width=glow_width
        )
        
        # 为前两层添加额外的发光效果，增强立体感
        if is_heart_particle and depth_layer < 2:
            outer_glow_size = self.size * 2.0
            self.outer_glow_id = canvas.create_oval(
                x - outer_glow_size, y - outer_glow_size,
                x + outer_glow_size, y + outer_glow_size,
                fill="", outline=self.color, width=0.2
            )
        else:
            self.outer_glow_id = None
    
    def update(self, mouse_x=None, mouse_y=None, attract=False, wind_direction=0):
        # 更新时间
        self.time += 0.05
        
        # 检查是否开始飘落
        if self.is_heart_particle and not self.is_falling:
            self.fall_counter += 1
            if self.fall_counter > self.fall_delay and random.random() < 0.002:
                self.is_falling = True
        
        if self.is_falling:
            # 飘落效果
            self.fall_speed += GRAVITY * (0.9 ** self.depth_layer)  # 深层粒子受重力影响更小
            self.horizontal_speed += math.cos(wind_direction) * WIND_STRENGTH * (0.9 ** self.depth_layer)
            
            # 更新位置
            new_x = self.x + self.horizontal_speed
            new_y = self.y + self.fall_speed
            
            # 边界检查
            if new_y > HEIGHT + 10:
                new_y = -10
                new_x = random.randint(0, WIDTH)
                self.fall_speed = random.uniform(0.1, 0.5) * (0.8 ** self.depth_layer)
                self.horizontal_speed = 0
            
            if new_x < -10:
                new_x = -10
                self.horizontal_speed = abs(self.horizontal_speed) * 0.8
            elif new_x > WIDTH + 10:
                new_x = WIDTH + 10
                self.horizontal_speed = -abs(self.horizontal_speed) * 0.8
        else:
            # 正常的脉动效果
            pulse = math.sin(self.time * self.pulse_speed + self.sin_offset) * 5
            
            # 根据深度层调整脉动幅度
            pulse *= (0.9 ** self.depth_layer)
            
            # 计算新位置
            new_x = self.original_x + math.cos(self.angle) * self.distance * pulse
            new_y = self.original_y + math.sin(self.angle) * self.distance * pulse
        
        # 鼠标交互 - 吸引或排斥粒子
        if mouse_x is not None and mouse_y is not None and attract:
            dx = mouse_x - new_x
            dy = mouse_y - new_y
            distance = max(math.sqrt(dx*dx + dy*dy), 0.1)
            
            # 根据深度层调整吸引力
            attraction_factor = 0.5 * (0.8 ** self.depth_layer)
            
            if distance < 150:
                force = attraction_factor / distance
                new_x += dx * force
                new_y += dy * force
                
                # 增加粒子大小
                new_size = min(self.original_size * 1.5, self.original_size + 1)
                
                # 更新粒子大小
                self.canvas.coords(
                    self.id,
                    new_x - new_size, new_y - new_size,
                    new_x + new_size, new_y + new_size
                )
                
                # 更新发光效果大小
                glow_size = new_size * (1.3 + 0.1 * self.depth_layer)
                self.canvas.coords(
                    self.glow_id,
                    new_x - glow_size, new_y - glow_size,
                    new_x + glow_size, new_y + glow_size
                )
                
                # 更新外发光效果
                if self.outer_glow_id:
                    outer_glow_size = new_size * 2.0
                    self.canvas.coords(
                        self.outer_glow_id,
                        new_x - outer_glow_size, new_y - outer_glow_size,
                        new_x + outer_glow_size, new_y + outer_glow_size
                    )
                
                self.size = new_size
            else:
                # 恢复原始大小
                if self.size > self.original_size:
                    self.size = max(self.size - 0.1, self.original_size)
                    
                    # 更新粒子大小
                    self.canvas.coords(
                        self.id,
                        new_x - self.size, new_y - self.size,
                        new_x + self.size, new_y + self.size
                    )
                    
                    # 更新发光效果大小
                    glow_size = self.size * (1.3 + 0.1 * self.depth_layer)
                    self.canvas.coords(
                        self.glow_id,
                        new_x - glow_size, new_y - glow_size,
                        new_x + glow_size, new_y + glow_size
                    )
                    
                    # 更新外发光效果
                    if self.outer_glow_id:
                        outer_glow_size = self.size * 2.0
                        self.canvas.coords(
                            self.outer_glow_id,
                            new_x - outer_glow_size, new_y - outer_glow_size,
                            new_x + outer_glow_size, new_y + outer_glow_size
                        )
        
        # 计算移动距离
        dx = new_x - self.x
        dy = new_y - self.y
        
        # 更新位置
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.glow_id, dx, dy)
        if self.outer_glow_id:
            self.canvas.move(self.outer_glow_id, dx, dy)
        
        # 更新当前位置
        self.x = new_x
        self.y = new_y
        
        # 随机改变角度
        self.angle += random.uniform(-0.05, 0.05) * (1.1 ** self.depth_layer)  # 深层粒子角度变化更大
        
        # 更新生命周期
        if not self.is_heart_particle:
            self.life -= self.fade_speed
            if self.life <= 0:
                self.life = random.uniform(0.7, 1.0)
                # 重置位置
                new_x = random.randint(0, WIDTH)
                new_y = random.randint(0, HEIGHT)
                
                # 移动到新位置
                self.canvas.coords(
                    self.id,
                    new_x - self.size, new_y - self.size,
                    new_x + self.size, new_y + self.size
                )
                
                glow_size = self.size * (1.3 + 0.1 * self.depth_layer)
                self.canvas.coords(
                    self.glow_id,
                    new_x - glow_size, new_y - glow_size,
                    new_x + glow_size, new_y + glow_size
                )
                
                if self.outer_glow_id:
                    outer_glow_size = self.size * 2.0
                    self.canvas.coords(
                        self.outer_glow_id,
                        new_x - outer_glow_size, new_y - outer_glow_size,
                        new_x + outer_glow_size, new_y + outer_glow_size
                    )
                
                self.x = new_x
                self.y = new_y
                self.original_x = new_x
                self.original_y = new_y
        
        return True

def create_heart_particles(canvas, center_x, center_y, size):
    particles = []
    
    # 创建多层爱心，增加立体感
    for layer in range(DEPTH_LAYERS):
        # 每层的大小稍微缩小，创造深度感
        layer_size = size * (DEPTH_SCALE ** layer)
        
        # 每层的位置稍微偏移，创造立体感
        layer_offset_x = layer * 2
        layer_offset_y = layer * 2
        
        # 减小步长，增加粒子数量
        step = 1 if layer < 2 else 2  # 前两层使用更多粒子
        
        for t in range(0, 628, step):
            t = t / 100
            # 爱心参数方程
            x = 16 * (math.sin(t) ** 3)
            y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            
            # 缩放和定位
            x = center_x + layer_offset_x + x * layer_size
            y = center_y + layer_offset_y - y * layer_size  # 注意这里是减号
            
            # 在每个点周围添加多个粒子，使爱心更饱满
            # 前面的层使用更多粒子
            particle_count = random.randint(2, 5) if layer < 2 else random.randint(1, 3)
            
            for _ in range(particle_count):
                # 偏移量随深度减小
                offset_scale = max(0.5, 2 - layer * 0.5)
                offset_x = random.uniform(-2, 2) * offset_scale
                offset_y = random.uniform(-2, 2) * offset_scale
                
                particles.append(Particle(canvas, x + offset_x, y + offset_y, True, layer))
    
    return particles

def create_background_particles(canvas, count):
    particles = []
    for _ in range(count):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        # 随机深度层
        depth = random.randint(0, DEPTH_LAYERS - 1)
        particles.append(Particle(canvas, x, y, False, depth))
    return particles

class HeartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("立体蓝色粒子爱心")
        
        # 设置窗口大小和位置
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # 创建画布
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 创建爱心粒子和背景粒子
        self.heart_particles = create_heart_particles(self.canvas, WIDTH // 2, HEIGHT // 2, 10)
        self.background_particles = create_background_particles(self.canvas, 200)
        self.all_particles = self.heart_particles + self.background_particles
        
        # 心跳参数
        self.heart_beat = 0
        self.pulse_factor = 1
        
        # 风向参数
        self.wind_direction = 0
        
        # 鼠标交互
        self.attract_mode = False
        self.mouse_x = None
        self.mouse_y = None
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.toggle_attract_mode)
        self.canvas.bind("<Motion>", self.track_mouse)
        self.root.bind("<space>", self.regenerate_heart)
        self.root.bind("<KeyPress-f>", self.toggle_fall)
        
        # 创建信息文本
        self.info_text = self.canvas.create_text(
            10, HEIGHT - 20, 
            text="点击鼠标: 切换吸引模式 | 空格键: 重新生成爱心 | F键: 触发飘落效果", 
            fill="white", anchor="w"
        )
        
        self.mode_text = self.canvas.create_text(
            10, 20, 
            text="吸引模式: 关闭", 
            fill="white", anchor="w"
        )
        
        # 开始动画
        self.update()
    
    def track_mouse(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
    
    def toggle_attract_mode(self, event):
        self.attract_mode = not self.attract_mode
        mode_status = "开启" if self.attract_mode else "关闭"
        self.canvas.itemconfig(self.mode_text, text=f"吸引模式: {mode_status}")
    
    def toggle_fall(self, event):
        # 触发所有爱心粒子开始飘落
        for particle in self.heart_particles:
            if random.random() < 0.7:
                particle.is_falling = True
    
    def regenerate_heart(self, event):
        # 删除现有的爱心粒子
        for particle in self.heart_particles:
            self.canvas.delete(particle.id)
            self.canvas.delete(particle.glow_id)
            if particle.outer_glow_id:
                self.canvas.delete(particle.outer_glow_id)
        
        # 创建新的爱心粒子
        self.heart_particles = create_heart_particles(self.canvas, WIDTH // 2, HEIGHT // 2, 10)
        self.all_particles = self.heart_particles + self.background_particles
    
    def update(self):
        # 爱心跳动效果
        self.heart_beat += 0.03
        self.pulse_factor = 1 + 0.15 * math.sin(self.heart_beat)
        
        # 更新风向
        self.wind_direction += (random.uniform(-1, 1) * WIND_CHANGE_SPEED)
        
        # 更新所有粒子
        for particle in self.all_particles:
            particle.update(self.mouse_x, self.mouse_y, self.attract_mode, self.wind_direction)
        
        # 添加一些随机飘动的粒子
        if random.random() < 0.05 and len(self.background_particles) < 300:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            depth = random.randint(0, DEPTH_LAYERS - 1)
            new_particle = Particle(self.canvas, x, y, False, depth)
            self.background_particles.append(new_particle)
            self.all_particles.append(new_particle)
        
        # 安排下一次更新
        self.root.after(16, self.update)

def main():
    root = tk.Tk()
    app = HeartApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 