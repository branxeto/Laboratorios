RollOff = [0, 0.25, 0.75, 1]; % Este valor es variable para [0-0.25-0.75-1]
Fo = 6; %Ancho de banda

% <----- ACTIVIDAD PREVIA ----->
figure; %Iniciar grafico

    subplot(2,1,1);
    title('Respuesta en frecuencia Coseno alzado');
    xlabel('Frecuencia (f)');
    ylabel('Amplitud');
    hold on;
    grid on;
    
    subplot(2,1,2);
    title('Respuesta al impulso');
    xlabel('Tiempo');
    ylabel('Amplitud');
    hold on;
    grid on;

for j = 1:length(RollOff)

    alpha = RollOff(j);
    F_delta = alpha * Fo;
    F1 = Fo - F_delta;
    B = F_delta + Fo;%Ancho de banda absoluto
    F = 2*B; %Frecuencia
    T = -F:0.01:F; %Vector frecuencias
    N = length(T); %Numero de puntos con respecto a las frecuencias
    H = zeros(1, length(T));
    for i = 1:length(T) %Sumatoria para Filtro de coseno alzado
        F_abs = abs(T(i));
        if F_abs <= F1 % |f| < f1
            H(i) = 1;
        elseif (F1 < F_abs) && (F_abs <= B) % f1 < |f| < B
            H(i) = 0.5*(1 + cos((pi*(F_abs-F1))/(2*F_delta)));
        elseif F_abs > B % |f| > B
            H(i) = 0;
        end
    end

    t = linspace(-N/2,N/2, N)*(1/F); %Creación de vector tiempo con relación a la frecuencia y transformandolo en tiempo con el periodo de la frecuencia
    %t = t(t >= 0); % Mostrar solo valores positivos de vector tiempo
    H_time = ifft(ifftshift(H)); % Trasnformada inversa de funcion H
    H_time = H_time(end - length(t) + 1: end); % Definimos solo los valores positivos

    subplot(2,1,1);
    plot(T,H);
    subplot(2,1,2);
    plot(t,H_time);
    
end

