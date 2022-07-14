import matplotlib
matplotlib.use('Agg')

import numpy as np
import cv2
import matplotlib.pyplot as plt
import numpy as np
import control as ctl
import control.matlab as ml
import matplotlib.pyplot as plt

##plot_margins отрисовывает ЛАФЧХ и переходный процесс по заданным T1,T2,T3 
def plot_margins(T1,T2,T3):
    K=2550000   #               K=1600000
    D=50        # По оси рамы   D=50        # По оси платформы
    J=676.23    #               J=190.68
    T0=J/D
    # Составление передаточных функций звеньев структурной схемы
    W1=ml.tf(np.array([K/D]),np.array([1,0]))*ml.tf(np.array([1]),np.array([T0,1]))
    W2=ml.tf(np.array([T1,1]),np.array([T2,1]))
    W3=ml.tf(np.array([1]),np.array([T3,1]))
    # составление разомкнутой и замкнутой системы
    sys=W1*W2*W3
    sys_stp=ml.feedback(W1,W2*W3)
    # составление списка частот
    start=-2
    stop=5
    f=np.logspace(start,stop,100)
    # Получение списка амплитуд фаз и часост соответствующих амплитудам и фазам
    mag,phase,omega = ctl.bode(sys,f,dB=True,plot=False,Hz=True)
    # Получение списка амплитуд и моментов времени, соответствующих этим амплитудам 
    y,x=ml.step(sys_stp)
    # Приведение частоты, амплитуды и фазы к требуемым единицам измерения
    omega=omega/(2*np.pi)
    magdB = 20*np.log10(mag)
    phase_deg = phase*180.0/np.pi
    # получение запасов устойчивости по амплитуде и фазе
    # а также частоты среза и частоты пересечения фазы значения -180deg 
    Gm,Pm,Wcg,Wcp = ml.margin(sys)
    # Приведение частоты и амплитуды к требуемым единицам измерения
    GmdB = 20*np.log10(Gm)
    Wcp=Wcp/(2*np.pi)
    Wcg=Wcg/(2*np.pi)


    ## Построение ЛАФЧХ и переходного процесса по расчитанным величинам
    fig,(ax1,ax2,ax3) = plt.subplots(3,1, clear=True)
    fig.set_size_inches(15, 8)
    # Построение переходного процесса
    ax3.plot(x,y,linewidth=5)
    ax3.plot(x,[1+0.03 for _ in x],'k--',linewidth=1)
    ax3.plot(x,[1-0.03 for _ in x],'k--',linewidth=1)
    # Построение амплитудной характеристики
    ax1.semilogx(omega,magdB)
    ax1.grid(True,which="both",linestyle='--')
    ax1.set_xlabel('Частота, Гц')
    ax1.set_ylabel('Амплитуда, дБ')
    # Построение фазовой характеристики 
    ax2.semilogx(omega,phase_deg)
    ax2.grid(True,which="both",linestyle='--')
    ax2.set_xlabel('Частота, Гц')
    ax2.set_ylabel('Фаза, град.')
    ax3.grid(True,which="both")
    ax3.set_xlabel('Время, с')
    ax3.set_ylabel('Угол, угл. мин.')
    # Добавление ключевых параметров на графики
    ax1.set_title('Зап Амп = '+str(np.round(GmdB,2))+' dB      '+
                  'Зап фаз = '+str(np.round(Pm,2))+'deg      '+
                  'Част. среза = '+str(np.round(Wcp,2))+' Гц      '+
                  'Перерег. = '+str(np.round((np.max(y)-1),2))+ ' '+
                  'T0,T1,T2,T3 ='+''.join(str(x)+', ' for x in [T0,T1,T2,T3]))
    # Построение линии нуля dB
    ax1.plot(omega,0*omega,'k--',linewidth=1)
    # Построение линии -180 deg
    ax2.plot(omega,-180+0*omega,'k--',linewidth=1)
    # Построение вертикальной линии, соответствующей пересечению ФЧХ -180 deg
    # с пометкой запаса устойчивости по амплитуде
    ax2.plot([Wcg,Wcg],[-180,0],'k--',linewidth=1)
    ax1.plot([Wcg,Wcg],[np.min(magdB),0-GmdB],'k--',linewidth=1)
    ax1.plot([Wcg,Wcg],[0,0-GmdB],'r--',linewidth=2)
    # Построение вертикальной линии соответствующей частоте среза
    ax1.plot([Wcp,Wcp],[np.min(magdB),0],'k--',linewidth=1)
    ax2.plot([Wcp,Wcp],[-180+Pm,0],'k--',linewidth=1)
    ax2.plot([Wcp,Wcp],[-180,-180+Pm],'g--',linewidth=2)
    # Построение вертикальных линий соответствующих постоянным времени T0,T1,T2,T3
    for T in [T0,T1,T2,T3]:
        if T!=0:
           ax1.plot([1/T/(2*np.pi),1/T/(2*np.pi)],[np.min(magdB),np.max(magdB)],'b--',linewidth=1)
           ax2.plot([1/T/(2*np.pi),1/T/(2*np.pi)],[-250,0],'b--',linewidth=1)

    # Добавление фигур в img cv
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.cla()
    plt.clf()
    plt.close('all')
    del fig
    # img is rgb, convert to opencv's default bgr
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    return img

def nothing(x):
    pass

def main():

    # Создание окна и ползунков для постоянных времени
    cv2.namedWindow('plot')
    cv2.createTrackbar('T1','plot',781,10000,nothing)#/100000
    cv2.createTrackbar('T2','plot',60,1000,nothing)#/100000
    cv2.createTrackbar('T3','plot',80,100000,nothing)#/1000000

    while 1:
        # Запись постоянных времени с ползунков в соответствующие переменные
        T1,T2,T3=(cv2.getTrackbarPos('T1','plot')/100000,
                    cv2.getTrackbarPos('T2','plot')/100000,cv2.getTrackbarPos('T3','plot')/10000000)
        # Получение изображения с ЛАФЧХ и ПП
        img=plot_margins(T1,T2,T3)
        # Вывод ЛАФЧХ и ПП в окно
        cv2.imshow("plot",img)

        # выход по клавише esc
        k = cv2.waitKey(33) & 0xFF
        if k == 27:
            break

if __name__ == '__main__':
    main()

