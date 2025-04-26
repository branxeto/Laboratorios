%<---- Valores previos ---->
RollOff = [0, 0.25, 0.75, 1]; % Este valor es variable para [0-0.25-0.75-1]

%<---- Laboratorio ----->
N_bits = 20000; %Numero de bits
bits = randi([0 1], 1, N_bits); %Randomizar entre 0 y 1
bits = 2*bits - 1; %Hacer que los valores vayan entre -1 y 1

mps = 8; %Muestras por cada espacio de los bits para suavizar la señal
bits_upsample = upsample(bits, mps); %Funcion para agregar los espacios entre cada bit
Ruido = 20; %Relacion señal a ruido en dB, mientras mayor la relación, mejor la limpieza de la señal
span = 10;

for j = 1:length(RollOff)
    alpha = RollOff(j);
    H = rcosdesign(alpha, span, mps, 'normal');
    
    t_senal = conv(bits_upsample, H, 'same'); %Señal para transformar upsample de 0 y 1 en una señal que represente H, 'same' es para hacer que tenga el mismo tamaño que upsample
    r_senal = awgn(t_senal, Ruido, 'measured'); %Función para generar ruido
    eyediagram(r_senal, 2*mps);
end