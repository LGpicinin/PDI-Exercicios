import numpy as np
import cv2
import sys

IMG_60 = './imagens/60.bmp'
IMG_82 = './imagens/82.bmp'
IMG_114 = './imagens/114.bmp'
IMG_150 = './imagens/150.bmp'
IMG_205 = './imagens/205.bmp'




def changeImage (img, img_out):

    img_aux = img.copy

    # passa o filtro da média
    img_aux = cv2.blur(img, [101, 101])
    cv2.imwrite ('./resultados/blur.png', img_aux*255)

    # subtrai imagem original da imagem borrada
    img_out = img - img_aux
    cv2.imwrite ('./resultados/sum.png', img_out*255)

    # binariza
    ret, img_out = cv2.threshold(img_out, 0.2, 1, cv2.THRESH_BINARY)
    cv2.imwrite ('./resultados/out.png', img_out*255)



def main ():

    print("\nEscolha uma imagem: ")
    escolha = input()

    img_path = "./imagens/" + escolha + ".bmp"
    
    # Abre a imagem em escala de cinza.
    img = cv2.imread (img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    img = img.astype (np.float32) / 255

    img_out = img.copy()
    cv2.imwrite ('./resultados/original.png', img_out*255)

    changeImage(img, img_out)



if __name__ == '__main__':
    main ()