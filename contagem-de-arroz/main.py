import numpy as np
import cv2
import sys

IMG_60 = './imagens/60.bmp'
IMG_82 = './imagens/82.bmp'
IMG_114 = './imagens/114.bmp'
IMG_150 = './imagens/150.bmp'
IMG_205 = './imagens/205.bmp'

N_PIXELS_MIN = 50
N_PIXELS_MAX = 250

class Component:
    def __init__(self, label, n_pixels, n_arroz) -> None:
        self.label = label
        self.n_pixels = n_pixels
        self.n_arroz = n_arroz


def testaComponentes (dictionary, media):
    min = media - media*0.5
    max = media + media*0.4
    print("\nmedia = " + str(media))
    print("\nmin = " + str(min))
    print("\nmax = " + str(max))

    for i in range(0, len(dictionary)):
        comp = dictionary[i]
        print(str(comp.n_pixels))

            #dictionary.append(comp)
        comp.n_arroz = 1
        count = max
        while comp.n_pixels > count:
            count = count + max
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
    num_comp = 0
    sum_pixels = 0

    for row in range (rows):
        for col in range (cols):
            #print(str(img[row, col]))
            if img[row, col] == 1:
                num_comp = num_comp+1
                comp = Component(label, 0, 0)
                inunda(img, row, col, comp, cols, rows)

                sum_pixels = sum_pixels + comp.n_pixels
                if comp.n_pixels >= N_PIXELS_MIN:
                    dictionary.append(comp)

                #testaTamComponente(dictionary, comp)
                label = label + 1
    
    media = sum_pixels/len(dictionary)
    testaComponentes(dictionary, media)
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