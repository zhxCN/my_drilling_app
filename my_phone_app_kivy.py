import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from datetime import datetime, timedelta
from kivy.graphics import InstructionGroup
from kivy.core.text import Label as CoreLabel
import math

# 配置树莓派服务器地址 - 需要根据实际IP修改
SERVER_URL = "http://192.168.4.1:8080"  # 替换为树莓派实际IP


class CustomGraph(Widget):
    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    points = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.redraw)
        self.bind(pos=self.redraw)
        self.bind(min_value=self.redraw)
        self.bind(max_value=self.redraw)
        self.bind(points=self.redraw)
        self.line_color = (1, 0, 0, 1)  # 默认红色
        self.bg_color = (1, 1, 1, 1)    # 白色背景
        self.grid_color = (0.8, 0.8, 0.8, 1)  # 浅灰色网格
        self.axis_color = (0, 0, 0, 1)  # 黑色坐标轴
        self.label_color = (0, 0, 0, 1)  # 黑色标签
        self.redraw()

    def set_line_color(self, color):
        self.line_color = color
        self.redraw()
    
    def redraw(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            # 绘制背景
            Color(*self.bg_color)
            Rectangle(pos=self.pos, size=self.size)
            
            # 绘制网格和坐标轴
            self.draw_grid_and_axes()
            
            # 绘制曲线
            if self.points:
                self.draw_line()
    
    def draw_grid_and_axes(self):
        padding = 20
        width, height = self.size
        grid_width = width - 2 * padding
        grid_height = height - 2 * padding
        
        # 绘制网格
        Color(*self.grid_color)
        
        # 水平网格线 (10条)
        for i in range(11):
            y = padding + grid_height * i / 10
            Line(points=[padding, y, width - padding, y], width=0.5)
        
        # 垂直网格线 (10条)
        for i in range(11):
            x = padding + grid_width * i / 10
            Line(points=[x, padding, x, height - padding], width=0.5)
        
        # 绘制坐标轴
        Color(*self.axis_color)
        # X轴
        Line(points=[padding, padding, width - padding, padding], width=1.5)
        # Y轴
        Line(points=[padding, padding, padding, height - padding], width=1.5)
        
        # 绘制刻度标签
        Color(*self.label_color)
        # Y轴标签
        value_range = self.max_value - self.min_value
        for i in range(11):
            value = self.min_value + value_range * i / 10
            y = padding + grid_height * i / 10
            
            # 使用 CoreLabel 创建文本标签
            core_label = CoreLabel(
                text=f"{value:.1f}",
                font_size=10,
                color=self.label_color
            )
            core_label.refresh()
            
            # 获取纹理
            texture = core_label.texture
            if texture:
                # 计算位置（左下角为原点）
                pos_x = self.pos[0] + 5
                pos_y = self.pos[1] + y - texture.height / 2
                
                # 绘制纹理
                Rectangle(
                    texture=texture,
                    pos=(pos_x, pos_y),
                    size=texture.size
                )
        
        # X轴标签（时间）
        if self.points:
            # 使用 CoreLabel 创建第一个标签
            core_label_start = CoreLabel(text="0", font_size=10, color=self.label_color)
            core_label_start.refresh()
            texture_start = core_label_start.texture
            if texture_start:
                # 计算位置
                pos_x = self.pos[0] + padding
                pos_y = self.pos[1] + padding - 15
                Rectangle(
                    texture=texture_start,
                    pos=(pos_x, pos_y),
                    size=texture_start.size
                )
            
            # 使用 CoreLabel 创建最后一个标签
            core_label_end = CoreLabel(text="100%", font_size=10, color=self.label_color)
            core_label_end.refresh()
            texture_end = core_label_end.texture
            if texture_end:
                # 计算位置
                pos_x = self.pos[0] + width - padding - 30
                pos_y = self.pos[1] + padding - 15
                Rectangle(
                    texture=texture_end,
                    pos=(pos_x, pos_y),
                    size=texture_end.size
                )
    
    def draw_line(self):
        if not self.points:
            return
            
        padding = 20
        width, height = self.size
        grid_width = width - 2 * padding
        grid_height = height - 2 * padding
        value_range = self.max_value - self.min_value
        
        # 计算实际坐标点
        scaled_points = []
        for x, y in self.points:
            # 确保值在范围内
            y = max(self.min_value, min(y, self.max_value))
            
            # 计算在画布上的位置
            x_pos = self.pos[0] + padding + grid_width * x / 100
            y_pos = self.pos[1] + padding + grid_height * (y - self.min_value) / value_range
            scaled_points.extend([x_pos, y_pos])
        
        # 绘制曲线
        Color(*self.line_color)
        Line(points=scaled_points, width=1.5)
        
        # 绘制数据点（每5个点画一个）
        for i in range(0, len(scaled_points), 10):
            if i+1 < len(scaled_points):
                x = scaled_points[i]
                y = scaled_points[i+1]
                Ellipse(pos=(x-2, y-2), size=(4, 4))

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(
            text="钻井参数监测系统", 
            font_size=24, 
            size_hint_y=0.2,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        
        # 登录表单
        form = GridLayout(cols=2, spacing=10, size_hint_y=0.4)
        form.add_widget(Label(text="手机号:", bold=True))
        self.phone_input = TextInput(
            multiline=False, 
            input_filter='int',
            hint_text="请输入手机号",
            size_hint_y=None,
            height=40
        )
        form.add_widget(self.phone_input)
        
        # 按钮区域
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.2)
        login_btn = Button(
            text="登录", 
            on_press=self.login,
            background_color=(0.2, 0.6, 0.4, 1),
            size_hint_x=0.6
        )
        register_btn = Button(
            text="注册", 
            on_press=self.show_register,
            background_color=(0.6, 0.4, 0.2, 1),
            size_hint_x=0.4
        )
        btn_layout.add_widget(login_btn)
        btn_layout.add_widget(register_btn)
        
        layout.add_widget(title)
        layout.add_widget(form)
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def login(self, instance):
        phone = self.phone_input.text.strip()
        if not phone or len(phone) != 11:
            self.show_message("请输入11位手机号")
            return
            
        try:
            response = requests.post(f"{SERVER_URL}/api/login", json={'phone': phone})
            if response.status_code == 200:
                user_data = response.json()
                app = App.get_running_app()
                app.user_data = user_data
                self.manager.current = 'main'
            else:
                error_msg = response.json().get('message', '登录失败')
                self.show_message(error_msg)
        except requests.exceptions.ConnectionError:
            self.show_message("无法连接到服务器，请检查网络")
        except Exception as e:
            self.show_message(f"登录错误: {str(e)}")
    
    def show_message(self, message):
        # 在实际应用中，可以添加一个弹出框显示消息
        print(message)
    
    def show_register(self, instance):
        self.manager.current = 'register'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(
            text="新用户注册", 
            font_size=24, 
            size_hint_y=0.15,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        
        # 注册表单
        form = GridLayout(cols=2, spacing=10, size_hint_y=0.6)
        
        form.add_widget(Label(text="姓名:", bold=True))
        self.name_input = TextInput(
            multiline=False, 
            hint_text="请输入姓名",
            size_hint_y=None,
            height=40
        )
        form.add_widget(self.name_input)
        
        form.add_widget(Label(text="手机号:", bold=True))
        self.phone_input = TextInput(
            multiline=False, 
            input_filter='int',
            hint_text="请输入11位手机号",
            size_hint_y=None,
            height=40
        )
        form.add_widget(self.phone_input)
        
        form.add_widget(Label(text="公司:", bold=True))
        self.company_input = TextInput(
            multiline=False, 
            hint_text="请输入公司名称",
            size_hint_y=None,
            height=40
        )
        form.add_widget(self.company_input)
        
        # 按钮区域
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.15)
        submit_btn = Button(
            text="提交", 
            on_press=self.register,
            background_color=(0.2, 0.6, 0.4, 1)
        )
        back_btn = Button(
            text="返回", 
            on_press=self.back_to_login,
            background_color=(0.8, 0.3, 0.3, 1)
        )
        btn_layout.add_widget(back_btn)
        btn_layout.add_widget(submit_btn)
        
        layout.add_widget(title)
        layout.add_widget(form)
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def register(self, instance):
        name = self.name_input.text.strip()
        phone = self.phone_input.text.strip()
        company = self.company_input.text.strip()
        
        if not name:
            self.show_message("请输入姓名")
            return
        if not phone or len(phone) != 11:
            self.show_message("请输入11位手机号")
            return
        if not company:
            self.show_message("请输入公司名称")
            return
        
        data = {
            'name': name,
            'phone': phone,
            'company': company
        }
        
        try:
            response = requests.post(f"{SERVER_URL}/api/register", json=data)
            if response.status_code == 200:
                self.show_message("注册成功！")
                self.back_to_login(instance)
            else:
                error_msg = response.json().get('message', '注册失败')
                self.show_message(error_msg)
        except requests.exceptions.ConnectionError:
            self.show_message("无法连接到服务器，请检查网络")
        except Exception as e:
            self.show_message(f"注册错误: {str(e)}")
    
    def show_message(self, message):
        # 在实际应用中，可以添加一个弹出框显示消息
        print(message)
    
    def back_to_login(self, instance):
        self.manager.current = 'login'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部用户信息栏
        user_bar = BoxLayout(
            size_hint_y=0.1,
            padding=10,
            spacing=10
        )
        self.user_label = Label(
            text="", 
            font_size=18,
            halign='left',
            valign='middle',
            size_hint_x=0.8
        )
        logout_btn = Button(
            text="退出", 
            size_hint_x=0.2,
            background_color=(0.8, 0.3, 0.3, 1),
            on_press=self.logout
        )
        user_bar.add_widget(self.user_label)
        user_bar.add_widget(logout_btn)
        
        # 主内容区域
        content = BoxLayout(orientation='vertical')
        
        # 欢迎信息
        self.welcome_label = Label(
            text="欢迎使用钻井参数监测系统",
            font_size=22,
            bold=True,
            color=(0.2, 0.4, 0.6, 1),
            size_hint_y=0.2
        )
        content.add_widget(self.welcome_label)
        
        # 功能按钮区域
        btn_bar = BoxLayout(
            size_hint_y=0.3,
            padding=20,
            spacing=20
        )
        realtime_btn = Button(
            text="实时数据", 
            font_size=18,
            background_color=(0.2, 0.6, 0.4, 1),
            on_press=self.show_realtime
        )
        history_btn = Button(
            text="历史记录", 
            font_size=18,
            background_color=(0.4, 0.4, 0.8, 1),
            on_press=self.show_history
        )
        settings_btn = Button(
            text="系统设置", 
            font_size=18,
            background_color=(0.8, 0.5, 0.2, 1),
            on_press=self.show_settings
        )
        btn_bar.add_widget(realtime_btn)
        btn_bar.add_widget(history_btn)
        btn_bar.add_widget(settings_btn)
        
        # 状态信息区域
        status_bar = BoxLayout(
            orientation='vertical',
            size_hint_y=0.3,
            padding=10
        )
        self.status_label = Label(
            text="系统状态: 正常",
            font_size=16,
            color=(0, 0.6, 0, 1)
        )
        self.last_update_label = Label(
            text="最后更新时间: --",
            font_size=14
        )
        status_bar.add_widget(self.status_label)
        status_bar.add_widget(self.last_update_label)
        
        content.add_widget(btn_bar)
        content.add_widget(status_bar)
        
        main_layout.add_widget(user_bar)
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def on_pre_enter(self):
        app = App.get_running_app()
        if hasattr(app, 'user_data'):
            user = app.user_data
            self.user_label.text = f"{user['Name']} | {user['Company']}"
        
        # 更新最后更新时间
        self.last_update_label.text = f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    def show_realtime(self, instance):
        # 切换到实时数据界面
        self.manager.current = 'realtime'
    
    def show_history(self, instance):
        # 切换到历史数据界面
        self.manager.current = 'history'
    
    def show_settings(self, instance):
        # 切换到设置界面
        self.manager.current = 'settings'
    
    def logout(self, instance):
        # 清除用户数据
        if hasattr(App.get_running_app(), 'user_data'):
            del App.get_running_app().user_data
        self.manager.current = 'login'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航栏
        nav_bar = BoxLayout(
            size_hint_y=0.08,
            padding=5
        )
        back_btn = Button(
            text="返回", 
            size_hint_x=0.2,
            background_color=(0.8, 0.3, 0.3, 1),
            on_press=self.back_to_main
        )
        title = Label(
            text="历史数据查询", 
            font_size=20,
            bold=True
        )
        nav_bar.add_widget(back_btn)
        nav_bar.add_widget(title)
        
        # 查询条件区域
        query_panel = BoxLayout(
            orientation='vertical', 
            size_hint_y=0.25,
            padding=10,
            spacing=5
        )
        
        # 时间选择模式
        time_mode_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        time_mode_layout.add_widget(Label(text="时间范围:", size_hint_x=0.3))
        self.time_mode = Spinner(
            text='当前时间前', 
            values=('当前时间前', '时间范围'),
            size_hint_x=0.7
        )
        time_mode_layout.add_widget(self.time_mode)
        
        # 时间值选择
        self.time_value_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        self.time_value_layout.add_widget(Label(text="小时:", size_hint_x=0.3))
        self.hours_spinner = Spinner(
            text='1', 
            values=[str(i) for i in range(1, 25)],
            size_hint_x=0.3
        )
        self.time_value_layout.add_widget(self.hours_spinner)
        self.time_value_layout.add_widget(Label(text="分钟:", size_hint_x=0.3))
        self.minutes_spinner = Spinner(
            text='0', 
            values=[str(i) for i in range(0, 60, 5)],
            size_hint_x=0.3
        )
        self.time_value_layout.add_widget(self.minutes_spinner)
        
        # 井号选择
        well_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        well_layout.add_widget(Label(text="井号:", size_hint_x=0.3))
        self.well_spinner = Spinner(
            text='加载中...', 
            size_hint_x=0.7,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        well_layout.add_widget(self.well_spinner)
        
        # 查询按钮
        query_btn = Button(
            text="查询数据", 
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 0.4, 1),
            on_press=self.query_data
        )
        
        query_panel.add_widget(time_mode_layout)
        query_panel.add_widget(self.time_value_layout)
        query_panel.add_widget(well_layout)
        query_panel.add_widget(query_btn)
        
        # 数据显示区域
        display_area = BoxLayout(orientation='vertical', size_hint_y=0.67)
        
        # 井号标签
        self.well_label = Label(
            text="井号: --", 
            size_hint_y=0.05,
            font_size=16,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        display_area.add_widget(self.well_label)
        
        # 参数选择按钮
        self.param_buttons = BoxLayout(size_hint_y=0.08, spacing=5)
        params = [
            ('指重', 'A01', (0, 1, 0)),        # green
            ('泵压', 'A02', (0.5, 0, 0.5)),    # purple
            ('扭矩', 'A03', (1, 0, 0)),        # red
            ('排量', 'A04', (1, 1, 0)),        # yellow
            ('转速', 'A05', (0, 0, 0))         # black
        ]
        for name, code, color in params:
            btn = ToggleButton(
                text=name, 
                group='params',
                background_color=color + (1,),
                background_normal='',
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, c=code: self.select_parameter(c))
            self.param_buttons.add_widget(btn)
        
        # 默认选择第一个参数
        self.param_buttons.children[-1].state = 'down'
        self.current_param = 'A01'
        
        display_area.add_widget(self.param_buttons)
        
        # 数据表格容器
        table_container = BoxLayout(size_hint_y=0.4)
        self.table_scroll = ScrollView()
        self.table_layout = GridLayout(cols=7, size_hint_y=None, spacing=5)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))
        self.table_scroll.add_widget(self.table_layout)
        table_container.add_widget(self.table_scroll)
        display_area.add_widget(table_container)
        
        # 曲线图容器
        graph_container = BoxLayout(size_hint_y=0.47)
        self.graph = CustomGraph()
        graph_container.add_widget(self.graph)
        display_area.add_widget(graph_container)
        
        main_layout.add_widget(nav_bar)
        main_layout.add_widget(query_panel)
        main_layout.add_widget(display_area)
        self.add_widget(main_layout)
        
        # 加载井号列表
        Clock.schedule_once(self.load_wells)
    
    def load_wells(self, dt):
        try:
            response = requests.get(f"{SERVER_URL}/api/wells", timeout=5)
            if response.status_code == 200:
                wells = response.json()
                well_options = [f"{w['ID']}-{w['WELL']}" for w in wells]
                self.well_spinner.values = well_options
                if well_options:
                    self.well_spinner.text = well_options[0]
            else:
                self.well_spinner.text = "加载失败"
        except requests.exceptions.ConnectionError:
            self.well_spinner.text = "无法连接服务器"
        except Exception as e:
            self.well_spinner.text = f"错误: {str(e)}"
    
    def query_data(self, instance):
        selected_well = self.well_spinner.text
        if not selected_well or selected_well == "加载中...":
            return
            
        try:
            well_id = selected_well.split('-')[0]
        except:
            return
            
        # 计算时间范围
        now = datetime.now()
        if self.time_mode.text == '当前时间前':
            hours = int(self.hours_spinner.text)
            minutes = int(self.minutes_spinner.text)
            start_time = now - timedelta(hours=hours, minutes=minutes)
            end_time = now
        else:
            # 简化处理 - 在实际应用中应添加日期时间选择器
            start_time = now - timedelta(hours=1)
            end_time = now
        
        data = {
            'well_id': well_id,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            response = requests.post(f"{SERVER_URL}/api/drilling_data", json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    self.data = result
                    self.display_data()
                else:
                    print(f"查询失败: {result.get('message')}")
            else:
                print(f"服务器错误: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("无法连接到服务器")
        except Exception as e:
            print(f"查询错误: {str(e)}")
    
    def display_data(self):
        # 更新井号标签
        self.well_label.text = f"井号: {self.data['well_name']}"
        
        # 清空表格
        self.table_layout.clear_widgets()
        
        # 添加表头
        headers = ["序号", "指重", "泵压", "扭矩", "排量", "转速", "时间"]
        for header in headers:
            header_label = Label(
                text=header, 
                bold=True,
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=40
            )
            self.table_layout.add_widget(header_label)
        
        # 添加数据行
        for row in self.data['data']:
            for key in ['index', 'A01', 'A02', 'A03', 'A04', 'A05', 'DT']:
                value = row[key]
                # 时间只显示时分秒
                if key == 'DT' and len(value) > 10:
                    value = value[11:19]
                
                data_label = Label(
                    text=str(value), 
                    size_hint_y=None,
                    height=30
                )
                self.table_layout.add_widget(data_label)
        
        # 更新曲线
        self.select_parameter(self.current_param)
    
    def select_parameter(self, param_code):
        if not hasattr(self, 'data') or not self.data or not self.data.get('data'):
            return
            
        self.current_param = param_code
        
        # 设置曲线颜色
        param_colors = {
            'A01': (0, 1, 0, 1),    # green
            'A02': (0.5, 0, 0.5, 1), # purple
            'A03': (1, 0, 0, 1),     # red
            'A04': (1, 1, 0, 1),     # yellow
            'A05': (0, 0, 0, 1)      # black
        }
        self.graph.set_line_color(param_colors.get(param_code, (1, 0, 0, 1)))
        
        # 准备曲线数据
        points = []
        timestamps = [datetime.strptime(row['DT'], '%Y-%m-%d %H:%M:%S') for row in self.data['data']]
        
        if timestamps:
            min_time = min(timestamps)
            max_time = max(timestamps)
            time_range = (max_time - min_time).total_seconds()
            
            for i, row in enumerate(self.data['data']):
                time_val = datetime.strptime(row['DT'], '%Y-%m-%d %H:%M:%S')
                x = ((time_val - min_time).total_seconds() / time_range) * 100 if time_range > 0 else i
                y = row[param_code]
                points.append((x, y))
        
        # 设置Y轴范围（留10%的余量）
        min_val = min(y for x, y in points) if points else 0
        max_val = max(y for x, y in points) if points else 100
        padding = (max_val - min_val) * 0.1
        
        self.graph.min_value = max(0, min_val - padding)
        self.graph.max_value = max_val + padding
        self.graph.points = points
    
    def back_to_main(self, instance):
        self.manager.current = 'main'

class DrillingApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(HistoryScreen(name='history'))
        return self.sm

if __name__ == '__main__':
    DrillingApp().run()