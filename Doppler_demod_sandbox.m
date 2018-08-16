%Create a simulated output of red-shifted and blue-shifted frequency trains for a CRES experiment.

rng default           % random number generator

f_c = 1.0e8;         % BASEBAND (post-downmixing) cyclotron frequency (Hz)
f_a = 0.9e8;          % axial oscillation frequency (Hz)
mod_ind = 1.0;        % modulation index
SNR = 1.00;           % simulated average signal-to-noise power ratio
A_r = 1.0;            % red-shifted signal amplitude
A_b = 1.0;            % blue-shifted signal amplitude
phi_r = 0.5;          % red-shifted initial phase
phi_b = 0.5;          % blue-shifted initial phase
Fs = 4E9;             % sample frequency, Hz
T = 1.0E-06;          % total time, seconds 

t = 0:1/Fs:T-1/Fs;    % time array from 0 to T in increments of 1/Fs
noise = randn(size(t));
S_r = A_r * (SNR)^0.5 * sin(6.28*f_c*t - mod_ind*sin(6.28*f_a*t) + phi_r) + noise;
noise = randn(size(t));
S_b = A_b * (SNR)^0.5 * sin(6.28*f_c*t + mod_ind*sin(6.28*f_a*t) + phi_b) + noise;

N = Fs*T;              % total # of samples
for k=1:N
  Prod(k) = S_r(k) * S_b(k);
end

red_dft = fft(S_r);    %take the discrete-time Fourier transform of the red-shifted channel
red_dft = red_dft(1:N/2+1);
psd_red = (1/(Fs*N)) * abs(red_dft).^2;
psd_red(2:end-1) = 2*psd_red(2:end-1);

prod_dft = fft(Prod);  %take the discrete-time Fourier transform of the product
prod_dft = prod_dft(1:N/2+1);
psd_prod = (1/(Fs*N)) * abs(prod_dft).^2;
psd_prod(2:end-1) = 2*psd_prod(2:end-1);

freq = 0:Fs/N:Fs/2;
figure
%plot(freq,10*log10(psd_red), 'Color','red')
plot(freq,10*log10(psd_prod), 'Color','blue')
grid on
fontSize = 36;
title('125 MHz carrier, mod. index=1.0, SNR=1.0','FontSize',24)
xlabel('Frequency (Hz)','FontSize',24)
ylabel('Power/Frequency (dB/Hz)','FontSize',24)
