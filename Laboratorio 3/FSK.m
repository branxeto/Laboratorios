
clear all; close all; clc;

Data = randi([0 1], 1, 10);
time = 0:9;
y = [];
j = 0;
for i = 1:2:length(Data)
    j=j+1;
    if Data(i) == 0 && Data(i+1) == 0
        y(j) = 0;
    else if Data(i) == 0 && Data(i+1) == 1
            y(j) = 1;
        else if Data(i) == 1 && Data(i+1) == 1
                y(j) = 2;
            else if Data(i) == 1 && Data(i+1) == 0
                    y(j) = 3;
                end
            end
        end
    end
end


stairs(time,Data), axis([0 9 -2 2]), xlabel('Time (s)'), ylabel('Amplitude'), title(['Input Data ', num2str(Data)]), grid on;

t = 0:0.01:5-0.01;
T = 0:0.01:0.99;
f1 = sin(2 * pi * T);
f2 = sin(8 * pi * T);
f3 = sin(16 * pi * T);
f4 = sin(32 * pi * T);

for a = 1:length(y)
    if y(a) == 0
        signal(a * 100 - 99: a * 100) = f1;
    else if y(a) == 1
            signal(a * 100 - 99: a * 100) = f2;
        else if y(a) == 2
                signal(a * 100 - 99: a * 100) = f3;
            else if y(a) == 3
                    signal(a * 100 - 99: a * 100) = f4;
                end
            end
        end
    end
end

figure;
fs_FSK = 100; % Adjust the sampling frequency accordingly
frequencies_FSK = linspace(-fs_FSK/2, fs_FSK/2, length(signal));
G_FSK = fft(signal);
plot(frequencies_FSK, abs(fftshift(G_FSK))), xlabel('Frequency (Hz)'), ylabel('Magnitude'), title('Fourier Transform of FSK Signal'), grid on;
