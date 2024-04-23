import numpy as np
import cv2
import sys
import math

IMG_60 = './imagens/60.bmp'
IMG_82 = './imagens/82.bmp'
IMG_114 = './imagens/114.bmp'
IMG_150 = './imagens/150.bmp'
IMG_205 = './imagens/205.bmp'

N_PIXELS_MIN = 50
N_PIXELS_MAX = 250

class Component:
    def __init__(self, label, n_pixels, n_arroz, t, l, b, r) -> None:
        self.label = label
        self.n_pixels = n_pixels
        self.n_arroz = n_arroz
        self.top = t
        self.left = l
        self.bottom = b
        self.right = r

def calculaDesvioPixels(dictionary, media):
    count_comp = 0
    sum_desvio = 0

    for i in range(0, len(dictionary)):
        comp = dictionary[i]
        if (comp.n_pixels - media) > 0:
            sum_desvio = sum_desvio + (comp.n_pixels - media)
            count_comp = count_comp + 1
    desvio_medio = float(sum_desvio/count_comp)
    print("\ndesvio medio pixels = " + str(desvio_medio))

    return desvio_medio

def calculaDesvioAltura(dictionary, media):
    count_comp = 0
    sum_desvio = 0

    for i in range(0, len(dictionary)):
        comp = dictionary[i]
        if (comp.bottom - comp.top) - media > 0:
            sum_desvio = sum_desvio + ((comp.bottom - comp.top) - media)
            count_comp = count_comp + 1
    desvio_medio = float(sum_desvio/count_comp)
    print("\ndesvio medio altura = " + str(desvio_medio))

    return desvio_medio

def calculaDesvioLargura(dictionary, media):
    count_comp = 0
    sum_desvio = 0

    for i in range(0, len(dictionary)):
        comp = dictionary[i]
        if (comp.right - comp.left) - media > 0:
            sum_desvio = sum_desvio + ((comp.right - comp.left) - media)
            count_comp = count_comp + 1
    desvio_medio = float(sum_desvio/count_comp)
    print("\ndesvio medio largura = " + str(desvio_medio))

    return desvio_medio

def testaComponentes (dictionary, mediaPixels, mediaLargura, mediaAltura):


    print("\nmedia pixels = " + str(mediaPixels))
    print("\nmedia altura = " + str(mediaAltura))
    print("\nmedia largura = " + str(mediaLargura))

    desvioPixels = calculaDesvioPixels(dictionary, mediaPixels)
    desvioLargura = calculaDesvioLargura(dictionary, mediaLargura)
    desvioAltura = calculaDesvioAltura(dictionary, mediaAltura)

    fatorPixels = float(1 - float(desvioPixels/(mediaPixels+desvioPixels)))
    fatorLargura = float(1 - float(desvioLargura/(mediaLargura+desvioLargura)))
    fatorAltura = float(1 - float(desvioAltura/(mediaAltura+desvioAltura)))

    if fatorPixels<fatorAltura and fatorPixels<fatorLargura:
        if(desvioPixels>mediaPixels):
            fatorPixels = fatorPixels * 0.62
        else:
            fatorPixels = fatorPixels * 0.7
    elif fatorAltura<fatorPixels and fatorAltura<fatorLargura:
        fatorAltura = fatorAltura * 0.73
    elif fatorLargura<fatorPixels and fatorLargura<fatorAltura:
        fatorLargura = fatorLargura * 0.73


    print("\nfator pixels = " + str(fatorPixels))
    print("\nfator altura = " + str(fatorAltura))
    print("\nfator largura = " + str(fatorLargura))

    sumPixels = mediaPixels*fatorPixels
    sumLargura = mediaLargura*fatorLargura
    sumAltura = mediaAltura*fatorAltura

    #print("\nsoma = " + str(sum))

    for i in range(0, len(dictionary)):
        comp = dictionary[i]
        #print(str(comp.n_pixels))

            #dictionary.append(comp)
        comp.n_arroz = 1
        countPixels = mediaPixels + sumPixels
        countLargura = mediaLargura + sumLargura
        countAltura = mediaAltura + sumAltura
        while comp.n_pixels > countPixels or (comp.bottom - comp.top) > countAltura or (comp.right - comp.left) > countLargura:
            countPixels = countPixels + sumPixels
            countAltura = countAltura + sumAltura
            countLargura = countLargura + sumLargura
            comp.n_arroz = comp.n_arroz + 1



def inunda (img, row, col, comp: Component, lenCol, lenRow):

    filaRow = []
    filaCol = []
    filaRow.append(row)
    filaCol.append(col)

    img[row, col] = comp.label
    comp.n_pixels = comp.n_pixels + 1

    while len(filaRow) > 0:
        
        row = filaRow.pop(0)
        col = filaCol.pop(0)

        if row > comp.bottom:
            comp.bottom = row
        elif row < comp.top:
            comp.top = row
        
        if col < comp.left:
            comp.left = col
        elif col > comp.right:
            comp.right = col

        #print("\nrow = " + str(row) + "\ncol = " + str(col))

        if (row+1 in range(0, lenRow)):
            if img[row+1, col] == 1:
                img[row+1, col] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col)
                filaRow.append(row+1)

        if (col+1 in range(0, lenCol)):
            if img[row, col+1] == 1:
                img[row, col+1] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col+1)
                filaRow.append(row)

        if (row-1 in range(0, lenRow)):
            if img[row-1, col] == 1:
                img[row-1, col] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col)
                filaRow.append(row-1)

        if (col-1 in range(0, lenCol)):
            if img[row, col-1] == 1:
                img[row, col-1] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col-1)
                filaRow.append(row)


def rotula (img):

    rows, cols = img.shape
    label = 2
    dictionary = []
    sum_pixels = 0
    sum_altura = 0
    sum_largura = 0

    for row in range (rows):
        for col in range (cols):
            #print(str(img[row, col]))
            if img[row, col] == 1:
                comp = Component(label, 0, 0, row, col, row, col)
                inunda(img, row, col, comp, cols, rows)

                if comp.n_pixels >= N_PIXELS_MIN:
                    dictionary.append(comp)
                    sum_pixels = sum_pixels + comp.n_pixels
                    sum_altura = sum_altura + (comp.bottom - comp.top)
                    sum_largura = sum_largura + (comp.right - comp.left)

                #testaTamComponente(dictionary, comp)
                label = label + 1
    

    mediaPixels = sum_pixels/len(dictionary)
    mediaLargura = sum_largura/len(dictionary)
    mediaAltura = sum_altura/len(dictionary)
    testaComponentes(dictionary, mediaPixels, mediaLargura, mediaAltura)
    return dictionary


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

    return img_out



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


    # muda a imagem
    img_out = changeImage(img, img_out)
    cv2.imwrite ('./resultados/out.png', img_out*255)

    # rotula a imagem
    components = rotula(img_out)

    # conta número de grãos de arroz
    n_components = len(components)
    n_arroz = 0
    for i in range(0, n_components):
        n_arroz = n_arroz + components[i].n_arroz

    print("Número de grãos de arroz: " + str(n_arroz))



if __name__ == '__main__':
    main ()