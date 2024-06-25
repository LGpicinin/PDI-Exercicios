import cv2
import numpy as np
import random

def detect_edges(image):

    area = image.shape[0]*image.shape[1]

    min = 10
    max = 100

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 1)
    edges = cv2.Canny(blur, min, min*3, apertureSize=3)

    # calcula bordas até que menos de 0.01% da imagem esteja setada
    while np.sum(edges)/255 > area*0.03:
        if min + 1 != 80:
            min = min + 1
            max = max + 1
        else:
            break
        edges = cv2.Canny(blur, min, min*3, apertureSize=3)
    return edges

def detect_lines(edges, min_points):
    lines = cv2.HoughLines(edges, 1, np.pi / 180, min_points)
    # faça um assert para garantir que tenha mais de 2 linhas e manda msg se não tiver
    assert lines is not None, "Não foi possível detectar linhas na imagem"
    return lines

def compute_intersection(line1, line2):
    rho1, theta1 = line1[0]
    rho2, theta2 = line2[0]

    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])

    b = np.array([[rho1], [rho2]])

    det_A = np.linalg.det(A)
    if det_A != 0:
        intersection = np.linalg.solve(A, b)
        return intersection
    else:
        return None

def distance_point_to_line(point, equation_line):
    rho, theta = equation_line[0]
    x0, y0 = point

    a = np.cos(theta)
    b = np.sin(theta)

    return np.abs(a * x0 + b * y0 - rho) / np.sqrt(a**2 + b**2)



def ransac_vanishing_point(lines, num_iterations, threshold , width , restrictAreaFunc = None, restrict = False):

    best_left = [[0], [0]]
    left_count = 0

    best_right = [[0], [0]]
    right_count = 0

    best_intersection = None
    best_count = 0

    for _ in range(num_iterations):

        line1, line2 = random.sample(list(lines), 2)

        intersection = compute_intersection(line1, line2)

        if intersection is None:
            continue

        count = 0
        for line in lines:
            if distance_point_to_line(intersection, line) < threshold:
                count += 1

        if count > best_count:
            best_count = count
            best_intersection = intersection

        # se ponto estiver fora da imagem para à direita
        if restrictRight(intersection, width) == True and count > right_count:
            right_count = count
            best_right = intersection
        
        # se ponto estiver fora da imagem para à esquerda
        elif restrictLeft(intersection) == True and count > left_count:
            left_count = count
            best_left = intersection

    # se tiver algum ponto nos extremos
    if left_count!=0 or right_count!=0:

        # se contagem esquerda maior que direita
        if left_count > right_count:
            # se 2 vezes contagem esquerda for maior que contagem principal, então a imagem tem dois pontos de fuga
            if left_count*2 > best_count:
                # deixo os pontos extremos espelhados
                best_right = [[width+abs(best_left[0][0])], [best_left[1][0]]]
                return [best_left, best_right]
            
        # caso contrário
        else:
            # se 2 vezes contagem direita for maior que contagem principal, então a imagem tem dois pontos de fuga
            if right_count*2 > best_count:
                # deixo os pontos extremos espelhados
                best_left = [[(best_right[0][0] - width)], [best_right[1][0]]]
                return [best_left, best_right]
    
    assert best_intersection is not None, "Não foi possível encontrar o ponto de fuga"
    return [best_intersection]

#restrição para a direita
def restrictRight(intersection, width):
    if intersection[0] > width :
        return True
    return False

# restringe para a esquerda
def restrictLeft(intersection):
    if intersection[0] < 0:
        return True
    return False

# restringe para cima
def restrictTop(intersection, height):
    if intersection[1] < height//2:
        return True
    return False

#restringe para baixo
def restrictBottom(intersection, height):
    if intersection[1] > height//2:
        return True
    return False

# desenha linhas
def draw_lines(lines, image):
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 1)


def vanishing_point(filePath):
    # Carregar imagem
    imagelines = cv2.imread("images/" +  filePath)
    image = imagelines.copy()
    
    # Detectar bordas
    edges = detect_edges(image)
    cv2.imwrite('resultados2/image_edges_'+ filePath , edges)

    # Detectar linhas
    lines = detect_lines(edges, 100)

    #Desenha as linhas na imagem
    draw_lines(lines, imagelines)
    cv2.imwrite('resultados2/image_lines_'+ filePath , imagelines) 
    
    # Definir parâmetros do RANSAC
    num_iterations = 750
    threshold = 50
    
    # Encontrar ponto de fuga
    print("Calculando ponto de fuga da " + filePath)
    vanish_points = ransac_vanishing_point(lines, num_iterations, threshold , image.shape[0] )


    vanish_point1 = vanish_points[0]

    # se tiver 2 pontos de fuga
    if len(vanish_points) != 1:

        vanish_point2 = vanish_points[1]

        # faz borda suficiente para caber os dois pontos
        imageBorda = cv2.copyMakeBorder(image, 0, 0, (int(abs(vanish_point1[0][0]))), (int(abs(vanish_point1[0][0]))), cv2.BORDER_CONSTANT, value=[255, 255, 255])

        # desenha pontos
        cv2.circle(imageBorda, (0, int(vanish_point1[1][0])), 10, (0, 255, 0), -1)
        cv2.circle(imageBorda, (imageBorda.shape[1]-1, int(vanish_point2[1][0])), 10, (0, 255, 0), -1)

        cv2.imwrite('resultados2/image_borda_pontos' + filePath , imageBorda)

        # gera imagem preta
        perspective_image = np.zeros((imageBorda.shape[0], imageBorda.shape[1]), np.uint8)

        # coloca dois pixels brancos (pontos de fuga)
        perspective_image[int(vanish_point1[1][0])][0] = 255
        perspective_image[int(vanish_point2[1][0])][perspective_image.shape[1]-1] = 255

        lines = detect_lines(perspective_image, 0)

        draw_lines(lines, imageBorda)

        cv2.imwrite('resultados2/perspective_image_'+ filePath , imageBorda)
        

    # se tiver 1 ponto de fuga
    else:
        # desenha ponto
        cv2.circle(image, (int(vanish_point1[0][0]), int(vanish_point1[1][0])), 10, (0, 0, 255), -1)

        cv2.imwrite('resultados2/image_borda_pontos' + filePath , image)

        # gera imagem preta
        perspective_image = np.zeros((image.shape[0], image.shape[1]), np.uint8)

        # coloca um pixel branco (ponto de fuga)
        perspective_image[int(vanish_point1[1][0])][int(vanish_point1[0][0])] = 255

        lines = detect_lines(perspective_image, 0)

        draw_lines(lines, image)

        cv2.imwrite('resultados2/perspective_image_'+ filePath , image) 




def main ():

    images = ["image1.jpeg", "image2.jpeg", "image3.jpeg", "image4.jpg", "image6.jpg", "image7.jpg", "image8.jpg", "image9.jpeg"]

    for(image) in images:
        vanishing_point(image)
    

if __name__ == '__main__':

    main()