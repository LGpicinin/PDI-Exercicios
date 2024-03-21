#===============================================================================
# Exemplo: segmentação de uma imagem em escala de cinza.
#-------------------------------------------------------------------------------
# Autor: Bogdan T. Nassu
# Universidade Tecnológica Federal do Paraná
#===============================================================================

import sys
import timeit
import numpy as np
import cv2

#===============================================================================

INPUT_IMAGE =  'arroz.bmp'

# TODO: ajuste estes parâmetros!
NEGATIVO = False
THRESHOLD = 0.8
ALTURA_MIN = 1
LARGURA_MIN = 1
N_PIXELS_MIN = 400

#===============================================================================

class Component:
    def __init__(self, label, n_pixels, t, l, b, r) -> None:
        self.label = label
        self.n_pixels = n_pixels
        self.top = t
        self.left = l
        self.bottom = b
        self.right = r



def binariza (img, threshold):

    rows, cols, channel = img.shape
    
    for row in range (rows):
        for col in range (cols):
            if img[row, col, 0] > threshold:
                img[row, col, 0] = 1
            else:
                img[row, col, 0] = 0

    return img


    # TODO: escreva o código desta função.
    # Dica/desafio: usando a função np.where, dá para fazer a binarização muito
    # rapidamente, e com apenas uma linha de código!

#-------------------------------------------------------------------------------

def inunda (img, row, col, comp: Component, lenCol, lenRow):
    if row < 0 | row > lenRow | col < 0 | col > lenCol:
        return
    
    img[row, col, 0] = comp.label
    comp.n_pixels = comp.n_pixels + 1

    if row > comp.bottom:
        comp.bottom = row
    elif row < comp.top:
        comp.top = row
    
    if col < comp.left:
        comp.left = col
    elif col > comp.right:
        comp.right = col

    if img[row+1, col, 0] == 1:
        inunda(img, row+1, col, comp, lenCol, lenRow)
    if img[row, col+1, 0] == 1:
        inunda(img, row, col+1, comp, lenCol, lenRow)
    if img[row-1, col, 0] == 1:
        inunda(img, row-1, col, comp, lenCol, lenRow)
    if img[row, col-1, 0] == 1:
        inunda(img, row, col-1, comp, lenCol, lenRow)

def rotula (img, n_pixels_min):

    rows, cols, channels = img.shape
    label = 2
    count = 0
    dictionary = []

    for row in range (rows):
        for col in range (cols):
            if img[row, col, 0] == 1:
                comp = Component(label, count, row, col, row, col)
                inunda(img, row, col, comp, rows, cols)
                if(comp.n_pixels > n_pixels_min):
                    dictionary.append(comp)
                    label = label + 1
    
    return dictionary

    # TODO: escreva esta função.
    # Use a abordagem com flood fill recursivo.

#===============================================================================

def main ():

    # Abre a imagem em escala de cinza.
    img = cv2.imread (INPUT_IMAGE, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    # É uma boa prática manter o shape com 3 valores, independente da imagem ser
    # colorida ou não. Também já convertemos para float32.
    img = img.reshape ((img.shape [0], img.shape [1], 1))
    img = img.astype (np.float32) / 255

    # Mantém uma cópia colorida para desenhar a saída.
    img_out = cv2.cvtColor (img, cv2.COLOR_GRAY2BGR)

    # Segmenta a imagem.
    if NEGATIVO:
        img = 1 - img
    img = binariza (img, THRESHOLD)
    cv2.imshow ('01 - binarizada', img)
    cv2.imwrite ('01 - binarizada.png', img*255)

    start_time = timeit.default_timer ()
    componentes = rotula (img, N_PIXELS_MIN)
    n_componentes = len (componentes)
    print ('Tempo: %f' % (timeit.default_timer () - start_time))
    print ('%d componentes detectados.' % n_componentes)

    # Mostra os objetos encontrados.
    for c in componentes:
        cv2.rectangle (img_out, (c.left, c.top), (c.right, c.bottom), (0,0,1))

    cv2.imshow ('02 - out', img_out)
    cv2.imwrite ('02 - out.png', img_out*255)
    cv2.waitKey ()
    cv2.destroyAllWindows ()


if __name__ == '__main__':
    main ()

#===============================================================================
