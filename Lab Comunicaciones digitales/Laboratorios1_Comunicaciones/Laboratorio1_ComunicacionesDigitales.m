%parametros claves
f = 1000; %Frecuencia de la señal
fs = 200000; %frecuencia de muestreo
ts = 1/fs;%Periodo de muestreo
ls = 200; %cantidad de muestras

%Punto uno: Señal sinusoidal
a = 1; %Amplitud de la señal
t = (0:ls-1)*ts;%Vector tiempo
sinusoidal = a * sin(2*pi*f*t); %Señal sinusoidal

%Punto dos: Modulación por amplitud de pulso (PAM) con muestreo natural.
tau = 0.3*ts; %Duración del pulso
d = (tau/ts)*100; %Ciclo de trabajo
tren_pulso = (square(2*pi*f*10*t,d) + 1)/2;
pam_natural = tren_pulso .* sinusoidal;

%vector = inicio:espacio de cada muestra:final

%Punto tres: Modulación por amplitud de pulso (PAM) con muestreo 
% instantaneo
pam_instantaneo = zeros(size(t));
valores = 0;
for i = 1:length(t)
    if tren_pulso(i) == 1
        if valores == 0
            valores = sinusoidal(i);
        end
        pam_instantaneo(i) = valores;
    else 
        valores = 0;
        pam_instantaneo(i) = 0;
    end
end

%<----Laboratorio---->

%Punto uno
F_sinusoidal = fft(sinusoidal);
F_pam_natural = fft(pam_natural);
F_pam_instantaneo = fft(pam_instantaneo);
vector_f = (0:length(F_sinusoidal)-1);

%Punto dos
N = 5; %Numero de bits para PCM
L = 2^N; %Numero de niveles
Nmax = 4; %Numero de bits de palabra
Nmin = -Nmax;
del = (Nmax-Nmin)/L;
part = Nmin:del:Nmax; %Valores que tomara la cuantificacion PCM
code = Nmin-(del/2):del:Nmax+(del/2); %Conteo de los valores cuantificables
[ind,q] = quantiz(sinusoidal,part,code);
l1 = length(ind);
l2 = length(q);
err = pam_instantaneo - q;

for i = 1:l1
    if (ind(1)~=0)
        ind(i) = ind(i);
    end
    i=i+1;
end

for i=1:l2
    if (q(i)==Nmin-(del/2))
        q(i)=Nmin+(del/2);
    end
end


%Graficos
figure;
hold on;
    %Punto tres
    subplot(3,1,1)
    plot(vector_f,abs(F_sinusoidal));
    hold on;
    xlabel('Frequency (Hz)');
    ylabel('Magnitude');
    title('Transformada de furier de señal original');
    grid on;

    subplot(3,1,2)
    plot(abs(F_pam_natural));
    xlabel('Frequency (Hz)');
    ylabel('Magnitude');
    title('Transformada de furier de PAM natural');
    grid on;

    subplot(3,1,3)
    plot(abs(F_sinusoidal));
    xlabel('Frequency (Hz)');
    ylabel('Magnitude');
    title('Transformada de furier de PAM instantaneo');
    grid on;

%Graficos
figure;
hold on;

    subplot(4,1,1)
    plot(t,sinusoidal)
    grid on;
    xlabel('tiempo');
    ylabel('Amplitud');
    title('Señal original');

    subplot(4,1,2)
    plot(t, pam_instantaneo)
    grid on;
    xlabel('tiempo');
    ylabel('Amplitud');
    title('Señal PAM instantaneo');

    subplot(4,1,3)
    stem(q);
    grid on;
    xlabel('tiempo');
    ylabel('Amplitud');
    title('Señal cuantizada');
   
    subplot(4,1,4)
    plot(t, err);
    grid on;
    xlabel('tiempo');
    ylabel('Amplitud');
    title('Error de cuantizacion');

