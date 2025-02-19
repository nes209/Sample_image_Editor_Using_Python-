import tkinter as tk
from tkinter import filedialog, simpledialog
import cv2
import numpy as np
from PIL import Image, ImageTk

class VisualDesignSuite:
    def __init__(self, master):
        self.window = master
        self.window.title("استديو التصميم البصري")
        self.window.configure(bg='#1A2A3A')  # تغيير اللون الأساسي
        
        # إعدادات الصورة
        self.active_image = None
        self.zoom_level = 1.0
        self.canvas_pos_x = 0
        self.canvas_pos_y = 0
        self.display_width = 0
        self.display_height = 0
        self.selected_tool = None
        self.drawing_start = (0, 0)
        
        # إنشاء واجهة المستخدم
        self.initialize_interface()
        
    def initialize_interface(self):
        # لوحة الأدوات الجانبية
        side_panel = tk.Frame(self.window, bg='#2A3A4A', padx=15, pady=15)
        side_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # قسم التحكم الأساسي
        control_section = tk.Frame(side_panel, bg='#2A3A4A')
        control_section.pack(pady=15)
        
        new_button_style = {
            'bg': '#4B5A6A',
            'fg': '#E0E0E0',
            'activebackground': '#5B6A7A',
            'activeforeground': '#FFFFFF',
            'relief': 'groove',
            'padx': 12,
            'pady': 8
        }
        
        tk.Button(control_section, text="استيراد ملف", command=self.load_image, **new_button_style).grid(row=0, column=0, pady=6, sticky='ew')
        tk.Button(control_section, text="التقاط من كاميرا", command=self.take_photo, **new_button_style).grid(row=1, column=0, pady=6, sticky='ew')
        tk.Button(control_section, text="حفظ المشروع", command=self.save_project, **new_button_style).grid(row=2, column=0, pady=6, sticky='ew')
        
        # أدوات التعديل
        modification_tools = tk.LabelFrame(side_panel, text="أدوات التعديل", bg='#2A3A4A', fg='#C0C0C0')
        modification_tools.pack(pady=15, fill='x')
        
        tool_set = [
            ('رسم خط', 'line', '#8A2BE2'),
            ('إطار مربع', 'rectangle', '#2E8B57'),
            ('شكل دائري', 'circle', '#20B2AA'),
            ('إضافة نص', 'text', '#DA70D6')
        ]
        
        for label, tool_id, color in tool_set:
            tk.Button(modification_tools, text=label, 
                    command=lambda t=tool_id: self.choose_tool(t),
                    bg=color, fg='white',
                    activebackground=color,
                    relief='ridge').pack(fill='x', pady=3)
        
        # تأثيرات الصورة
        effects_frame = tk.LabelFrame(side_panel, text="التأثيرات", bg='#2A3A4A', fg='#C0C0C0')
        effects_frame.pack(pady=15, fill='x')
        
        effect_options = [
            ('أبيض وأسود', self.convert_monochrome, '#808080'),
            ('انعكاس أفقي', self.flip_horizontal, '#A0A0A0')
        ]
        
        for label, action, color in effect_options:
            tk.Button(effects_frame, text=label, 
                    command=action,
                    bg=color, fg='black',
                    activebackground=color,
                    relief='ridge').pack(fill='x', pady=3)
        
        # إعدادات الحجم
        size_frame = tk.LabelFrame(side_panel, text="ضبط الأبعاد", bg='#2A3A4A', fg='#C0C0C0')
        size_frame.pack(pady=15, fill='x')
        
        self.size_input = tk.Entry(size_frame, bg='#3A4A5A', fg='white', insertbackground='white')
        self.size_input.pack(fill='x', pady=7)
        
        tk.Button(size_frame, text="تحديث الأبعاد", 
                command=self.adjust_dimensions,
                bg='#5A6A7A', fg='white',
                activebackground='#6A7A8A',
                relief='ridge').pack(fill='x')
        
        # معلومات المشروع
        self.details_label = tk.Label(side_panel, 
                                    text="مواصفات الصورة: ",
                                    bg='#2A3A4A', fg='#C0C0C0')
        self.details_label.pack(pady=15)
        
        # منطقة العمل الرئيسية
        self.work_area = tk.Canvas(self.window, width=850, height=650, bg='#0A1A2A',highlightthickness=0)
        self.work_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.work_area.bind("<ButtonPress-1>", self.on_canvas_click)
        self.work_area.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def choose_tool(self, tool):
        self.selected_tool = tool
        
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.active_image = cv2.imread(file_path)
            self.refresh_canvas()
            
    def take_photo(self):
        camera = cv2.VideoCapture(0)
        success, frame = camera.read()
        if success:
            self.active_image = frame
            self.refresh_canvas()
        camera.release()
        
    def save_project(self):
        if self.active_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if save_path:
                cv2.imwrite(save_path, self.active_image)
                
    def convert_monochrome(self):
        if self.active_image is not None:
            mono = cv2.cvtColor(self.active_image, cv2.COLOR_BGR2GRAY)
            self.active_image = cv2.cvtColor(mono, cv2.COLOR_GRAY2BGR)
            self.refresh_canvas()
            
    def flip_horizontal(self):
        if self.active_image is not None:
            self.active_image = cv2.flip(self.active_image, cv2.FLIP_HORIZONTAL)
            self.refresh_canvas()
            
    def adjust_dimensions(self):
        if self.active_image is not None:
            try:
                percentage = float(self.size_input.get())
                scale = percentage / 100.0
                original_h, original_w = self.active_image.shape[:2]
                new_width = int(original_w * scale)
                new_height = int(original_h * scale)
                self.active_image = cv2.resize(self.active_image, (new_width, new_height))
                self.refresh_canvas()
            except ValueError:
                pass
            
    def refresh_canvas(self):
        if self.active_image is not None:
            canvas_width = self.work_area.winfo_width()
            canvas_height = self.work_area.winfo_height()
            
            img_height, img_width = self.active_image.shape[:2]
            
            width_ratio = canvas_width / img_width if img_width > 0 else 1
            height_ratio = canvas_height / img_height if img_height > 0 else 1
            self.zoom_level = min(width_ratio, height_ratio)
            
            self.display_width = int(img_width * self.zoom_level)
            self.display_height = int(img_height * self.zoom_level)
            
            resized_img = cv2.resize(self.active_image, (self.display_width, self.display_height))
            rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
            self.tk_image = ImageTk.PhotoImage(image=Image.fromarray(rgb_img))
            
            self.work_area.delete("all")
            self.canvas_pos_x = (canvas_width - self.display_width) // 2
            self.canvas_pos_y = (canvas_height - self.display_height) // 2
            self.work_area.create_image(self.canvas_pos_x, self.canvas_pos_y, anchor=tk.NW, image=self.tk_image)
            
            channels = self.active_image.shape[2] if len(self.active_image.shape) == 3 else 1
            self.details_label.config(text=f"الحجم: {img_height}x{img_width} | القنوات اللونية: {channels}")
            
    def on_canvas_click(self, event):
        if self.active_image is None or self.selected_tool is None:
            return
        
        x = event.x
        y = event.y
        
        if not (self.canvas_pos_x <= x < self.canvas_pos_x + self.display_width and
                self.canvas_pos_y <= y < self.canvas_pos_y + self.display_height):
            return
        
        self.drawing_start = (
            int((x - self.canvas_pos_x) / self.zoom_level),
            int((y - self.canvas_pos_y) / self.zoom_level))
        
    def on_canvas_release(self, event):
        if self.active_image is None or self.selected_tool is None:
            return
        
        x = event.x
        y = event.y
        
        if not (self.canvas_pos_x <= x < self.canvas_pos_x + self.display_width and
                self.canvas_pos_y <= y < self.canvas_pos_y + self.display_height):
            return
        
        end_point = (
            int((x - self.canvas_pos_x) / self.zoom_level),
            int((y - self.canvas_pos_y) / self.zoom_level))
        
        draw_color = (255, 0, 0)  # لون أزرق
        line_width = 3
        
        if self.selected_tool == 'line':
            cv2.line(self.active_image, self.drawing_start, end_point, draw_color, line_width)
        elif self.selected_tool == 'rectangle':
            cv2.rectangle(self.active_image, self.drawing_start, end_point, draw_color, line_width)
        elif self.selected_tool == 'circle':
            radius = int(np.hypot(end_point[0]-self.drawing_start[0], end_point[1]-self.drawing_start[1]))
            cv2.circle(self.active_image, self.drawing_start, radius, draw_color, line_width)
        elif self.selected_tool == 'text':
            user_text = simpledialog.askstring("إدخال نص", "اكتب النص المراد إضافته:")
            if user_text:
                cv2.putText(self.active_image, user_text, self.drawing_start, cv2.FONT_HERSHEY_COMPLEX, 1.2, draw_color, line_width)
        
        self.refresh_canvas()

if __name__ == "__main__":
    main_window = tk.Tk()
    app_instance = VisualDesignSuite(main_window)
    main_window.mainloop()