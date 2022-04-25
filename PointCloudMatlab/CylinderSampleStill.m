%% Load and Normalize Point Cloud

clear; clc;

HEIGHT = 30;
WIDTH = 48;
RLIM = WIDTH/2 - 0.5;
UPR = 360;
DPU = 360/UPR;
RPU = deg2rad(DPU);
FRAMERATE = 15000;

NEXT_FRAME = uint8(0xFF);
NEXT_SLICE = uint8(0xFE);

filename = 'tree_blender_file';
% file = "Poisson Disk Samples";
rawcloud = pcread(['plys/', filename, '.ply']);

% load('xyzPoints');
% rawcloud = pointCloud(xyzPoints);

rawXYZ = rawcloud.Location;
T = [1,0,0;0,cosd(90),-sind(90);0,sind(90),cosd(90)];
% rawXYZ = rawXYZ * T';
rawXYZ(:,[1,2]) = rawXYZ(:,[1,2]) - [mean(rawcloud.XLimits), mean(rawcloud.YLimits)];
rawXYZ(:,3) = rawXYZ(:,3) - rawcloud.ZLimits(1);
diffs = [norm(max(rawXYZ(:,[1,2])) - min(rawXYZ(:,[1,2]))), max(rawXYZ(:,3))];
rawXYZ = rawXYZ * min([WIDTH, HEIGHT] ./ diffs);
rawCol = single(rawcloud.Color) / 255;

cloud = pointCloud(rawXYZ, 'Color', rawCol, 'Intensity', rawcloud.Intensity);

%% Visualize cloud

figure(1);
pcshow(cloud);

%% Sample

TOL = 0.5;
ONCOLOR = [0.8,0.95,1];
OFFCOLOR = [0,0,0];

tt = 0 : RPU : 2*pi - RPU;
rr = -RLIM : RLIM;
zz = 0 : HEIGHT - 1;

cylXYZ = zeros(length(tt)*length(rr)*length(zz), 3);
cylCol = zeros(length(tt)*length(rr)*length(zz), 3);

i = 1;

wait = waitbar(0, '', 'Name', 'Sweeping through angles');

file = fopen(['still_bins/', filename, '.vox'], 'w');
fwrite(file, uint16(UPR), 'uint16');
fwrite(file, uint16(FRAMERATE), 'uint16');

fwrite(file, NEXT_FRAME, 'uint8');

for t = tt
    fwrite(file, NEXT_SLICE, 'uint8');
    for r = rr
        for z = zz
            cylXYZ(i, :) = [r*cos(t), r*sin(t), z];
            points = cloud.findPointsInROI(tolxyz(TOL, cylXYZ(i, :)));
            if(isempty(points))
                cylCol(i,:) = OFFCOLOR;
            else
%                 cylCol(i,:) = ONCOLOR;
                cylCol(i,:) = mean(rawCol(points, :));
%                 bytecol = uint8(cylCol(i,:) * 255);
                fwrite(file, uint8(HEIGHT - z - 1), 'uint8');
                fwrite(file, uint8(r + 23.5), 'uint8');
                fwrite(file, uint8(bytecol), 'uint8');
            end
            i = i + 1;
        end
    end
%     clc; t
    waitbar(t/max(tt), wait, sprintf('Current Angle: %.04f',t));
end

fclose(file);

close(wait);

% pcshow(pointCloud(cloud.Location(points,:)));

%% Visualize sampled cloud

figure(2);
pcshow(pointCloud(cylXYZ, 'Color', cylCol), 'MarkerSize', 1);

%% Utility Functions

function tolv = tolxyz (tol, xyz)
    tolv = [xyz(1)-tol, xyz(1)+tol,...
            xyz(2)-tol, xyz(2)+tol,...
            xyz(3)-tol, xyz(3)+tol];
end
