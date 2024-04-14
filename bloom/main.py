import sys
import timeit
import numpy as np
import cv2



IMG_WINDWAKER = './imagens/Wind Waker GC.bmp'
IMG_GT2 = './imagens/GT2.BMP'



    
def brightPass(img, img_out):
    soma = 0
    media = 0
    rols, cols, channels = img.shape

    for row in range(0, rols):
        for col in range(0, cols):
            soma = 0
            for channel in range(0, channels):
                soma = soma + img[row, col, channel]
            media = soma/3
            if media < 0.5:
                for channel in range(0, channels):
                    img_out[row, col, channel] = 0



def borraFiltroGaussiano(img):
    imgs = []
    desvio = 4

    for i in range(0, 4):
        imgs.append(cv2.GaussianBlur(img, (29, 29), desvio))
        desvio = desvio*2
    
    img_out = imgs[0].copy()
    for i in range(1, 4):
        img_out = img_out + imgs[i]
    
    return img_out



def borraFiltroMedia(img):
    imgs = []
    tam_janela = 9

    for i in range(0, 4):

        img_aux = img.copy()

        for j in range(0, 4):
            img_aux = cv2.blur(img_aux, [tam_janela, tam_janela])

        imgs.append(img_aux)
        tam_janela = tam_janela + 2
    
    img_out = imgs[0].copy()
    for i in range(1, 4):
        img_out = img_out + imgs[i]
    
    return img_out

            
                





def main():

    # escolhe uma imagem

    imgPath = ""

    print("\nDigite uma imagem(Ex.: 1): \n1-GT2\n2-Wind Waker")
    choose = input()

    if int(choose) == 1:
        imgPath = IMG_GT2
    else:
        imgPath = IMG_WINDWAKER
        
    img = cv2.imread (imgPath, cv2.IMREAD_COLOR)
    if img is None:
        print('Erro ao abrir a imagem')
        sys.exit()

    img = img.astype (np.float32) / 255



    #faz uma versão bright pass da imagem (máscara)

    img_brightPass = img.copy()
    brightPass(img, img_brightPass)
    cv2.imwrite ('brightPass.png', img_brightPass*255)


    # borra máscara usando filtro gaussiano e filtro da média

    img_borradaGaussiano = borraFiltroGaussiano(img_brightPass)
    cv2.imwrite ('borradaGaussiano.png', img_borradaGaussiano*255)

    img_borradaMedia = borraFiltroMedia(img_brightPass)
    cv2.imwrite ('borradaMedia.png', img_borradaMedia*255)


    # soma original com a máscara

    img_bloomGaussiano = img.copy()
    img_bloomGaussiano = img*0.8 + img_borradaGaussiano*0.2
    cv2.imwrite ('bloomGaussiano.png', img_bloomGaussiano*255)

    img_bloomMedia = img.copy()
    img_bloomMedia = img*0.8 + img_borradaMedia*0.2
    cv2.imwrite ('bloomMedia.png', img_bloomMedia*255)



if __name__ == '__main__':
    main()