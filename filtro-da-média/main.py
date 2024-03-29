import sys
import timeit
import numpy as np
import cv2



IMG_WHITE_BLACK = './Exemplos/a01 - Original.bmp'
IMG_COLORED = './Exemplos/b01 - Original.bmp'


def filtroIngenuo(altura, largura, img, img_out, canal):

    larguraTotal = (largura*2) + 1
    alturaTotal = (altura*2) + 1
    rows, cols, channel = img.shape

    for row in range(altura+1, rows-altura):
        for col in range(largura+1, cols-largura):
            soma = 0
            for x in range(col-largura, col+largura+1):
                for y in range(row-altura, row+altura+1):
                    soma = soma + img[y, x, canal]
            img_out[row, col, canal] = soma/(alturaTotal*larguraTotal)





def filtroSeparavel(altura, largura, img, img_out, canal):

    larguraTotal = (largura*2) + 1
    alturaTotal = (altura*2) + 1
    rows, cols, channel = img.shape
    img_aux = img.copy()

    for row in range(0, rows):
        for col in range(largura+1, cols-largura):
            soma = 0
            for x in range(col-largura, col+largura+1):
                soma = soma + img[row, x, canal]
            img_aux[row, col, canal] = soma/(larguraTotal)

    for row in range(altura+1, rows-altura):
        for col in range(largura+1, cols-largura):
            soma = 0
            for y in range(row-altura, row+altura+1):
                soma = soma + img_aux[y, col, canal]
            img_out[row, col, canal] = soma/(alturaTotal)  




def imagemIntegral(altura, largura, img, img_out, canal):

    larguraTotal = (largura*2) + 1
    alturaTotal = (altura*2) + 1
    rows, cols, channel = img.shape
    img_integral = img.copy()

    for row in range(0, rows):
        img_integral[row, 0, canal] = img[row, 0, canal]
        for col in range(1, cols):
            img_integral[row, col, canal] = img[row, col, canal] + img_integral[row, col-1, canal]

    for row in range(1, rows):
        for col in range(0, cols):
            img_integral[row, col, canal] = img_integral[row, col, canal] + img_integral[row-1, col, canal]

    for row in range(altura+1, rows-altura):
        for col in range(largura+1, cols-largura):
            soma = 0
            bottomRight = img_integral[row+altura, col+largura, canal]
            if row-(altura+1) < 0 or col-(largura+1) < 0:
                if row-(altura+1) < 0 and col-(largura+1) < 0:
                    soma = bottomRight
                elif row-(altura+1) < 0:
                    soma = bottomRight - img_integral[row+altura, col-(largura+1), canal]
                else:
                    soma = bottomRight - img_integral[row-(altura+1), col+largura, canal]
            else:
                bottomLeft = img_integral[row+altura, col-(largura+1), canal]
                topRight = img_integral[row-(altura+1), col+largura, canal]
                topLeft = img_integral[row-(altura+1), col-(largura+1), canal]
                soma = bottomRight - topRight - bottomLeft + topLeft

            img_out[row, col, canal] = soma/(alturaTotal*larguraTotal)
    





def main():

    # escolha entre colorido/preto e branco

    colorido = False

    print("\nDigite uma das opções(Ex.: 1): \n1-Preto e branco\n2-Colorido")
    cor = input()

    if int(cor) == 1:
        img = cv2.imread (IMG_WHITE_BLACK, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print('Erro ao abrir a imagem')
            sys.exit()
        img = img.reshape ((img.shape [0], img.shape [1], 1))

    else:
        colorido = True
        img = cv2.imread (IMG_COLORED, cv2.IMREAD_COLOR)
        if img is None:
            print('Erro ao abrir a imagem')
            sys.exit()

    
    #escolha da altura e da largura(ambos vão ser multiplicados por 2 e somado 1 nas funções)
            
    print( '\nDefina a largura da janela')
    largura = input()

    print( '\nDefina a altura da janela')
    altura = input()

    lar = int(largura)
    alt = int(altura)


    #chama as diferentes funções para calcular filtro da média

    rows, cols, channel = img.shape
    img = img.astype (np.float32) / 255

    img_ingenuo = img.copy()
    print('\nFiltro ingênuo começou')
    for ch in range(channel):
        filtroIngenuo(alt, lar, img, img_ingenuo, ch)
    print('\nFiltro ingênuo terminou')

    img_separavel = img.copy()
    print("\nFitro separável começou")
    for ch in range(channel):
        filtroSeparavel(alt, lar, img, img_separavel, ch)
    print("\nFitro separável terminou")

    img_integral = img.copy()
    print("\nImagem Integral começou")
    for ch in range(channel):
        imagemIntegral(alt, lar, img, img_integral, ch)
    print("\nImagem Integral terminou")

    print("\nFitro do opencv começou")
    img_out_cv2 = cv2.blur(img,[lar*2 + 1, alt*2 + 1])
    print("\nFitro do opencv terminou")



    #calcula diferença entre as funções implementadas e a do OpenCv

    if colorido == False:
        img_out_cv2 = img_out_cv2.reshape ((img_out_cv2.shape [0], img_out_cv2.shape [1], 1))
    provaIngenuo = (img_out_cv2-img_ingenuo)*10
    provaSeparável = (img_out_cv2-img_separavel)*10
    provaIntegral = (img_out_cv2-img_integral)*10



    #salva resultados em uma imagem
   
    cv2.imwrite ('provaIngenuo.png', provaIngenuo*255)
    cv2.imwrite ('provaSeparavel.png', provaSeparável*255)
    cv2.imwrite ('provaIntegral.png', provaIntegral*255)

    cv2.imwrite ('filtroIngenuo.png', img_ingenuo*255)
    cv2.imwrite ('filtroSeparavel.png', img_separavel*255)
    cv2.imwrite ('filtroImagemIntegral.png', img_integral*255)
    cv2.imwrite ('filtroOpenCv.png', img_out_cv2*255)


if __name__ == '__main__':
    main()