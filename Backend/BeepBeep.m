function bools = BeepBeep(file_1, file_2, chirp)
    rate = 48000; % sampling rate

    % A chirp signal of 1 second 
    % with a freq range of [1, 18]kHz 
    x = audioread(chirp);

    groundTruth = 25; % cm

    % Load data received by two different devices
    y = struct();
    disp(file_1)
    disp(file_2)
    y(1).raw = audioread(file_1);
    y(2).raw = audioread(file_2);
    for i = 1:2
        y(i).xcorr = conv(flipud(x), y(i).raw(:));
    end

    for i = 1:2
        [vals, locs] = findpeaks(abs(y(i).xcorr), ...
            'MinPeakDistance', length(x));
        [~, idx] = sort(vals, 'descend');
        
        y(i).etoa = locs(idx(1:2)) ./ rate;
        y(i).etoa = sort(y(i).etoa);
    end

    y(2).etoa = y(2).etoa + 10;

    c = 34000; % cm/s
    dAA = 3.5; % Spk-to-mic distance in devA
    dBB = 3.5; % Spk-to-mic distance in devB

    % c * (tB1 - tA1) + c * (tA3 - tB3) + (dAA + dBB)
    
    distance = c * (y(2).etoa(1) - y(1).etoa(1)) ...
        + c * (y(1).etoa(2) - y(2).etoa(2)) ...
        + (dAA + dBB);
    distance = distance / 2;

    bools =  num2str(distance);
end
