"""
TESLA 369 BOT - APK Android
Este app baixa e executa o bot direto do GitHub
"""
import os, sys, time, threading, subprocess, json
from android.permissions import request_permissions, Permission
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
import requests as req

Window.clearcolor = (0.04, 0.04, 0.1, 1)

class Tesla369App(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Titulo
        self.layout.add_widget(Label(
            text='⚡ TESLA 369 BOT',
            font_size='24sp',
            color=(1, 0.84, 0, 1),
            size_hint=(1, 0.1)
        ))
        
        # Status
        self.status_label = Label(
            text='Iniciando...',
            font_size='14sp',
            color=(0, 1, 0.53, 1),
            size_hint=(1, 0.1)
        )
        self.layout.add_widget(self.status_label)
        
        # Progresso
        self.progress = ProgressBar(max=100, size_hint=(1, 0.05))
        self.layout.add_widget(self.progress)
        
        # Log
        self.log_scroll = ScrollView(size_hint=(1, 0.5))
        self.log_label = Label(
            text='',
            font_size='10sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_label.text_size = (Window.width - 40, None)
        self.log_scroll.add_widget(self.log_label)
        self.layout.add_widget(self.log_scroll)
        
        # Botao
        self.btn = Button(
            text='🚀 INICIAR BOT',
            font_size='16sp',
            background_color=(1, 0.84, 0, 1),
            color=(0, 0, 0, 1),
            size_hint=(1, 0.15),
            on_press=self.iniciar_bot
        )
        self.layout.add_widget(self.btn)
        
        # Solicitar permissoes
        self.solicitar_permissoes()
        
        return self.layout
    
    def solicitar_permissoes(self):
        request_permissions([
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
            Permission.ACCESS_WIFI_STATE
        ])
    
    def log(self, msg):
        current = self.log_label.text
        self.log_label.text = current + msg + '\n'
        self.log_scroll.scroll_y = 0
    
    def update_progress(self, value):
        self.progress.value = value
    
    def update_status(self, text):
        self.status_label.text = text
    
    def iniciar_bot(self, instance):
        self.btn.disabled = True
        self.btn.text = '⏳ INICIANDO...'
        threading.Thread(target=self._run_bot, daemon=True).start()
    
    def _run_bot(self):
        try:
            self.update_status('📥 Baixando codigo...')
            self.update_progress(10)
            self.log('Baixando bot do GitHub...')
            
            # Baixar o codigo do GitHub
            url = 'https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main_public.py'
            r = req.get(url, timeout=30)
            
            if r.status_code == 200:
                work_dir = '/data/data/com.tesla369.bot/files'
                os.makedirs(work_dir, exist_ok=True)
                
                with open(f'{work_dir}/bot.py', 'w') as f:
                    f.write(r.text)
                
                self.log('✅ Codigo baixado!')
                self.update_progress(30)
                
                # Instalar dependencias
                self.update_status('📦 Instalando dependencias...')
                self.log('Instalando Flask, iqoptionapi...')
                
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install',
                    '--quiet', '--target', work_dir,
                    'flask', 'iqoptionapi', 'requests'
                ])
                
                self.log('✅ Dependencias instaladas!')
                self.update_progress(60)
                
                # Iniciar bot
                self.update_status('🚀 Iniciando bot...')
                self.log('Iniciando servidor Flask...')
                
                sys.path.insert(0, work_dir)
                os.chdir(work_dir)
                
                subprocess.Popen([
                    sys.executable, f'{work_dir}/bot.py'
                ])
                
                time.sleep(3)
                
                self.update_status('✅ BOT RODANDO!')
                self.update_progress(100)
                self.log('='*40)
                self.log('🌐 Acesse no navegador:')
                self.log('   http://localhost:5000')
                self.log('📱 IP do celular sendo usado!')
                self.log('='*40)
                
                # Abrir navegador
                import webbrowser
                webbrowser.open('http://localhost:5000')
                
            else:
                self.log(f'❌ Erro ao baixar: {r.status_code}')
                self.update_status('❌ ERRO')
                
        except Exception as e:
            self.log(f'❌ Erro: {str(e)}')
            self.update_status('❌ ERRO')

if __name__ == '__main__':
    Tesla369App().run()
