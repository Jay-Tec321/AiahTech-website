from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Computer, ComputerInquiry, App, Graphics
import os

def home(request):
    total_repairs = 500
    satisfaction_rate = "98%"
    turnaround_time = "24-48 hours"
    
    # Get available computers
    computers_list = Computer.objects.filter(status='available')
    
    # Get graphics from database
    graphics_list = Graphics.objects.all().order_by('-is_featured', 'order', '-created_at')
    
    # Build computers slideshow HTML
    computers_slides_html = ""
    computers_dots_html = ""
    if computers_list:
        for i, computer in enumerate(computers_list):
            active_class = "active" if i == 0 else ""
            brand_display = computer.get_brand_display()
            computers_slides_html += f'''
                    <div class="computer-slide {active_class}">
                        <div class="computer-slide-content">
                            <div class="computer-slide-image">
                                <img src="{computer.main_image.url}" alt="{computer.title}">
                            </div>
                            <div class="computer-slide-info">
                                <h3>{computer.title}</h3>
                                <p class="brand">{brand_display} • {computer.year}</p>
                                <p class="specs">💻 {computer.processor} • {computer.ram} • {computer.storage}</p>
                                <p class="price">Le {computer.price}</p>
                                <a href="/computers/{computer.id}/" class="btn-view">View Details →</a>
                            </div>
                        </div>
                    </div>
                    '''
            computers_dots_html += f'<span class="computer-dot {active_class}" onclick="goToComputerSlide({i})"></span>'
    else:
        computers_slides_html = '<p style="padding: 40px; opacity: 0.7;">No computers available right now. Check back soon!</p>'
    
    # Build slides HTML for graphics
    graphics_slides_html = ""
    graphics_dots_html = ""
    if graphics_list:
        for i, g in enumerate(graphics_list):
            active_class = "active" if i == 0 else ""
            graphics_slides_html += f'''
                    <div class="gallery-slide {active_class}">
                        <img src="{g.image.url}" alt="{g.title}">
                        <div class="slide-info">
                            <h4>{g.title}</h4>
                            <p>{g.description}</p>
                            <span class="category">{g.get_category_display()}</span>
                        </div>
                    </div>
                    '''
            graphics_dots_html += f'<span class="gallery-dot {active_class}" onclick="goToGraphicsSlide({i})"></span>'
    else:
        graphics_slides_html = '<p style="padding: 40px; opacity: 0.7;">No graphics uploaded yet. Add some from the admin panel!</p>'
    
    # JavaScript for slideshows and menu
    js_script = '''
        <script>
            // ===== SLIDE-OUT MENU =====
            function openMenu() {
                document.getElementById('sideMenu').style.width = '280px';
                document.getElementById('overlay').style.display = 'block';
                document.body.style.overflow = 'hidden';
            }

            function closeMenu() {
                document.getElementById('sideMenu').style.width = '0';
                document.getElementById('overlay').style.display = 'none';
                document.body.style.overflow = 'auto';
            }

            // ===== COMPUTER SLIDESHOW =====
            var currentComputerSlide = 0;
            var computerSlides = document.querySelectorAll('.computer-slide');
            var computerDots = document.querySelectorAll('.computer-dot');
            var computerAutoSlideInterval;

            function showComputerSlide(index) {
                if (index >= computerSlides.length) { currentComputerSlide = 0; }
                if (index < 0) { currentComputerSlide = computerSlides.length - 1; }
                
                for (var i = 0; i < computerSlides.length; i++) {
                    computerSlides[i].classList.remove('active');
                }
                for (var i = 0; i < computerDots.length; i++) {
                    computerDots[i].classList.remove('active');
                }
                
                computerSlides[currentComputerSlide].classList.add('active');
                computerDots[currentComputerSlide].classList.add('active');
            }

            function changeComputerSlide(direction) {
                currentComputerSlide += direction;
                showComputerSlide(currentComputerSlide);
                resetComputerAutoSlide();
            }

            function goToComputerSlide(index) {
                currentComputerSlide = index;
                showComputerSlide(currentComputerSlide);
                resetComputerAutoSlide();
            }

            function resetComputerAutoSlide() {
                clearInterval(computerAutoSlideInterval);
                if (computerSlides.length > 0) {
                    computerAutoSlideInterval = setInterval(function() {
                        currentComputerSlide++;
                        if (currentComputerSlide >= computerSlides.length) {
                            currentComputerSlide = 0;
                        }
                        showComputerSlide(currentComputerSlide);
                    }, 5000);
                }
            }

            if (computerSlides.length > 0) {
                showComputerSlide(0);
                computerAutoSlideInterval = setInterval(function() {
                    currentComputerSlide++;
                    if (currentComputerSlide >= computerSlides.length) {
                        currentComputerSlide = 0;
                    }
                    showComputerSlide(currentComputerSlide);
                }, 5000);
            }

            var computerContainer = document.getElementById('computerSlideshow');
            if (computerContainer) {
                computerContainer.addEventListener('mouseenter', function() {
                    clearInterval(computerAutoSlideInterval);
                });
                
                computerContainer.addEventListener('mouseleave', function() {
                    if (computerSlides.length > 0) {
                        resetComputerAutoSlide();
                    }
                });
            }

            // ===== GRAPHICS SLIDESHOW =====
            var currentGraphicsSlide = 0;
            var graphicsSlides = document.querySelectorAll('.gallery-slide');
            var graphicsDots = document.querySelectorAll('.gallery-dot');
            var animations = [
                'anim-fade', 'anim-zoom', 'anim-slide-left', 'anim-slide-right',
                'anim-slide-up', 'anim-slide-down', 'anim-rotate', 'anim-blur',
                'anim-flip', 'anim-bounce', 'anim-shake'
            ];
            var graphicsAutoSlideInterval;

            function showGraphicsSlide(index) {
                if (index >= graphicsSlides.length) { currentGraphicsSlide = 0; }
                if (index < 0) { currentGraphicsSlide = graphicsSlides.length - 1; }
                
                for (var i = 0; i < graphicsSlides.length; i++) {
                    graphicsSlides[i].classList.remove('active');
                }
                for (var i = 0; i < graphicsDots.length; i++) {
                    graphicsDots[i].classList.remove('active');
                }
                
                graphicsSlides[currentGraphicsSlide].classList.add('active');
                graphicsDots[currentGraphicsSlide].classList.add('active');
                
                var animClasses = ['anim-fade', 'anim-zoom', 'anim-slide-left', 'anim-slide-right',
                    'anim-slide-up', 'anim-slide-down', 'anim-rotate', 'anim-blur',
                    'anim-flip', 'anim-bounce', 'anim-shake'];
                
                for (var i = 0; i < graphicsSlides.length; i++) {
                    for (var j = 0; j < animClasses.length; j++) {
                        graphicsSlides[i].classList.remove(animClasses[j]);
                    }
                }
                
                var randomIndex = Math.floor(Math.random() * animations.length);
                graphicsSlides[currentGraphicsSlide].classList.add(animations[randomIndex]);
            }

            function changeGraphicsSlide(direction) {
                currentGraphicsSlide += direction;
                showGraphicsSlide(currentGraphicsSlide);
                resetGraphicsAutoSlide();
            }

            function goToGraphicsSlide(index) {
                currentGraphicsSlide = index;
                showGraphicsSlide(currentGraphicsSlide);
                resetGraphicsAutoSlide();
            }

            function resetGraphicsAutoSlide() {
                clearInterval(graphicsAutoSlideInterval);
                if (graphicsSlides.length > 0) {
                    graphicsAutoSlideInterval = setInterval(function() {
                        currentGraphicsSlide++;
                        if (currentGraphicsSlide >= graphicsSlides.length) {
                            currentGraphicsSlide = 0;
                        }
                        showGraphicsSlide(currentGraphicsSlide);
                    }, 5000);
                }
            }

            if (graphicsSlides.length > 0) {
                showGraphicsSlide(0);
                graphicsAutoSlideInterval = setInterval(function() {
                    currentGraphicsSlide++;
                    if (currentGraphicsSlide >= graphicsSlides.length) {
                        currentGraphicsSlide = 0;
                    }
                    showGraphicsSlide(currentGraphicsSlide);
                }, 5000);
            }

            var galleryContainer = document.getElementById('gallerySlideshow');
            if (galleryContainer) {
                galleryContainer.addEventListener('mouseenter', function() {
                    clearInterval(graphicsAutoSlideInterval);
                });
                
                galleryContainer.addEventListener('mouseleave', function() {
                    if (graphicsSlides.length > 0) {
                        resetGraphicsAutoSlide();
                    }
                });
            }
        </script>
    '''
    
    return HttpResponse(f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AiahTech - Advanced Technology Solutions</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #2d2d2d;
                min-height: 100vh;
                color: white;
                padding: 20px;
            }}
            .container {{ max-width: 1100px; width: 100%; margin: 0 auto; text-align: center; }}
            
            /* ===== TOP BAR ===== */
            .top-bar {{
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 20px;
                position: relative;
            }}
            
            /* ===== MENU BUTTON (LEFT) ===== */
            .menu-btn {{
                position: absolute;
                left: 0;
                background: rgba(255,255,255,0.1);
                border: none;
                color: white;
                font-size: 30px;
                padding: 8px 15px;
                cursor: pointer;
                border-radius: 10px;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .menu-btn:hover {{
                background: rgba(255,255,255,0.2);
                transform: scale(1.05);
            }}
            
            /* ===== LOGO (CENTER) ===== */
            .logo-img {{
                max-width: 200px;
                height: auto;
            }}
            
            /* ===== WHATSAPP BUTTON (RIGHT) ===== */
            .whatsapp-btn {{
                position: absolute;
                right: 0;
                background: #25D366;
                border: none;
                color: white;
                font-size: 24px;
                padding: 10px 16px;
                cursor: pointer;
                border-radius: 50px;
                transition: all 0.3s ease;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            .whatsapp-btn:hover {{
                background: #1da851;
                transform: scale(1.05);
                box-shadow: 0 4px 20px rgba(37, 211, 102, 0.4);
            }}
            
            /* ===== SIDE MENU (SLIDE-OUT) ===== */
            .side-menu {{
                height: 100%;
                width: 0;
                position: fixed;
                top: 0;
                left: 0;
                background: #1a1a1a;
                overflow-x: hidden;
                transition: 0.4s ease;
                z-index: 1000;
                box-shadow: 2px 0 20px rgba(0,0,0,0.5);
                padding-top: 60px;
            }}
            
            .side-menu .close-btn {{
                position: absolute;
                top: 15px;
                right: 20px;
                font-size: 36px;
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                transition: 0.3s;
            }}
            .side-menu .close-btn:hover {{
                color: #4ade80;
                transform: rotate(90deg);
            }}
            
            .side-menu .menu-header {{
                padding: 0 25px 20px 25px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 20px;
            }}
            
            .side-menu .menu-header img {{
                max-width: 150px;
                height: auto;
            }}
            
            .side-menu .menu-header h2 {{
                font-size: 20px;
                margin-top: 10px;
                color: white;
            }}
            
            .side-menu .menu-header p {{
                color: rgba(255,255,255,0.5);
                font-size: 13px;
            }}
            
            .side-menu a {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 15px 25px;
                text-decoration: none;
                color: rgba(255,255,255,0.7);
                font-size: 16px;
                font-weight: 500;
                transition: all 0.3s ease;
                border-left: 3px solid transparent;
            }}
            
            .side-menu a:hover {{
                background: rgba(255,255,255,0.05);
                color: white;
                border-left-color: #4ade80;
            }}
            
            .side-menu a.active {{
                color: #4ade80;
                border-left-color: #4ade80;
                background: rgba(74, 222, 128, 0.05);
            }}
            
            .side-menu a .icon {{
                font-size: 20px;
                width: 30px;
                text-align: center;
            }}
            
            /* WhatsApp in side menu */
            .side-menu .whatsapp-menu {{
                border-top: 1px solid rgba(255,255,255,0.1);
                margin-top: 10px;
                padding-top: 10px;
            }}
            .side-menu .whatsapp-menu a {{
                color: #25D366;
            }}
            .side-menu .whatsapp-menu a:hover {{
                background: rgba(37, 211, 102, 0.1);
                border-left-color: #25D366;
                color: #25D366;
            }}
            
            /* ===== OVERLAY ===== */
            .overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.6);
                z-index: 999;
                backdrop-filter: blur(3px);
            }}
            
            .subtitle {{ font-size: 24px; opacity: 0.9; margin-bottom: 30px; font-weight: 300; }}
            
            .btn-group {{ display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; margin-top: 30px; }}
            .btn {{
                display: inline-block;
                padding: 14px 35px;
                background: white;
                color: #2d2d2d;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 600;
                font-size: 16px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }}
            .btn-outline {{ background: transparent; color: white; border: 2px solid white; }}
            .btn-outline:hover {{ background: white; color: #2d2d2d; }}
            .btn-green {{ background: #4ade80; color: #1a1a2e; }}
            .btn-green:hover {{ background: #22c55e; color: #1a1a2e; }}
            .btn-blue {{ background: #3b82f6; color: white; }}
            .btn-blue:hover {{ background: #2563eb; color: white; }}
            .btn-whatsapp {{ background: #25D366; color: white; }}
            .btn-whatsapp:hover {{ background: #1da851; color: white; transform: translateY(-2px); box-shadow: 0 4px 20px rgba(37, 211, 102, 0.4); }}
            
            .section {{
                margin-top: 40px;
                background: rgba(255,255,255,0.08);
                border-radius: 20px;
                padding: 40px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .section h2 {{
                font-size: 36px;
                margin-bottom: 15px;
            }}
            
            .computer-slideshow {{
                position: relative;
                max-width: 100%;
                margin: 30px auto;
                overflow: hidden;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                background: rgba(0, 0, 0, 0.4);
                min-height: 400px;
            }}
            
            .computer-slide {{
                display: none;
                width: 100%;
                animation: fadeIn 1.2s ease-in-out;
            }}
            
            .computer-slide.active {{ display: block; }}
            
            @keyframes fadeIn {{
                0% {{ opacity: 0; transform: scale(0.95); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            
            .computer-slide-content {{
                display: flex;
                align-items: center;
                padding: 30px;
                gap: 30px;
            }}
            
            .computer-slide-image {{ flex: 1; min-height: 300px; }}
            .computer-slide-image img {{
                width: 100%;
                height: 350px;
                object-fit: contain;
                border-radius: 10px;
                background: rgba(0, 0, 0, 0.2);
            }}
            
            .computer-slide-info {{ flex: 1; text-align: left; padding: 20px; }}
            .computer-slide-info h3 {{ font-size: 32px; margin-bottom: 10px; }}
            .computer-slide-info .brand {{ opacity: 0.7; font-size: 16px; margin-bottom: 10px; }}
            .computer-slide-info .specs {{ opacity: 0.8; font-size: 15px; margin: 10px 0; line-height: 1.8; }}
            .computer-slide-info .price {{ font-size: 32px; font-weight: 700; color: #4ade80; margin: 15px 0; }}
            .computer-slide-info .btn-view {{
                display: inline-block;
                padding: 12px 30px;
                background: #4ade80;
                color: #1a1a2e;
                text-decoration: none;
                border-radius: 30px;
                font-weight: 600;
                font-size: 16px;
                transition: all 0.3s ease;
            }}
            .computer-slide-info .btn-view:hover {{ background: #22c55e; transform: translateX(5px); }}
            
            .computer-controls {{
                position: absolute;
                top: 50%;
                width: 100%;
                display: flex;
                justify-content: space-between;
                transform: translateY(-50%);
                padding: 0 15px;
                z-index: 10;
            }}
            
            .computer-btn {{
                background: rgba(0, 0, 0, 0.6);
                color: white;
                border: none;
                padding: 15px 22px;
                cursor: pointer;
                border-radius: 50%;
                font-size: 28px;
                transition: all 0.3s ease;
                backdrop-filter: blur(5px);
            }}
            .computer-btn:hover {{ background: rgba(255, 255, 255, 0.3); transform: scale(1.15); }}
            
            .computer-dots {{ text-align: center; padding: 15px 0 5px 0; }}
            .computer-dot {{
                display: inline-block;
                width: 14px;
                height: 14px;
                margin: 0 8px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .computer-dot.active {{ background: #4ade80; transform: scale(1.4); }}
            .computer-dot:hover {{ background: rgba(255, 255, 255, 0.7); }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
                margin: 30px 0;
            }}
            .card {{
                background: rgba(255,255,255,0.08);
                padding: 25px;
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.1);
                transition: transform 0.3s ease;
                text-align: left;
            }}
            .card:hover {{ transform: translateY(-5px); }}
            .card .icon {{ font-size: 40px; display: block; margin-bottom: 10px; }}
            .card h4 {{ font-size: 18px; margin-bottom: 8px; }}
            .card p {{ opacity: 0.9; font-size: 14px; line-height: 1.6; }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin: 30px 0;
                padding: 20px;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
            }}
            .stat-item {{ text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: 700; display: block; }}
            .stat-label {{ opacity: 0.8; font-size: 14px; }}
            
            .gallery-slideshow {{
                position: relative;
                max-width: 100%;
                margin: 30px auto;
                overflow: hidden;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                background: rgba(0, 0, 0, 0.4);
                min-height: 400px;
            }}
            
            .gallery-slide {{
                display: none;
                width: 100%;
                position: relative;
            }}
            .gallery-slide.active {{ display: block; }}
            
            .gallery-slide img {{
                width: 100%;
                height: 500px;
                object-fit: contain;
                background: rgba(0, 0, 0, 0.2);
            }}
            
            .gallery-slide .slide-info {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 20px 30px;
                background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
                text-align: left;
            }}
            .gallery-slide .slide-info h4 {{ font-size: 24px; margin-bottom: 5px; }}
            .gallery-slide .slide-info p {{ opacity: 0.9; font-size: 14px; margin-bottom: 5px; }}
            .gallery-slide .slide-info .category {{
                display: inline-block;
                padding: 3px 15px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                font-size: 12px;
            }}
            
            @keyframes animFade {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
            @keyframes animZoom {{ 0% {{ opacity: 0; transform: scale(0.5); }} 100% {{ opacity: 1; transform: scale(1); }} }}
            @keyframes animSlideLeft {{ 0% {{ opacity: 0; transform: translateX(80px); }} 100% {{ opacity: 1; transform: translateX(0); }} }}
            @keyframes animSlideRight {{ 0% {{ opacity: 0; transform: translateX(-80px); }} 100% {{ opacity: 1; transform: translateX(0); }} }}
            @keyframes animSlideUp {{ 0% {{ opacity: 0; transform: translateY(80px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes animSlideDown {{ 0% {{ opacity: 0; transform: translateY(-80px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes animRotate {{ 0% {{ opacity: 0; transform: rotate(-20deg) scale(0.7); }} 100% {{ opacity: 1; transform: rotate(0) scale(1); }} }}
            @keyframes animBlur {{ 0% {{ opacity: 0; filter: blur(10px); }} 100% {{ opacity: 1; filter: blur(0); }} }}
            @keyframes animFlip {{ 0% {{ opacity: 0; transform: rotateY(90deg); }} 100% {{ opacity: 1; transform: rotateY(0); }} }}
            @keyframes animBounce {{ 0% {{ opacity: 0; transform: scale(0.3); }} 50% {{ opacity: 1; transform: scale(1.05); }} 70% {{ transform: scale(0.95); }} 100% {{ transform: scale(1); }} }}
            @keyframes animShake {{ 0% {{ opacity: 0; transform: translateX(-50px); }} 25% {{ transform: translateX(20px); }} 50% {{ transform: translateX(-15px); }} 75% {{ transform: translateX(10px); }} 100% {{ opacity: 1; transform: translateX(0); }} }}
            
            .anim-fade {{ animation: animFade 1.2s ease-in-out; }}
            .anim-zoom {{ animation: animZoom 1.2s ease-in-out; }}
            .anim-slide-left {{ animation: animSlideLeft 1.2s ease-in-out; }}
            .anim-slide-right {{ animation: animSlideRight 1.2s ease-in-out; }}
            .anim-slide-up {{ animation: animSlideUp 1.2s ease-in-out; }}
            .anim-slide-down {{ animation: animSlideDown 1.2s ease-in-out; }}
            .anim-rotate {{ animation: animRotate 1.2s ease-in-out; }}
            .anim-blur {{ animation: animBlur 1.2s ease-in-out; }}
            .anim-flip {{ animation: animFlip 1.2s ease-in-out; }}
            .anim-bounce {{ animation: animBounce 1.2s ease-in-out; }}
            .anim-shake {{ animation: animShake 1.2s ease-in-out; }}
            
            .gallery-controls {{
                position: absolute;
                top: 50%;
                width: 100%;
                display: flex;
                justify-content: space-between;
                transform: translateY(-50%);
                padding: 0 15px;
                z-index: 10;
            }}
            
            .gallery-btn {{
                background: rgba(0, 0, 0, 0.6);
                color: white;
                border: none;
                padding: 15px 22px;
                cursor: pointer;
                border-radius: 50%;
                font-size: 28px;
                transition: all 0.3s ease;
                backdrop-filter: blur(5px);
            }}
            .gallery-btn:hover {{ background: rgba(255, 255, 255, 0.3); transform: scale(1.15); }}
            
            .gallery-dots {{ text-align: center; padding: 20px 0 10px 0; }}
            .gallery-dot {{
                display: inline-block;
                width: 14px;
                height: 14px;
                margin: 0 8px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .gallery-dot.active {{ background: #4ade80; transform: scale(1.4); }}
            .gallery-dot:hover {{ background: rgba(255, 255, 255, 0.7); }}
            
            .status {{
                margin-top: 40px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                font-size: 14px;
                opacity: 0.8;
            }}
            .status i {{
                display: inline-block;
                width: 10px;
                height: 10px;
                background: #4ade80;
                border-radius: 50%;
                margin-right: 8px;
            }}
            
            @media (max-width: 600px) {{
                .subtitle {{ font-size: 18px; }}
                .logo-img {{ max-width: 130px; }}
                .menu-btn {{ font-size: 24px; padding: 5px 12px; }}
                .whatsapp-btn {{ font-size: 18px; padding: 6px 12px; }}
                .whatsapp-btn span {{ display: none; }}
                .btn-group .btn {{ padding: 10px 20px; font-size: 14px; }}
                .computer-slide-content {{
                    flex-direction: column;
                    padding: 15px;
                }}
                .computer-slide-image img {{ height: 200px; }}
                .computer-slide-info h3 {{ font-size: 24px; }}
                .computer-slide-info .price {{ font-size: 24px; }}
                .computer-btn {{ padding: 10px 16px; font-size: 20px; }}
                .gallery-slide img {{ height: 300px; }}
                .gallery-btn {{ padding: 10px 16px; font-size: 20px; }}
                .gallery-slide .slide-info h4 {{ font-size: 18px; }}
                .gallery-slide .slide-info {{ padding: 15px; }}
                .grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <!-- ===== OVERLAY ===== -->
        <div class="overlay" id="overlay" onclick="closeMenu()"></div>

        <!-- ===== SIDE MENU ===== -->
        <div class="side-menu" id="sideMenu">
            <button class="close-btn" onclick="closeMenu()">✕</button>
            <div class="menu-header">
                <img src="/static/images/Business_Loggo_2.png" alt="AiahTech Logo">
                <h2>AiahTech</h2>
                <p>Advanced Technology Solutions</p>
            </div>
            <a href="/" class="active"><span class="icon">🏠</span> Home</a>
            <a href="/computers/"><span class="icon">🖥️</span> Computers for Sale</a>
            <a href="/apps/"><span class="icon">📱</span> Our Apps</a>
            <a href="/about/"><span class="icon">📖</span> About</a>
            <a href="mailto:info@aiahtech.com"><span class="icon">📧</span> Email</a>
            <div class="whatsapp-menu">
                <a href="https://wa.me/23279174763?text=Hello%20AiahTech%2C%20I%20need%20your%20services" target="_blank">
                    <span class="icon">💬</span> WhatsApp
                </a>
            </div>
            <a href="/admin/"><span class="icon">🔐</span> Admin Panel</a>
        </div>

        <div class="container">
            <!-- ===== TOP BAR ===== -->
            <div class="top-bar">
                <button class="menu-btn" onclick="openMenu()">☰</button>
                <a href="/">
                    <img src="/static/images/Business_Loggo_2.png" alt="AiahTech Logo" class="logo-img">
                </a>
                <a href="https://wa.me/23279174763?text=Hello%20AiahTech%2C%20I%20need%20your%20services" target="_blank" class="whatsapp-btn">
                    💬 <span>WhatsApp</span>
                </a>
            </div>
            
            <p class="subtitle">Advanced Technology Solutions for Modern Business</p>
            
            <div class="btn-group">
                <a href="/about/" class="btn btn-outline">📖 Learn More</a>
                <a href="/apps/" class="btn btn-blue">📱 Our Apps</a>
            </div>

            <!-- ===== COMPUTER SLIDESHOW ===== -->
            <div class="section">
                <h3>🖥️ Computers for Sale</h3>
                <p style="opacity: 0.9; font-size: 18px;">Quality computers at great prices</p>
                
                <div class="computer-slideshow" id="computerSlideshow">
                    <div class="computer-controls">
                        <button class="computer-btn" onclick="changeComputerSlide(-1)">❮</button>
                        <button class="computer-btn" onclick="changeComputerSlide(1)">❯</button>
                    </div>
                    
                    <div id="computerSlides">
                        {computers_slides_html}
                    </div>
                    
                    <div class="computer-dots" id="computerDots">
                        {computers_dots_html}
                    </div>
                    
                    <a href="/computers/" class="btn btn-green" style="margin-top: 10px; display: inline-block; margin-bottom: 15px;">View All Computers →</a>
                </div>
            </div>

            <!-- REPAIR SERVICES -->
            <div class="section">
                <h3>🔧 Computer Repair Services</h3>
                <p style="opacity: 0.9; font-size: 18px;">Expert repair services for all your computer needs</p>
                
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-number">{total_repairs}+</span>
                        <span class="stat-label">Repairs Completed</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{satisfaction_rate}</span>
                        <span class="stat-label">Satisfaction Rate</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{turnaround_time}</span>
                        <span class="stat-label">Turnaround Time</span>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <span class="icon">💻</span>
                        <h4>Hardware Repair</h4>
                        <p>Screen replacement, keyboard repair, motherboard diagnosis, battery replacement, and more.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🛠️</span>
                        <h4>Software Fix</h4>
                        <p>Operating system installation, software troubleshooting, driver updates, and system optimization.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🛡️</span>
                        <h4>Virus Removal</h4>
                        <p>Complete virus and malware removal, system cleanup, and security hardening.</p>
                    </div>
                    <div class="card">
                        <span class="icon">💾</span>
                        <h4>Data Recovery</h4>
                        <p>Recover lost files, corrupted drives, and accidental deletions from any storage device.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🔋</span>
                        <h4>Upgrade Services</h4>
                        <p>RAM upgrades, SSD installation, processor upgrades, and performance optimization.</p>
                    </div>
                    <div class="card">
                        <span class="icon">📞</span>
                        <h4>Remote Support</h4>
                        <p>Get expert help remotely without leaving your home or office.</p>
                    </div>
                </div>
            </div>

            <!-- MOBILE UNLOCKING -->
            <div class="section">
                <h3>📱 Mobile Unlocking & Software Repair</h3>
                <p style="opacity: 0.9; font-size: 18px;">Professional mobile services to keep your devices running smoothly</p>
                
                <div class="grid">
                    <div class="card">
                        <span class="icon">🔓</span>
                        <h4>Phone Unlocking</h4>
                        <p>Network unlocking, carrier unlocking, and factory reset for all phone brands including iPhone, Samsung, and more.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🔄</span>
                        <h4>Software Update</h4>
                        <p>OS updates, firmware upgrades, software flashing, and system restoration for mobile devices.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🛡️</span>
                        <h4>Malware Removal</h4>
                        <p>Complete virus and malware removal, phone cleanup, and security optimization for mobile devices.</p>
                    </div>
                    <div class="card">
                        <span class="icon">📲</span>
                        <h4>Data Recovery</h4>
                        <p>Recover deleted messages, contacts, photos, and other important data from your mobile device.</p>
                    </div>
                    <div class="card">
                        <span class="icon">⚙️</span>
                        <h4>Phone Optimization</h4>
                        <p>Speed up slow phones, battery optimization, storage cleaning, and performance boosting.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🔋</span>
                        <h4>Battery Replacement</h4>
                        <p>Professional battery replacement and repair services for all mobile phone brands.</p>
                    </div>
                </div>
            </div>

            <!-- WEBSITE DEVELOPMENT -->
            <div class="section">
                <h3>🌐 Website Development</h3>
                <p style="opacity: 0.9; font-size: 18px;">Custom websites built with modern technologies for your business</p>
                
                <div class="grid">
                    <div class="card">
                        <span class="icon">🖌️</span>
                        <h4>Custom Web Design</h4>
                        <p>Beautiful, responsive, and user-friendly website designs tailored to your brand identity.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🛍️</span>
                        <h4>E-Commerce Solutions</h4>
                        <p>Online stores with secure payment integration, inventory management, and shopping cart functionality.</p>
                    </div>
                    <div class="card">
                        <span class="icon">📝</span>
                        <h4>CMS Development</h4>
                        <p>Content management systems that allow you to easily update and manage your website content.</p>
                    </div>
                    <div class="card">
                        <span class="icon">⚡</span>
                        <h4>Web Applications</h4>
                        <p>Custom web applications with advanced functionality and seamless user experience.</p>
                    </div>
                    <div class="card">
                        <span class="icon">📱</span>
                        <h4>Responsive Design</h4>
                        <p>Websites that work perfectly on all devices - desktop, tablet, and mobile.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🚀</span>
                        <h4>Performance Optimization</h4>
                        <p>Fast-loading websites with SEO optimization and high-performance hosting solutions.</p>
                    </div>
                </div>
            </div>

            <!-- AI DEVELOPMENT -->
            <div class="section">
                <h3>🤖 AI Development</h3>
                <p style="opacity: 0.9; font-size: 18px;">Cutting-edge artificial intelligence solutions for your business</p>
                
                <div class="grid">
                    <div class="card">
                        <span class="icon">🧠</span>
                        <h4>Machine Learning</h4>
                        <p>Custom ML models for predictive analytics, pattern recognition, and intelligent decision-making.</p>
                    </div>
                    <div class="card">
                        <span class="icon">💬</span>
                        <h4>Chatbots & Virtual Assistants</h4>
                        <p>AI-powered chatbots for customer support, lead generation, and automated conversations.</p>
                    </div>
                    <div class="card">
                        <span class="icon">📊</span>
                        <h4>Data Analytics</h4>
                        <p>Advanced data analysis and visualization to uncover insights and drive business growth.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🎯</span>
                        <h4>Natural Language Processing</h4>
                        <p>Text analysis, sentiment analysis, language translation, and document processing.</p>
                    </div>
                    <div class="card">
                        <span class="icon">🖼️</span>
                        <h4>Computer Vision</h4>
                        <p>Image and video analysis, object detection, facial recognition, and visual search.</p>
                    </div>
                    <div class="card">
                        <span class="icon">⚙️</span>
                        <h4>AI Automation</h4>
                        <p>Intelligent process automation and workflow optimization using AI technologies.</p>
                    </div>
                </div>
            </div>

            <!-- ===== GRAPHICS SLIDESHOW ===== -->
            <div class="section">
                <h3>🎨 Graphics Design Gallery</h3>
                <p style="opacity: 0.9; font-size: 18px;">Showcasing our creative design work</p>
                
                <div class="gallery-slideshow" id="gallerySlideshow">
                    <div class="gallery-controls">
                        <button class="gallery-btn" onclick="changeGraphicsSlide(-1)">❮</button>
                        <button class="gallery-btn" onclick="changeGraphicsSlide(1)">❯</button>
                    </div>
                    
                    <div id="gallerySlides">
                        {graphics_slides_html}
                    </div>
                    
                    <div class="gallery-dots" id="galleryDots">
                        {graphics_dots_html}
                    </div>
                </div>
            </div>
            
            <div class="status"><i></i> Django 4.2.7 • System Ready • AiahTech v1.0</div>
        </div>

        {js_script}
    </body>
    </html>
    ''')


# ============ ABOUT PAGE ============
def about(request):
    return HttpResponse('''
    <html>
    <head>
        <title>About AiahTech</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center;
                padding: 50px;
                background: #2d2d2d;
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            h1 {
                font-size: 48px;
                color: #4ade80;
                margin-bottom: 20px;
            }
            .subtitle {
                font-size: 20px;
                color: #ccc;
                margin-bottom: 30px;
            }
            .about-text {
                font-size: 16px;
                color: #aaa;
                line-height: 1.8;
                margin-bottom: 30px;
            }
            .back {
                display: inline-block;
                padding: 12px 35px;
                background: #4ade80;
                color: #1a1a2e;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .back:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(74, 222, 128, 0.3);
            }
            .features-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-item {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .feature-item .icon {
                font-size: 30px;
                display: block;
                margin-bottom: 10px;
            }
            .feature-item h4 {
                color: #4ade80;
                margin-bottom: 5px;
            }
            .feature-item p {
                color: #888;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>About AiahTech</h2>
            <p class="subtitle">Advanced Technology Solutions for Modern Business</p>
            
            <div class="about-text">
                <p>AiahTech is owned by Joseph Aiah Gbonia 
                a Technology Scientist, researcher live in sierra leone. AiahTech is a technology solutions provider dedicated to transforming ideas into innovative digital experiences,
                problem solving with the influence of technology ideas and more.</p>
                <br>
                <p>Our goal is to spread your business to reach out to customers 
                withe the help of technology and create awearness regards technology to the world including the remote areas, 
                ensuring humans living on earth become more simple and interesting</p>
                <h2>Direct phone contact</h2>
                <p>+23279174763</p>
            </div>
            
           
            
            <div style="margin: 30px 0; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 10px;">
                <p style="color: #888; font-size: 14px;">📍 Based in Freetown Sierra Leone</p>
                <p style="color: #888; font-size: 14px;">📧 josephgbonia123@gmail.com</p>
                <p style="color: #888; font-size: 14px;">📞 +23279174763</p>
            </div>
            
            <a href="/" class="back">🏠 Back to Home</a>
        </div>
    </body>
    </html>
    ''')


# ============ COMPUTER STORE (Full Page) ============
def computers(request):
    computers_list = Computer.objects.filter(status='available')
    
    brand = request.GET.get('brand')
    if brand:
        computers_list = computers_list.filter(brand=brand)
    
    condition = request.GET.get('condition')
    if condition:
        computers_list = computers_list.filter(condition=condition)
    
    os = request.GET.get('os')
    if os:
        computers_list = computers_list.filter(operating_system=os)
    
    search = request.GET.get('search')
    if search:
        computers_list = computers_list.filter(
            Q(title__icontains=search) |
            Q(brand__icontains=search) |
            Q(model__icontains=search) |
            Q(processor__icontains=search)
        )
    
    paginator = Paginator(computers_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'computers': page_obj,
        'brands': Computer.objects.values_list('brand', flat=True).distinct(),
        'conditions': Computer.objects.values_list('condition', flat=True).distinct(),
        'oss': Computer.objects.values_list('operating_system', flat=True).distinct(),
        'current_brand': brand,
        'current_condition': condition,
        'current_os': os,
        'search_query': search,
    }
    return render(request, 'core/computers.html', context)


def computer_detail(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)
    similar = Computer.objects.filter(
        Q(brand=computer.brand) | Q(processor__icontains=computer.processor[:10]),
        status='available'
    ).exclude(id=computer.id)[:4]
    
    context = {
        'computer': computer,
        'similar': similar,
    }
    return render(request, 'core/computer_detail.html', context)


def inquire_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        budget = request.POST.get('budget')
        
        inquiry = ComputerInquiry(
            computer=computer,
            client_name=name,
            client_email=email,
            client_phone=phone,
            message=message,
            budget=budget if budget else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        inquiry.save()
        
        messages.success(request, f"✅ Thank you! Your inquiry about {computer.title} has been sent. We'll get back to you shortly!")
        return redirect('computer_detail', computer_id=computer.id)
    
    return redirect('computer_detail', computer_id=computer.id)


# ============ APP DOWNLOAD SECTION ============
def apps(request):
    apps_list = App.objects.filter(status__in=['active', 'beta'])
    
    platform = request.GET.get('platform')
    if platform:
        apps_list = apps_list.filter(platform=platform)
    
    search = request.GET.get('search')
    if search:
        apps_list = apps_list.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(features__icontains=search)
        )
    
    featured_apps = apps_list.filter(is_featured=True)[:3]
    
    paginator = Paginator(apps_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    platforms = App.objects.values_list('platform', flat=True).distinct()
    
    context = {
        'apps': page_obj,
        'featured_apps': featured_apps,
        'platforms': platforms,
        'current_platform': platform,
        'search_query': search,
    }
    return render(request, 'core/apps.html', context)


def app_detail(request, slug):
    app = get_object_or_404(App, slug=slug, status__in=['active', 'beta'])
    related_apps = App.objects.filter(platform=app.platform, status__in=['active', 'beta']).exclude(id=app.id)[:4]
    
    context = {
        'app': app,
        'related_apps': related_apps,
    }
    return render(request, 'core/app_detail.html', context)


def download_app(request, slug):
    app = get_object_or_404(App, slug=slug, status__in=['active', 'beta'])
    
    app.download_count += 1
    app.save()
    
    file_path = app.download_file.path
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    else:
        messages.error(request, "File not found. Please contact support.")
        return redirect('app_detail', slug=app.slug)