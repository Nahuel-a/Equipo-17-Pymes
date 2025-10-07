#!/usr/bin/env python3
"""
Live Navigation Scraper - Scraper en tiempo real que monitorea tu navegación
y dumpea recursos automáticamente mientras navegas.
"""

import asyncio
import os
import sys
import json
import re
import subprocess
from urllib.parse import urlparse
from datetime import datetime
from playwright.async_api import async_playwright
import aiofiles
from bs4 import BeautifulSoup

class LiveNavigationScraper:
    def __init__(self, output_dir="scraper_output", browser_type="chrome"):
        self.output_dir = output_dir
        self.browser_type = browser_type
        self.captured_resources = []
        self.detected_technologies = set()
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'pages_visited': [],
            'resources_captured': 0,
            'browser_used': browser_type
        }
        self.setup_directories()
        
    def setup_directories(self):
        """Crear estructura de directorios"""
        directories = [
            'dump/html',
            'dump/css', 
            'dump/js',
            'dump/images',
            'dump/fonts',
            'dump/other',
            'dump/pages',
            'logs'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.output_dir, directory), exist_ok=True)
        print(f"📁 Directorios creados en: {self.output_dir}")

    def find_chrome_executable(self):
        """Encontrar el ejecutable de Chrome"""
        # Rutas posibles donde podría estar Chrome
        possible_paths = [
            '/usr/local/bin/chrome',  # Enlace simbólico
            '/usr/bin/google-chrome',
            '/usr/bin/chrome',
            '/opt/google/chrome/chrome',
            '/snap/bin/chromium',
            subprocess.getoutput('which chrome').strip(),
            subprocess.getoutput('which google-chrome').strip()
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path) and os.access(path, os.X_OK):
                print(f"✅ Chrome encontrado en: {path}")
                return path
        
        # Si no se encuentra, usar flatpak
        print("🔍 Chrome no encontrado en rutas estándar, usando Flatpak...")
        return "flatpak"

    async def start_monitoring(self, initial_url):
        """Iniciar monitoreo de navegación"""
        print(f"🚀 Iniciando Playwright con {self.browser_type}...")
        
        async with async_playwright() as p:
            # Seleccionar el navegador según el tipo
            browser = None
            if self.browser_type == "chrome":
                chrome_path = self.find_chrome_executable()
                
                if chrome_path == "flatpak":
                    # Usar Chromium como fallback para Flatpak
                    print("🔄 Usando Chromium (compatible con Playwright)")
                    browser = await p.chromium.launch(
                        headless=False,
                        slow_mo=100,
                        args=[
                            '--window-size=1200,800',
                            '--start-maximized',
                            '--disable-blink-features=AutomationControlled',
                            '--no-sandbox',
                            '--disable-dev-shm-usage'
                        ]
                    )
                    self.browser_type = "chromium"  # Actualizar tipo usado
                else:
                    try:
                        # Intentar usar Chrome directamente
                        browser = await p.chromium.launch(
                            headless=False,
                            slow_mo=100,
                            executable_path=chrome_path,
                            args=[
                                '--window-size=1200,800',
                                '--start-maximized',
                                '--disable-blink-features=AutomationControlled',
                                '--no-sandbox',
                                '--disable-dev-shm-usage'
                            ]
                        )
                        print(f"✅ Chrome iniciado desde: {chrome_path}")
                    except Exception as e:
                        print(f"❌ Error iniciando Chrome: {e}")
                        print("🔄 Fallback a Chromium...")
                        browser = await p.chromium.launch(
                            headless=False,
                            slow_mo=100,
                            args=['--window-size=1200,800']
                        )
                        self.browser_type = "chromium"
                        
            elif self.browser_type == "firefox":
                browser = await p.firefox.launch(
                    headless=False,
                    slow_mo=100,
                    args=['-width=1200', '-height=800']
                )
            else:
                browser = await p.chromium.launch(
                    headless=False,
                    slow_mo=100,
                    args=['--window-size=1200,800']
                )
            
            if browser is None:
                print("❌ No se pudo iniciar ningún navegador")
                return
            
            # Crear contexto con grabación HAR
            context = await browser.new_context(
                viewport={'width': 1200, 'height': 800},
                record_har_path=os.path.join(self.output_dir, 'navigation_records.har'),
                ignore_https_errors=True,
                java_script_enabled=True,
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Configurar interceptores
            await self.setup_monitoring(page)
            
            # Navegar a la URL inicial
            print(f"🌐 Navegando a: {initial_url}")
            try:
                await page.goto(initial_url, wait_until='networkidle', timeout=30000)
                print("✅ Página cargada correctamente")
            except Exception as e:
                print(f"⚠️  Error al cargar la página: {e}")
                print("🔁 Intentando continuar...")
            
            # Mostrar instrucciones
            self.show_instructions()
            
            try:
                # Mantener el script ejecutándose
                while True:
                    await asyncio.sleep(1)
                    
                    # Verificar si la página sigue activa
                    if page.is_closed():
                        print("❌ La página se cerró. Finalizando...")
                        break
                        
            except KeyboardInterrupt:
                print("\n⏹️  Deteniendo scraper...")
            finally:
                # Generar reporte final
                await self.generate_final_report()
                await browser.close()

    async def setup_monitoring(self, page):
        """Configurar todos los interceptores de monitoreo"""
        
        # Interceptar requests
        page.on("request", lambda request: asyncio.create_task(
            self.log_request(request)
        ))
        
        # Interceptar responses
        page.on("response", lambda response: asyncio.create_task(
            self.process_response(response)
        ))
        
        # Monitorear cambios de navegación
        page.on("framenavigated", lambda frame: asyncio.create_task(
            self.handle_navigation(frame)
        ))
        
        # Capturar console logs
        page.on("console", lambda msg: self.log_console(msg))
        
        # Capturar errores de página
        page.on("pageerror", lambda error: self.log_error(error))
        
        # Monitorear requests fallidos
        page.on("requestfailed", lambda request: self.log_failed_request(request))

    async def log_request(self, request):
        """Loggear todas las requests"""
        resource_type = request.resource_type
        url = request.url
        
        # Filtrar algunos recursos ruidosos
        if resource_type in ['image', 'font', 'media']:
            return
            
        print(f"📤 REQUEST [{resource_type.upper()}] → {self.shorten_url(url)}")

    async def process_response(self, response):
        """Procesar todas las responses"""
        url = response.url
        status = response.status
        resource_type = response.request.resource_type
        
        # Solo procesar responses exitosas
        if status != 200:
            if status >= 400:
                print(f"❌ RESPONSE [{resource_type.upper()}] {status} ← {self.shorten_url(url)}")
            return
            
        # Filtrar recursos no deseados
        if self.should_skip_resource(url, resource_type):
            return
            
        print(f"📥 RESPONSE [{resource_type.upper()}] {status} ← {self.shorten_url(url)}")
        
        # Procesar el recurso
        await self.dump_resource(response, resource_type)

    def should_skip_resource(self, url, resource_type):
        """Determinar si un recurso debe ser ignorado"""
        skip_patterns = [
            'google-analytics',
            'googletag',
            'doubleclick',
            'facebook.com/tr',
            'analytics',
            'tracking',
            'beacon',
            'monitoring',
            'gtm',
            'hotjar'
        ]
        
        return any(pattern in url.lower() for pattern in skip_patterns)

    async def dump_resource(self, response, resource_type):
        """Descargar y guardar el recurso"""
        try:
            url = response.url
            content = await response.body()
            
            if not content:
                return
                
            # Clasificar y guardar el recurso
            file_path = await self.classify_and_save(url, content, resource_type, response)
            
            # Analizar contenido para detectar tecnologías
            await self.analyze_content(url, content, resource_type)
            
            # Actualizar estadísticas
            self.captured_resources.append({
                'url': url,
                'type': resource_type,
                'path': file_path,
                'timestamp': datetime.now().isoformat()
            })
            self.session_data['resources_captured'] += 1
            
            print(f"💾 GUARDADO: {file_path}")
            
        except Exception as e:
            print(f"❌ Error dumping {response.url}: {str(e)}")

    async def classify_and_save(self, url, content, resource_type, response):
        """Clasificar el recurso y guardarlo en la estructura adecuada"""
        
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Generar nombre de archivo seguro
        if not original_filename or '.' not in original_filename:
            filename = self.generate_filename(url, resource_type)
        else:
            filename = original_filename
        
        # Determinar directorio y extensión basado en el tipo
        content_type = response.headers.get('content-type', '').lower()
        
        if resource_type == 'document' or 'text/html' in content_type:
            directory = 'html'
            if not filename.endswith('.html'):
                filename += '.html'
                
        elif resource_type == 'stylesheet' or 'text/css' in content_type:
            directory = 'css'
            if not filename.endswith('.css'):
                filename += '.css'
                
        elif resource_type == 'script' or 'javascript' in content_type:
            directory = 'js'
            if not filename.endswith('.js'):
                filename += '.js'
                
        elif resource_type == 'image':
            directory = 'images'
            extension = self.get_image_extension(content_type, url)
            if not filename.endswith(extension):
                filename += extension
                
        elif resource_type == 'font':
            directory = 'fonts'
            extension = self.get_font_extension(content_type, url)
            if not filename.endswith(extension):
                filename += extension
                
        else:
            directory = 'other'
        
        file_path = os.path.join(self.output_dir, 'dump', directory, filename)
        
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
            
        return file_path

    def generate_filename(self, url, resource_type):
        """Generar nombre de archivo basado en URL y tipo"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace(':', '_').replace('/', '_')
        path = parsed_url.path.replace('/', '_').strip('_')
        
        if not path:
            path = 'index'
            
        timestamp = datetime.now().strftime("%H%M%S")
        
        return f"{domain}_{path}_{timestamp}.{resource_type}"

    def get_image_extension(self, content_type, url):
        """Obtener extensión para imágenes"""
        extensions = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'
        }
        
        # Primero intentar desde content-type
        for mime, ext in extensions.items():
            if mime in content_type:
                return ext
                
        # Fallback: desde la URL
        url_lower = url.lower()
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
            if ext in url_lower:
                return ext
                
        return '.bin'

    def get_font_extension(self, content_type, url):
        """Obtener extensión para fuentes"""
        extensions = {
            'font/woff': '.woff',
            'font/woff2': '.woff2',
            'application/font-woff': '.woff',
            'application/font-woff2': '.woff2',
            'font/ttf': '.ttf',
            'application/x-font-ttf': '.ttf',
            'font/otf': '.otf'
        }
        
        for mime, ext in extensions.items():
            if mime in content_type:
                return ext
                
        return '.font'

    async def analyze_content(self, url, content, resource_type):
        """Analizar contenido para detectar tecnologías"""
        try:
            content_str = content.decode('utf-8', errors='ignore')
            
            if resource_type in ['script', 'document']:
                await self.analyze_for_frameworks(url, content_str)
                
            elif resource_type == 'stylesheet':
                await self.analyze_for_css_frameworks(url, content_str)
                
        except Exception as e:
            print(f"⚠️  Error analizando contenido: {e}")

    async def analyze_for_frameworks(self, url, content):
        """Detectar frameworks JavaScript"""
        frameworks = {
            'React': ['react', 'React', 'createElement'],
            'Angular': ['angular', 'ng-', 'Angular'],
            'Vue.js': ['vue', 'Vue', 'createApp'],
            'Next.js': ['next', 'Next', '__NEXT_DATA__'],
            'Nuxt.js': ['nuxt', 'Nuxt'],
            'jQuery': ['jQuery', '$().'],
            'Bootstrap JS': ['bootstrap', 'Bootstrap'],
            'Tailwind CSS': ['tailwind', 'tailwindcss'],
            'Webpack': ['webpack', 'Webpack'],
            'Vite': ['__vite__', 'vite/client']
        }
        
        for framework, patterns in frameworks.items():
            if any(pattern in content for pattern in patterns):
                self.report_technology(framework, url)

    async def analyze_for_css_frameworks(self, url, content):
        """Detectar frameworks CSS"""
        css_frameworks = {
            'Bootstrap': ['.container', '.row', '.col-', 'bootstrap'],
            'Tailwind CSS': ['tailwind', '@tailwind'],
            'Bulma': ['bulma', 'section', 'hero'],
            'Foundation': ['foundation', 'row', 'column'],
            'Materialize': ['materialize', 'card-panel'],
            'Font Awesome': ['fontawesome', 'fa-']
        }
        
        for framework, patterns in css_frameworks.items():
            if any(pattern in content for pattern in patterns):
                self.report_technology(framework, url)

    def report_technology(self, tech, source):
        """Reportar tecnología detectada"""
        if tech not in self.detected_technologies:
            self.detected_technologies.add(tech)
            print(f"🎯 TECNOLOGÍA DETECTADA: {tech}")
            print(f"   📍 Fuente: {self.shorten_url(source)}")

    async def handle_navigation(self, frame):
        """Manejar cambios de navegación (SPA)"""
        if frame == frame.page.main_frame:
            new_url = frame.url
            if new_url and not new_url.startswith('about:'):
                print(f"🔄 NAVEGACIÓN DETECTADA: {self.shorten_url(new_url)}")
                
                # Guardar en historial
                if new_url not in self.session_data['pages_visited']:
                    self.session_data['pages_visited'].append(new_url)
                
                # Capturar snapshot después de un delay
                await asyncio.sleep(2)
                await self.capture_page_snapshot(frame.page, new_url)

    async def capture_page_snapshot(self, page, url):
        """Capturar snapshot de la página actual"""
        try:
            # Obtener HTML actual
            html_content = await page.content()
            
            # Generar nombre de archivo seguro
            safe_filename = self.url_to_filename(url) + ".html"
            filepath = os.path.join(self.output_dir, 'dump', 'pages', safe_filename)
            
            # Guardar HTML
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(html_content)
            
            print(f"📄 SNAPSHOT: {safe_filename}")
            
            # Analizar HTML para más tecnologías
            await self.analyze_html_content(html_content, url)
            
        except Exception as e:
            print(f"❌ Error capturando snapshot: {e}")

    async def analyze_html_content(self, html_content, url):
        """Analizar HTML para detectar tecnologías"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar meta tags de tecnologías
            meta_generator = soup.find('meta', attrs={'name': 'generator'})
            if meta_generator and meta_generator.get('content'):
                tech = meta_generator['content']
                self.report_technology(f"Generador: {tech}", url)
            
            # Buscar scripts específicos
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                src = script.get('src', '')
                if 'react' in src.lower():
                    self.report_technology("React (via script)", url)
                elif 'angular' in src.lower():
                    self.report_technology("Angular (via script)", url)
                elif 'vue' in src.lower():
                    self.report_technology("Vue.js (via script)", url)
                elif 'jquery' in src.lower():
                    self.report_technology("jQuery (via script)", url)
                    
            # Buscar atributos de frameworks
            if soup.find(attrs={'data-reactroot': True}):
                self.report_technology("React (data-reactroot)", url)
            if soup.find(attrs={'ng-': True}):
                self.report_technology("Angular (ng-*)", url)
            if soup.find(attrs={'v-': True}):
                self.report_technology("Vue.js (v-*)", url)
            if soup.find(attrs={'data-vue': True}):
                self.report_technology("Vue.js (data-vue)", url)
                
        except Exception as e:
            print(f"⚠️  Error analizando HTML: {e}")

    def log_console(self, msg):
        """Loggear mensajes de consola"""
        if msg.type in ['error', 'warning']:
            print(f"🖥️  CONSOLE [{msg.type.upper()}] {msg.text}")

    def log_error(self, error):
        """Loggear errores de página"""
        print(f"🚨 ERROR: {error}")

    def log_failed_request(self, request):
        """Loggear requests fallidas"""
        if request.resource_type in ['image', 'font']:
            return
        print(f"❌ REQUEST FALLIDA: {request.resource_type} - {self.shorten_url(request.url)}")

    def shorten_url(self, url, max_length=80):
        """Acortar URL para display"""
        if len(url) <= max_length:
            return url
        return url[:max_length-3] + "..."

    def url_to_filename(self, url):
        """Convertir URL a nombre de archivo seguro"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace(':', '_')
        path = parsed.path.replace('/', '_').strip('_')
        
        if not path:
            path = 'index'
            
        # Limpiar caracteres no seguros - CORREGIDO
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{domain}_{path}")
        return safe_name[:100]  # Limitar longitud

    def show_instructions(self):
        """Mostrar instrucciones de uso"""
        print("\n" + "="*60)
        print("🎯 LIVE NAVIGATION SCRAPER - INSTRUCCIONES")
        print("="*60)
        print(f"• Navegador: {self.browser_type}")
        print("• Navega libremente en la ventana del navegador")
        print("• El scraper capturará automáticamente:")
        print("  ✅ HTML, CSS, JavaScript")
        print("  ✅ Imágenes y fuentes") 
        print("  ✅ Llamadas API y recursos dinámicos")
        print("  ✅ Tecnologías detectadas (React, Angular, etc.)")
        print("• Presiona Ctrl+C para finalizar")
        print("="*60 + "\n")

    async def generate_final_report(self):
        """Generar reporte final de la sesión"""
        report = {
            'session': self.session_data,
            'technologies_detected': list(self.detected_technologies),
            'total_resources': len(self.captured_resources),
            'end_time': datetime.now().isoformat(),
            'resources_by_type': {}
        }
        
        # Contar recursos por tipo
        for resource in self.captured_resources:
            r_type = resource['type']
            report['resources_by_type'][r_type] = report['resources_by_type'].get(r_type, 0) + 1
        
        # Guardar reporte
        report_path = os.path.join(self.output_dir, 'session_report.json')
        async with aiofiles.open(report_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(report, indent=2, ensure_ascii=False))
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL DE LA SESIÓN")
        print("="*60)
        print(f"⏱️  Duración: {self.session_data['start_time']} → {report['end_time']}")
        print(f"🌐 Páginas visitadas: {len(self.session_data['pages_visited'])}")
        print(f"💾 Recursos capturados: {report['total_resources']}")
        print(f"🚀 Tecnologías detectadas: {len(report['technologies_detected'])}")
        print(f"🌍 Navegador usado: {self.browser_type}")
        
        if report['technologies_detected']:
            print("Tecnologías:")
            for tech in report['technologies_detected']:
                print(f"  • {tech}")
                
        print(f"\n📁 Todos los recursos guardados en: {self.output_dir}/dump/")
        print(f"📄 Reporte completo: {report_path}")
        print("="*60)

async def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python scraper.py <URL> [chrome|firefox|chromium]")
        print("Ejemplo: python scraper.py https://ejemplo.com chrome")
        print("Ejemplo: python scraper.py https://ejemplo.com firefox")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Seleccionar navegador (chrome por defecto)
    browser_type = "chrome"
    if len(sys.argv) > 2:
        browser_type = sys.argv[2].lower()
        if browser_type not in ["chrome", "firefox", "chromium"]:
            print("⚠️  Navegador no válido. Usando Chrome por defecto.")
            browser_type = "chrome"
    
    # Validar URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"🎯 Iniciando scraper con {browser_type}...")
    scraper = LiveNavigationScraper(browser_type=browser_type)
    
    try:
        await scraper.start_monitoring(url)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        print("👋 Scraper finalizado")

if __name__ == "__main__":
    asyncio.run(main())