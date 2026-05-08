from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

# Abrir o screenshot do Instagram que contém a logo
img = Image.open('/home/ubuntu/upload/IMG_1200.jpg')
w, h = img.size
print(f"Imagem original: {w}x{h}")

# A logo circular está no canto superior esquerdo do perfil
# Baseado na imagem 945x2048, a logo está aproximadamente em:
# x: 30 a 200, y: 530 a 700 (área do avatar do perfil)
# Logo circular está em ~x:30-200, y:620-820 na imagem 945x2048
# Logo circular está em ~x:28-215, y:820-1020 na imagem 945x2048
logo_crop = img.crop((28, 820, 215, 1020))
logo_crop = logo_crop.resize((400, 400), Image.LANCZOS)
logo_crop.save('/home/ubuntu/video-anchor/assets/logo_raw_crop.png')
print("Logo recortada salva.")

# Também salvar versão maior para uso no vídeo
logo_large = logo_crop.resize((800, 800), Image.LANCZOS)
logo_large.save('/home/ubuntu/video-anchor/assets/logo_large.png')
print("Logo grande salva.")
