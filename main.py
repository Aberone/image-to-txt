import skimage.io as sk
import matplotlib as mpl


def split(a, b):
    # Возвраает равномерный вектор из целых чисел, ближайших к a / b, сумма элементов которого равна a
    # a :-> b = b*Q + R*1
    # a :-> b = (b - R)*Q + R*Q + R*1
    # a :-> b = (b - R)*Q + R*(Q + 1)
    # (b - R) раз по Q;  R раз по Q + 1
    if a >= b:
        Q = a // b
        R = a % b
        if R == 0:
            return (Q,) * b
        else:
            if (b - R) > R:
                filler_times = b - R
                filler_amt = Q
                insertor_times = R
                insertor_amt = Q + 1
            else:
                filler_times = R
                filler_amt = Q + 1
                insertor_times = b - R
                insertor_amt = Q
            resultat = [filler_amt] * filler_times
            delta = filler_times / insertor_times
            cnt = 0
            for i in range(insertor_times):
                resultat.insert(round(cnt), insertor_amt)
                cnt += delta
            return tuple(resultat)
    else:
        return 'Error: extension is not avaliable'


opt = open('output.txt', 'w', encoding='utf-8')
print('Введите название файла с изображением (файл должен находиться в рабочей папке на одном уровне с main.py):')
name = input()
img = sk.imread(name)
# img_wh --> ширина и высота картинки, px
img_width = img.shape[1]
img_height = img.shape[0]
print('Введите количество символов, которое выходной файл должен занимать в ширину (целое число), и отношение ширины к высоте (два целых числа):')
# wh_celling --> ширина и высота картинки, sym
width_celling, coeff_height, coeff_width = map(int, input().split())
height_celling = int(width_celling * (img_height / img_width) * (coeff_width / coeff_height))
# sym_wh[n] --> ширина и высота символа на n-ной позиции, n ∈ [0; wh_celling), px/sym
sym_width = split(img_width, width_celling)
sym_height = split(img_height, height_celling)
# matrix[h][w] --> средняя интенсивность пикселей в блоке h:w
matrix = [[-1 for j in range(width_celling)] for i in range(height_celling)]
# frequency[интенсивность цвета] --> число пикселей с такой интенсивностью, шт.
frequency = [0] * 256
# result --> заданная картинка в текстовом представлении
result = ''

# hwn - порядковый номер обрабатываемого блока, hw_corner - координата его левого верхнего пикселя
hn = 0
h_corner = 0
# Внешний цикл: обработка hn:wn-ного блока с шагами в sym_hw соответственно
while h_corner <= img_height and hn < len(sym_height):
    wn = 0
    w_corner = 0
    while w_corner <= img_width and wn < len(sym_width):
        # Внутренний цикл: обработка блока, проецируемого в один символ
        # плюс сбор статистики о частотном распределении интенсивностей в блоках и на картинке в целом
        block_ints_sum = 0
        for h_pix in range(h_corner, h_corner + sym_height[hn]):
            for w_pix in range(w_corner, w_corner + sym_width[wn]):
                # Частотный анализ картинки в целом
                intensity = (int(img[h_pix, w_pix, 0]) + int(img[h_pix, w_pix, 1]) + int(img[h_pix, w_pix, 2])) // 3
                frequency[intensity] += 1
                # Частотный анализ конкретного блока
                block_ints_sum += intensity
        matrix[hn][wn] = block_ints_sum // (sym_height[hn] * sym_width[wn])
        w_corner += sym_width[wn]
        wn += 1
    h_corner += sym_height[hn]
    hn += 1

# Определение границ перехода между четырьмя оттенками
mark1 = -1
mark2 = -1
mark3 = -1
up_sum = 0
freq_sum = img_width * img_height
for i in range(256):
    up_sum += frequency[i]
    if mark1 == -1 and up_sum >= freq_sum // 4:
        mark1 = i
    elif mark2 == -1 and up_sum >= freq_sum // 2:
        mark2 = i
    elif mark3 == -1 and up_sum >= 3 * freq_sum // 4:
        mark3 = i
        break

# Преобразование значений matrix в символы в соответствии с границами перехода:
for h_idx in range(height_celling):
    for w_idx in range(width_celling):
        if 0 <= matrix[h_idx][w_idx] < mark1:
            result += '█'
        elif mark1 <= matrix[h_idx][w_idx] < mark2:
            result += '▓'
        elif mark2 <= matrix[h_idx][w_idx] < mark3:
            result += '▒'
        else:
            result += '░'
    result += '\n'

opt.write(result)
opt.close()
