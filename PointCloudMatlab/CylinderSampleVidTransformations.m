%% Load and Normalize Point Cloud

clear; clc;

HEIGHT = 30;
WIDTH = 48;
RLIM = WIDTH/2 - 0.5;
UPR = 360;
DPU = 360/UPR;
RPU = deg2rad(DPU);
FRAMERATE = 15000;
size_perc = 0.6;

NEXT_FRAME = uint8(0xFF);
NEXT_SLICE = uint8(0xFE);

filename = 'pagoda';
% file = "Poisson Disk Samples";
rawcloud = pcread(['plys/', filename, '.ply']);

% load('xyzPoints');
% rawcloud = pointCloud(xyzPoints);

rawXYZ = rawcloud.Location;
% T = [1,0,0;0,cosd(90),-sind(90);0,sind(90),cosd(90)];
% rawXYZ = rawXYZ * T';
rawXYZ(:,[1,2]) = rawXYZ(:,[1,2]) - [mean(rawcloud.XLimits), mean(rawcloud.YLimits)];
rawXYZ(:,3) = rawXYZ(:,3) - rawcloud.ZLimits(1);
diffs = [norm(max(rawXYZ(:,[1,2])) - min(rawXYZ(:,[1,2]))), max(rawXYZ(:,3))];
rawXYZ = rawXYZ * size_perc*min([WIDTH, HEIGHT] ./ diffs);
rawCol = single(rawcloud.Color) / 255;

%% Set Keyframes

rawXYZ = [rawXYZ,ones(size(rawXYZ,1),1)];

keyframes = {};
keyframes{end+1} = htmgen(0,0,0,[0,0,0]);
keyframes{end+1} = htmgen(0,0,24,[0,0,0]);
keyframes{end+1} = htmgen(0,0,24,[0,0,0]);
keyframes{end+1} = htmgen(0,0,24,[0,0,0]);
keyframes{end+1} = htmgen(0,0,0,[0,0,2]);
keyframes{end+1} = htmgen(0,0,0,[0,0,2]);
keyframes{end+1} = htmgen(0,0,0,[0,0,2]);
keyframes{end+1} = htmgen(24,0,0,[0,0,0]);
keyframes{end+1} = htmgen(24,0,0,[0,0,0]);
keyframes{end+1} = htmgen(24,0,0,[0,0,0]);
keyframes{end+1} = htmgen(0,24,0,[0,0,0]);
keyframes{end+1} = htmgen(0,24,0,[0,0,0]);
keyframes{end+1} = htmgen(0,24,0,[0,0,0]);

file = fopen(['video_bins/', filename, '.vox'], 'w');
fwrite(file, uint16(UPR), 'uint16');
fwrite(file, uint16(FRAMERATE), 'uint16');

%% LOOP

framewait = waitbar(0, '', 'Name', 'Frames');
wait = waitbar(0, '', 'Name', 'Sweeping through angles');
prevenpoints = {};

for k = 1:length(keyframes)
    fwrite(file, uint8(NEXT_FRAME), 'uint8');
    waitbar(k/length(keyframes), framewait, sprintf('Current Frame: %d/%d',k,length(keyframes)));
    
    bytecolzero = uint8([0,0,0]);
    for prevenindex = 1:length(prevenpoints) 
        fwrite(file, uint8(HEIGHT - z - 1), 'uint8');
        fwrite(file, uint8(r + 23.5), 'uint8');
        fwrite(file, uint8(bytecolzero), 'uint8');
    end
    
    %% Visualize cloud
%     rawXYZ = rawXYZ * keyframes{k}';
    rawXYZ = applyTransformation(rawXYZ, keyframes{k});

    cloud = pointCloud(rawXYZ(:,1:3), 'Color', rawCol, 'Intensity', rawcloud.Intensity);

    figure(1);
    pcshow(cloud);
    set(gcf,'color','k'); set(gcf, 'InvertHardCopy', 'off');
    saveas(gcf, sprintf("out/%05d-cylindersim.png", k));
    figure(2);

    %% Sample

    TOL = 0.5;
    ONCOLOR = [1,1,1];
    OFFCOLOR = [0,0,0];

    tt = 0 : RPU : 2*pi - RPU;
    rr = -RLIM : RLIM;
    zz = 0 : HEIGHT - 1;

    cylXYZ = zeros(length(tt)*length(rr)*length(zz), 3);
    cylCol = zeros(length(tt)*length(rr)*length(zz), 3);

    i = 1;
    sliceidx = 1;


    for t = tt
        fwrite(file, NEXT_SLICE, 'uint8');
        sliceenpoints = [];
        for r = rr
            for z = zz
                cylXYZ(i, :) = [r*cos(t), r*sin(t), z];
                points = cloud.findPointsInROI(tolxyz(TOL, cylXYZ(i, :)));
                if(isempty(points))
                    cylCol(i,:) = OFFCOLOR;
                else
                    cylCol(i,:) = ONCOLOR;
    %                 cylCol(i,:) = mean(rawCol(points, :));
                    bytecol = uint8(cylCol(i,:) * 255);
                    fwrite(file, uint8(HEIGHT - z - 1), 'uint8');
                    fwrite(file, uint8(r + 23.5), 'uint8');
                    fwrite(file, uint8(bytecol), 'uint8');
                    sliceenpoints = [sliceenpoints;[HEIGHT - z - 1, r + 23.5, bytecol]];
                end
                i = i + 1;
            end
        end
        prevenpoints{sliceidx} = sliceenpoints;
        sliceidx = sliceidx + 1;
        waitbar(t/max(tt), wait, sprintf('Current Angle: %.04f',t));
    end
    
    %% Visualize Sampled Cloud

    figure(2);
    pcshow(pointCloud(cylXYZ, 'Color', cylCol), 'MarkerSize', 50);
    set(gcf,'color','k'); set(gcf, 'InvertHardCopy', 'off');
    saveas(gcf, sprintf("out/%05d-cylinder.png", k));


    % pcshow(pointCloud(cloud.Location(points,:)));
end

close(wait);
close(framewait);
fclose(file);

%% Create video

% system("bash -c (ffmpeg -f image2 -r 15 -i out/%05d-cylinder.png -vcodec mpeg4 -y cylinder.mp4)")

%% Utility Functions

function tolv = tolxyz (tol, xyz)
    tolv = [xyz(1)-tol, xyz(1)+tol,...
            xyz(2)-tol, xyz(2)+tol,...
            xyz(3)-tol, xyz(3)+tol];
end

function htm = htmgen (x, y, z, trans)
    rotm = [1,0,0;0,cosd(x),-sind(x);0,sind(x),cosd(x)] * ...
           [cosd(y),0,sind(y);0,1,0;-sind(y),0,cosd(y)] * ...
           [cosd(z),-sind(z),0;sind(z),cosd(z),0;0,0,1] ;
    htm = [rotm,trans';0,0,0,1];
end

function pc_out = applyTransformation (pc_in, T)
    origin = mean(pc_in, 1);
    pc_out = (pc_in - origin)*T' + origin;
end
